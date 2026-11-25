import sys
from typing import Optional

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from pydantic import BaseModel

# Relative imports within the backend app package
from . import appointments as appointment_store
from .appointment_tools import (
    book_appointment as tool_book_appointment,
    cancel_appointment as tool_cancel_appointment,
)
from .appointments import appointments
from .doctors import doctors
from .voice_pipeline import run_voice_pipeline

# Configure clear backend logging for pipeline & service debugging
logger.remove()
logger.add(sys.stderr, level="INFO")

app = FastAPI(
    title="MediVoice AI",
    description="AI Voice Doctor Appointment Assistant API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class BookingRequest(BaseModel):
    patient_name: str
    phone_number: str
    doctor_id: int
    slot: str


@app.get("/")
def home():
    return {
        "message": "Welcome to MediVoice AI Backend",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/doctors")
def get_doctors():
    return doctors


@app.get("/doctors/{doctor_id}")
def get_doctor(doctor_id: int):
    for doctor in doctors:
        if doctor["id"] == doctor_id:
            return doctor
    raise HTTPException(status_code=404, detail="Doctor not found")


@app.get("/availability")
def get_availability(specialty: Optional[str] = None):
    result = []
    for doctor in doctors:
        if specialty and doctor["specialty"].lower() != specialty.lower():
            continue
        result.append(
            {
                "doctor_id": doctor["id"],
                "doctor_name": doctor["name"],
                "specialty": doctor["specialty"],
                "available_slots": doctor["available_slots"],
            }
        )
    return result


@app.get("/appointments")
def get_appointments():
    return appointments


@app.post("/book")
def book_appointment(request: BookingRequest):
    result = tool_book_appointment(
        patient_name=request.patient_name,
        phone_number=request.phone_number,
        doctor_id=request.doctor_id,
        slot=request.slot,
    )
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return {
        "message": result["message"],
        "appointment": result["appointment"],
    }


@app.delete("/cancel/{appointment_id}")
def cancel_appointment(appointment_id: int, phone_number: str):
    result = tool_cancel_appointment(
        phone_number=phone_number,
        appointment_id=appointment_id,
    )
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return {
        "message": result["message"],
        "cancelled_appointment": result["cancelled_appointment"],
    }


@app.websocket("/ws/voice")
async def voice_call(websocket: WebSocket):
    await websocket.accept()
    logger.info("========== VOICE CLIENT CONNECTED ===========")
    try:
        await run_voice_pipeline(websocket)
    except WebSocketDisconnect:
        logger.info("Voice client WebSocket disconnected.")
    except Exception as exc:
        logger.exception(f"Voice pipeline error: {exc}")
    finally:
        logger.info("Voice client session ended.")
