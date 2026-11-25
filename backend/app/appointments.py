
import json
from pathlib import Path

# Persistent storage file
DATA_FILE = Path(__file__).resolve().parent / "appointments_data.json"


def load_appointments():
    """Load appointments and ID counter from JSON storage."""
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)

            return data.get("appointments", []), data.get("next_appointment_id", 1)

        except (json.JSONDecodeError, OSError):
            pass

    return [], 1


def save_appointments():
    """Save appointments and ID counter to JSON storage."""
    data = {
        "appointments": appointments,
        "next_appointment_id": next_appointment_id
    }

    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


# Load saved data when backend starts
appointments, next_appointment_id = load_appointments()
