"""
MediVoice AI - Pipecat Voice Pipeline
Connects WebSocket transport (with Protobuf + Silero VAD + RTVI),
ElevenLabs STT, Gemini LLM with tool calling, and ElevenLabs TTS.
"""

from loguru import logger
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.frames.frames import TTSSpeakFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.frameworks.rtvi import (
    RTVIObserver,
    RTVIObserverParams,
    RTVIProcessor,
)
from pipecat.serializers.protobuf import ProtobufFrameSerializer
from pipecat.services.elevenlabs.stt import ElevenLabsRealtimeSTTService
from pipecat.services.elevenlabs.tts import ElevenLabsTTSService
from pipecat.transports.websocket.fastapi import (
    FastAPIWebsocketParams,
    FastAPIWebsocketTransport,
)

from app.config import ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID
from app.gemini_bridge import GeminiBridge

INITIAL_GREETING = (
    "Hello! Welcome to MediVoice AI. I can help you check doctor availability, "
    "book an appointment, or cancel an existing appointment. How can I help you today?"
)


async def run_voice_pipeline(websocket):
    """Run a single real-time Pipecat voice session over a FastAPI WebSocket."""
    transport = FastAPIWebsocketTransport(
        websocket,
        params=FastAPIWebsocketParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            audio_in_sample_rate=16000,
            audio_out_sample_rate=24000,
            audio_in_channels=1,
            audio_out_channels=1,
            vad_analyzer=SileroVADAnalyzer(),
            serializer=ProtobufFrameSerializer(),
        ),
    )

    rtvi = RTVIProcessor(transport=transport)

    stt = ElevenLabsRealtimeSTTService(
        api_key=ELEVENLABS_API_KEY,
        sample_rate=16000,
    )

    tts = ElevenLabsTTSService(
        api_key=ELEVENLABS_API_KEY,
        voice_id=ELEVENLABS_VOICE_ID,
        sample_rate=24000,
    )

    gemini = GeminiBridge()

    pipeline = Pipeline(
        [
            transport.input(),
            rtvi,
            stt,
            gemini,
            tts,
            transport.output(),
        ]
    )

    task = PipelineTask(
        pipeline,
        params=PipelineParams(
            audio_in_sample_rate=16000,
            audio_out_sample_rate=24000,
            allow_interruptions=True,
        ),
        observers=[
            RTVIObserver(
                rtvi,
                params=RTVIObserverParams(
                    user_audio_level_enabled=True,
                    bot_audio_level_enabled=True,
                ),
            )
        ],
    )

    @rtvi.event_handler("on_client_ready")
    async def on_client_ready(rtvi_proc):
        logger.info("RTVI client ready -> sending bot-ready and initial greeting")
        await rtvi_proc.set_bot_ready()
        gemini.add_assistant_message(INITIAL_GREETING)
        await task.queue_frames([TTSSpeakFrame(INITIAL_GREETING)])

    @transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(_transport, _websocket):
        logger.info("WebSocket client disconnected -> cancelling pipeline task")
        await task.cancel()

    runner = PipelineRunner(handle_sigint=False)
    await runner.run(task)
