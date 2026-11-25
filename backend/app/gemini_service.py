import asyncio
from google import genai
from google.genai import types
from loguru import logger

from app.config import GEMINI_API_KEY
from app.appointment_tools import (
    check_doctor_availability,
    book_appointment,
    cancel_appointment,
)

client = genai.Client(api_key=GEMINI_API_KEY)


SYSTEM_PROMPT = """
You are MediVoice AI, a calm, gentle, patient and professional healthcare appointment assistant.

PERSONALITY AND SPEAKING STYLE:
- Speak in a soft, warm, reassuring and natural conversational tone.
- Sound like a patient receptionist, never like a robotic system.
- Keep every spoken response short, preferably one sentence.
- Ask only ONE question at a time.
- Never rush the caller.
- After asking a question, allow the caller time to answer.
- Do not interrupt, pressure, dominate, or overwhelm the caller.
- Avoid repeating the same sentence, question, or information.
- If the caller pauses or is silent, wait patiently. Do not keep talking or repeat your question.
- If you did not understand, politely ask them to repeat only the part you missed.
- Acknowledge answers naturally with brief phrases like "Of course", "Certainly", "Take your time", or "Alright".

CONVERSATION RULES:
- Remember all information the caller has already provided in this conversation.
- Never ask for information that the caller has already provided and that you understood correctly.
- Do not restart the conversation or repeat the greeting during an ongoing call.
- Do not ask multiple questions in one sentence.
- Do not list all details repeatedly after every caller response.
- If the caller gives multiple pieces of information together, use all of them.
- If the caller corrects information, use the corrected information.

APPOINTMENT AVAILABILITY:
- Always call check_doctor_availability before suggesting or confirming any available appointment slot.
- Use the tool results as the ONLY source of truth for doctors, dates and available slots.
- Never invent, modify, convert, or assume a slot.
- When a slot is returned by the availability tool, preserve its exact slot string when passing it to book_appointment.
- Do not check availability repeatedly if you already have the relevant results and the caller has not changed the doctor or date.
- If the caller asks for a particular doctor, use that doctor. Do not unnecessarily ask for their specialty.
- Offer only the relevant available slots. Present them briefly and naturally.

BOOKING PROCESS:
Collect the following information, one item at a time only when missing:
1. Doctor and date.
2. Caller-selected available time.
3. Patient's full name.
4. 10-digit phone number.

Do not ask for all missing details in a single question.
Do not ask the patient to repeat information already understood.
Do not book until all required information is collected.

Before booking:
- Read the phone number back digit by digit.
- Ask the caller to confirm the phone number.
- Also confirm the selected doctor, date and time clearly.
- Wait until the caller explicitly confirms the details.
- Only then call book_appointment.
- Pass the exact available slot string from the availability tool. Never make up or reformat the slot, date or year.
- Never claim a booking succeeded unless the booking tool returns success=true.
- If booking fails, calmly explain the actual reason and check the returned availability before suggesting alternatives.


POST-BOOKING VOICE SUMMARY AND REMINDER:
- After book_appointment returns success=true, verbally summarize the confirmed appointment.
- Mention the doctor's full name, specialty, appointment date, and exact time.
- Use the actual details returned by the booking tool. Do not invent or alter them.
- Give a short reminder to arrive 10-15 minutes early.
- Keep the summary warm, natural, and concise.
- Do not repeat the summary if it has already been spoken.
- If booking fails, never give a successful booking summary or reminder.
- Example: "Your appointment is confirmed with Dr. Ananya Rao,
  specializing in Dermatology, on November 26th at 10 AM.
  Please arrive 10 to 15 minutes early. We look forward to seeing you!"


CANCELLATION PROCESS:
- Collect the caller's 10-digit phone number if not already provided.
- Read it back digit by digit and obtain explicit confirmation.
- If multiple appointments exist, clarify which appointment they wish to cancel.
- Only call cancel_appointment after the required confirmation.
- Never claim cancellation succeeded unless the tool returns success=true.

PATIENT SAFETY:
- You are an appointment assistant, not a doctor.
- Never diagnose, recommend treatment, or prescribe medication.
- For an emergency or potentially life-threatening situation, advise the caller to seek immediate emergency medical assistance.

IMPORTANT:
- Be patient and let the caller lead the pace.
- Use a gentle, non-repetitive, human-like conversational style.
- Do not speak unnecessarily while the caller is thinking.
- Never book or cancel without explicit confirmation.
- Never make up appointment availability or booking results.
"""


appointment_functions = [
    types.FunctionDeclaration(
        name="check_doctor_availability",
        description="Returns available doctors and their slots, optionally filtered by doctor name, specialty, or date.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "doctor_name": types.Schema(
                    type=types.Type.STRING,
                    description="Optional doctor name such as Dr. Ananya Rao or Rao.",
                ),
                "specialty": types.Schema(
                    type=types.Type.STRING,
                    description="Optional medical specialty such as Cardiology, Dermatology, General Medicine, or Orthopedics.",
                ),
                "date": types.Schema(
                    type=types.Type.STRING,
                    description="Optional date filter such as Nov 26, Nov 27, or tomorrow.",
                ),
            },
        ),
    ),
    types.FunctionDeclaration(
        name="book_appointment",
        description="Books a selected slot for the caller using the confirmed spoken phone number.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "patient_name": types.Schema(
                    type=types.Type.STRING,
                    description="Caller's full name.",
                ),
                "phone_number": types.Schema(
                    type=types.Type.STRING,
                    description="Confirmed 10-digit phone number spoken by the caller.",
                ),
                "doctor_id": types.Schema(
                    type=types.Type.INTEGER,
                    description="ID of the selected doctor from check_doctor_availability.",
                ),
                "doctor_name": types.Schema(
                    type=types.Type.STRING,
                    description="Optional doctor name if doctor_id is unavailable.",
                ),
                "slot": types.Schema(
                    type=types.Type.STRING,
                    description="Exact available slot string from check_doctor_availability.",
                ),
            },
            required=["patient_name", "phone_number", "slot"],
        ),
    ),
    types.FunctionDeclaration(
        name="cancel_appointment",
        description="Cancels the caller's existing appointment found using their confirmed spoken phone number.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "phone_number": types.Schema(
                    type=types.Type.STRING,
                    description="Confirmed 10-digit phone number spoken by the caller.",
                ),
                "appointment_id": types.Schema(
                    type=types.Type.INTEGER,
                    description="Optional appointment ID only needed if the caller has multiple appointments.",
                ),
            },
            required=["phone_number"],
        ),
    ),
]

gemini_tools = [types.Tool(function_declarations=appointment_functions)]

TOOL_FUNCTIONS = {
    "check_doctor_availability": check_doctor_availability,
    "book_appointment": book_appointment,
    "cancel_appointment": cancel_appointment,
}

async def _generate_response_sync(
    user_message: str,
    conversation_history=None,
    booking_completed=False
):
    """Run Gemini turn asynchronously with tool-calling loop and return (text, events)."""
    if conversation_history is None:
        conversation_history = []

    contents = []
    for item in conversation_history:
        role = "model" if item.get("role") == "assistant" else "user"
        text = item.get("content", "")
        if text:
            contents.append(
                types.Content(
                    role=role,
                    parts=[types.Part.from_text(text=text)],
                )
            )

    contents.append(
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=user_message)],
        )
    )

    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        tools=gemini_tools,
        temperature=0.4,
    )

    events = []
    response = await client.aio.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=contents,
        config=config,
    )

    tool_call_count = 0
    booking_successful_this_turn = booking_completed

    while response.function_calls and tool_call_count < 3:
        tool_call_count += 1
        function_responses = []
        for function_call in response.function_calls:
            function_name = function_call.name
            arguments = dict(function_call.args or {})
            logger.info(f"Executing tool {function_name} with args={arguments}")

            if function_name == "book_appointment" and booking_successful_this_turn:
                result = {
                    "success": False,
                    "message": "A booking has already been completed during this call. Do not book another appointment."
    }

            elif function_name in TOOL_FUNCTIONS:
                result = TOOL_FUNCTIONS[function_name](**arguments)

            else:
                result = {"success": False, "message": "Unknown function"}

            if (
                function_name == "book_appointment"
                and isinstance(result, dict)
                and result.get("success")
                ):
                booking_successful_this_turn = True

            logger.info(f"Tool {function_name} result: {result}")

            if function_name == "book_appointment" and isinstance(result, dict) and result.get("success"):
                events.append({"type": "appointment_booked", "appointment": result.get("appointment")})
            elif function_name == "cancel_appointment" and isinstance(result, dict) and result.get("success"):
                events.append({"type": "appointment_cancelled", "appointment": result.get("cancelled_appointment")})

            function_responses.append(
                types.Part.from_function_response(
                    name=function_name,
                    response={"result": result},
                )
            )

        contents.append(response.candidates[0].content)
        contents.append(
            types.Content(
                role="user",
                parts=function_responses,
            )
        )
        response = await client.aio.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=contents,
            config=config,
        )

    # Extract final reply text
    reply_text = ""
    if response.candidates:
        for part in response.candidates[0].content.parts:
            if isinstance(part, types.Part) and getattr(part, "text", None):
                reply_text = part.text
                break
        else:
            reply_text = getattr(response.candidates[0].content, "text", "") or ""
    return reply_text, events

async def generate_response_with_events(
    user_message: str,
    conversation_history=None,
    booking_completed=False
):
    """Non-blocking wrapper that returns the Gemini reply and any tool events."""
    return await _generate_response_sync(
        user_message,
        conversation_history,
        booking_completed
    )

async def generate_response(user_message: str, conversation_history=None):
    """Convenient helper returning only the reply text."""
    reply_text, _ = await generate_response_with_events(user_message, conversation_history)
    return reply_text
