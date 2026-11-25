from loguru import logger
import time

from pipecat.frames.frames import (
    Frame,
    InterimTranscriptionFrame,
    LLMFullResponseEndFrame,
    LLMFullResponseStartFrame,
    LLMTextFrame,
    TranscriptionFrame,
)
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor
from pipecat.processors.frameworks.rtvi import RTVIServerMessageFrame

from app.gemini_service import generate_response_with_events


class GeminiBridge(FrameProcessor):
    """Connects recognized speech to Gemini and forwards LLM text & tool events downstream."""

    def __init__(self):
        super().__init__()
        self.conversation_history = []
        self.last_user_text = ""
        self.last_user_time = 0.0
        self.booking_completed = False

    def add_assistant_message(self, content: str):
        """Record an assistant message (e.g., initial greeting) into history."""
        if content:
            self.conversation_history.append(
                {"role": "assistant", "content": content}
            )

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        await super().process_frame(frame, direction)

        # Always forward incoming frames downstream
        await self.push_frame(frame, direction)

        # Handle committed user speech transcriptions
        if isinstance(frame, TranscriptionFrame) and not isinstance(
            frame, InterimTranscriptionFrame
        ):
            user_text = (frame.text or "").strip()

            if not user_text:
                return

            # Prevent the same speech transcription from triggering Gemini repeatedly
            normalized_text = " ".join(user_text.lower().split())
            current_time = time.time()

            if (
                normalized_text == self.last_user_text
                and current_time - self.last_user_time < 4.0
            ):
                logger.warning(f"Ignoring duplicate transcription: {user_text}")
                return

            self.last_user_text = normalized_text
            self.last_user_time = current_time

            logger.info(f"Caller: {user_text}")

            try:
                reply_text, tool_events = await generate_response_with_events(
    user_text,
    self.conversation_history,
    booking_completed=self.booking_completed
)

            except Exception as e:
                logger.exception(f"Gemini response failed: {e}")
                reply_text = (
                    "I'm sorry, I had a temporary issue processing that. "
                    "Could you please repeat?"
                )
                tool_events = []

            # Send tool events to the frontend
            for event in tool_events:
                if event.get("type") == "appointment_booked":
                    self.booking_completed = True
                    await self.push_frame(RTVIServerMessageFrame(data=event))
                

            # Send Gemini's response to the voice pipeline
            if reply_text:
                logger.info(f"MediVoice AI: {reply_text}")

                self.conversation_history.append(
                    {"role": "user", "content": user_text}
                )
                self.conversation_history.append(
                    {"role": "assistant", "content": reply_text}
                )

                await self.push_frame(LLMFullResponseStartFrame())
                await self.push_frame(LLMTextFrame(text=reply_text))
                await self.push_frame(LLMFullResponseEndFrame())