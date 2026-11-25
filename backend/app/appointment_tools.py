import re

from app.doctors import doctors
from app.appointments import appointments
import app.appointments as appointment_store


def normalize_phone_number(phone_number: str) -> str:
    """Normalize a spoken phone number to 10 digits."""
    digits = re.sub(r"\D", "", str(phone_number or ""))

    if len(digits) > 10 and digits.startswith(("91", "1", "0")):
        digits = digits[-10:]

    return digits


def _find_doctor(doctor_id=None, doctor_name=None):
    """Find a doctor by ID or partial case-insensitive name."""

    if doctor_id is not None:
        try:
            doc_id = int(doctor_id)
            match = next(
                (d for d in doctors if d["id"] == doc_id),
                None
            )
            if match:
                return match
        except (TypeError, ValueError):
            pass

    if doctor_name:
        cleaned = re.sub(
            r"^\s*dr\.?\s*",
            "",
            doctor_name.strip(),
            flags=re.IGNORECASE
        ).lower()

        for doctor in doctors:
            doc_clean = re.sub(
                r"^\s*dr\.?\s*",
                "",
                doctor["name"],
                flags=re.IGNORECASE
            ).lower()

            if cleaned in doc_clean or doc_clean in cleaned:
                return doctor

    return None


def _extract_time(text):
    """Extract a time such as 11:30 AM or 3 PM from text."""
    text = str(text or "").strip().upper()

    match = re.search(
        r"\b(\d{1,2})(?::(\d{2}))?\s*(AM|PM)\b",
        text
    )

    if not match:
        return None

    hour = int(match.group(1))
    minute = int(match.group(2) or 0)
    period = match.group(3)

    return f"{hour}:{minute:02d} {period}"


def _match_available_slot(available_slots, requested_slot):
    """
    Match the requested appointment to the canonical available slot.

    First tries an exact match. If that fails, matches the time only
    when exactly one available slot has that time.
    """

    requested_slot = str(requested_slot or "").strip()

    if not requested_slot:
        return None

    # 1. Exact match
    exact_match = next(
        (
            slot for slot in available_slots
            if str(slot).strip().lower() == requested_slot.lower()
        ),
        None
    )

    if exact_match:
        return exact_match

    # 2. Extract the requested time
    requested_time = _extract_time(requested_slot)

    if not requested_time:
        return None

    # 3. Match against available slots using their time
    time_matches = []

    for available_slot in available_slots:
        available_time = _extract_time(available_slot)

        if available_time == requested_time:
            time_matches.append(available_slot)

    # Only accept time-based matching if it is unambiguous
    if len(time_matches) == 1:
        return time_matches[0]

    return None


def check_doctor_availability(
    doctor_name=None,
    specialty=None,
    date=None
):
    """Return doctors and their available slots."""

    results = []

    cleaned_doc = None

    if doctor_name:
        cleaned_doc = re.sub(
            r"^\s*dr\.?\s*",
            "",
            doctor_name.strip(),
            flags=re.IGNORECASE
        ).lower()

    date_filter = date.strip().lower() if date else None

    if date_filter == "tomorrow":
        date_filter = "nov 26"
    elif date_filter == "today":
        date_filter = "nov 25"

    for doctor in doctors:

        # Filter by specialty
        if specialty and specialty.strip().lower() not in doctor["specialty"].lower():
            continue

        # Filter by doctor name
        if cleaned_doc:
            doc_clean = re.sub(
                r"^\s*dr\.?\s*",
                "",
                doctor["name"],
                flags=re.IGNORECASE
            ).lower()

            if cleaned_doc not in doc_clean and doc_clean not in cleaned_doc:
                continue

        slots = doctor["available_slots"]

        # Filter by date if slot strings contain dates
        if date_filter:
            filtered_slots = [
                slot for slot in slots
                if date_filter in str(slot).lower()
            ]
        else:
            filtered_slots = list(slots)

        results.append(
            {
                "doctor_id": doctor["id"],
                "name": doctor["name"],
                "specialty": doctor["specialty"],
                "available_slots": filtered_slots,
            }
        )

    return results


def book_appointment(
    patient_name,
    phone_number,
    doctor_id=None,
    slot="",
    doctor_name=None
):
    """Book an appointment using the canonical available slot."""

    # Validate patient name
    if not patient_name or not str(patient_name).strip():
        return {
            "success": False,
            "message": "Patient name is required."
        }

    # Validate phone number
    normalized_phone = normalize_phone_number(phone_number)

    if len(normalized_phone) != 10:
        return {
            "success": False,
            "message": "A valid 10-digit phone number is required."
        }
        # Prevent duplicate active appointments by name OR phone number
    normalized_name = " ".join(str(patient_name).strip().lower().split())

    for existing in appointments:
        existing_name = " ".join(
            str(existing.get("patient_name", "")).strip().lower().split()
        )
        existing_phone = normalize_phone_number(
            existing.get("phone_number", "")
        )

        if existing_phone == normalized_phone:
            return {
                "success": False,
                "message": (
                    "This phone number already has an active appointment. "
                    "Please cancel the existing appointment before booking another."
                )
            }

        if existing_name == normalized_name:
            return {
                "success": False,
                "message": (
                    "This patient already has an active appointment. "
                    "Please cancel the existing appointment before booking another."
                )
            }

    # Find doctor
    doctor = _find_doctor(
        doctor_id=doctor_id,
        doctor_name=doctor_name
    )

    if not doctor:
        return {
            "success": False,
            "message": "Doctor not found."
        }

    requested_slot = str(slot or "").strip()

    # Match against actual available slots
    matched_slot = _match_available_slot(
        doctor["available_slots"],
        requested_slot
    )

    # Reject if no valid slot is found
    if not matched_slot:
        return {
            "success": False,
            "message": (
                f"Slot {requested_slot} is unavailable "
                f"for {doctor['name']}."
            ),
            "available_slots": doctor["available_slots"],
        }

    # Generate appointment ID
    appointment_id = appointment_store.next_appointment_id

    # Create appointment using canonical slot string
    appointment = {
        "id": appointment_id,
        "patient_name": str(patient_name).strip(),
        "phone_number": normalized_phone,
        "doctor_id": doctor["id"],
        "doctor_name": doctor["name"],
        "specialty": doctor["specialty"],
        "slot": matched_slot,
        "reminder": "Please arrive 10-15 minutes before your appointment.",
    }

    # Save appointment
    appointments.append(appointment)

    # Remove booked slot from availability
    doctor["available_slots"].remove(matched_slot)

    # Increment ID
    appointment_store.next_appointment_id += 1

    # Persist appointments to JSON
    appointment_store.save_appointments()

    return {
        "success": True,
        "message": (
            f"Appointment #{appointment_id} booked with "
            f"{doctor['name']} for {matched_slot}."
        ),
        "appointment": appointment,
    }


def cancel_appointment(phone_number, appointment_id=None):
    """Cancel an existing appointment using the caller's phone number."""

    normalized_phone = normalize_phone_number(phone_number)

    if len(normalized_phone) != 10:
        return {
            "success": False,
            "message": (
                "A valid 10-digit phone number is required "
                "to look up the appointment."
            )
        }

    # Find appointments belonging to this phone number
    matching = [
        appointment for appointment in appointments
        if appointment["phone_number"] == normalized_phone
    ]

    if not matching:
        return {
            "success": False,
            "message": (
                f"No active appointment found for phone number "
                f"{normalized_phone}."
            )
        }

    # Find appointment by ID when provided
    if appointment_id is not None:
        try:
            appt_id = int(appointment_id)
        except (TypeError, ValueError):
            return {
                "success": False,
                "message": "Invalid appointment ID."
            }

        target = next(
            (
                appointment for appointment in matching
                if appointment["id"] == appt_id
            ),
            None
        )

        if not target:
            return {
                "success": False,
                "message": (
                    "No matching appointment found for "
                    "that ID and phone number."
                )
            }

    elif len(matching) > 1:
        return {
            "success": False,
            "message": (
                "Multiple appointments found for this phone number. "
                "Please specify which one to cancel."
            ),
            "appointments": matching,
        }

    else:
        target = matching[0]

    # Restore cancelled slot to doctor availability
    doctor = next(
        (
            doctor for doctor in doctors
            if doctor["id"] == target["doctor_id"]
        ),
        None
    )

    if doctor and target["slot"] not in doctor["available_slots"]:
        doctor["available_slots"].append(target["slot"])

    # Remove appointment
    appointments.remove(target)

    # Persist updated appointments to JSON
    appointment_store.save_appointments()

    return {
        "success": True,
        "message": (
            f"Cancelled appointment with {target['doctor_name']} "
            f"at {target['slot']}."
        ),
        "cancelled_appointment": target,
    }