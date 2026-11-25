# MediVoice AI 🎙️

An **AI-powered voice receptionist for medical clinics** that enables patients to interact naturally with a virtual receptionist to check doctor availability, book appointments, and cancel appointments.

> **Project status:** Prototype/demo using mock doctor and appointment data. It is not connected to a real clinic scheduling system.

---

## ✨ Features

- **Voice conversations:** Patients interact with the receptionist by speaking.
- **Doctor availability:** Checks mock doctor schedules and available time slots.
- **Appointment booking:** Collects patient name and phone number, verifies the details, and books an available slot.
- **Voice booking confirmation:** Summarizes the doctor's name, specialty, appointment date, and time after a successful booking.
- **Arrival reminder:** Advises patients to arrive **10–15 minutes early**.
- **Appointment cancellation:** Cancels appointments using the patient's phone number and, when needed, the appointment ID.
- **Confirmation safeguards:** Reads back the phone number and booking details and requires explicit confirmation before booking or cancelling.
- **Local appointment persistence:** Stores appointment records in a JSON file so bookings survive backend restarts.
- **Web dashboard:** Displays the call interface, transcripts, doctor availability, and appointment information.

---

## 🧠 How It Works

MediVoice AI follows a voice-processing and AI interaction flow:

1. The patient speaks through the browser.
2. **Speech-to-Text (STT)** converts speech into text.
3. **Google Gemini** interprets the request, manages the conversation, and selects an appointment tool when needed.
4. Backend tools check doctor availability, book appointments, or cancel appointments.
5. **Text-to-Speech (TTS)** generates the receptionist's spoken response.
6. The frontend dashboard displays call status and relevant information.

---

## 🧰 Technology Stack

| Component | Technology |
|---|---|
| Frontend | React, Vite, JavaScript, CSS |
| Backend/API | Python, FastAPI, Uvicorn |
| Voice pipeline | Pipecat, browser voice client, WebSocket transport |
| Conversational AI | Google Gemini (Google GenAI SDK) |
| Text-to-Speech | ElevenLabs |
| Appointment storage | Local JSON file |
| Configuration | `python-dotenv`, environment variables |

---

## 📁 Project Structure

```text
MediVoiceAI/
├── backend/
│   ├── app/
│   │   ├── appointment_tools.py       # Availability, booking, cancellation logic
│   │   ├── appointments.py            # Appointment persistence
│   │   ├── config.py                 # Environment configuration
│   │   ├── doctors.py                 # Mock doctor data and schedules
│   │   ├── gemini_bridge.py           # Voice/AI bridge
│   │   ├── gemini_service.py          # Gemini instructions and tool handling
│   │   ├── main.py                    # FastAPI entry point
│   │   ├── voice_assistant.py          # Voice assistant setup
│   │   └── voice_pipeline.py            # Voice pipeline components
│   ├── .env.example                    # Environment variable template
│   └── requirements.txt                 # Backend dependencies
├── frontend/
│   ├── src/
│   │   ├── App.jsx                     # Main dashboard
│   │   ├── App.css                     # Dashboard styling
│   │   ├── api.js                      # Backend API communication
│   │   └── ...
│   ├── public/
│   ├── package.json
│   └── vite.config.js
├── .gitignore
└── README.md
```

> `backend/app/appointments_data.json` is created locally when appointments are saved. It is ignored by Git to avoid committing private appointment data. Local environment files and virtual environments are also excluded.

---

## ⚙️ Prerequisites

Install the following:

- Python **3.10**
- Node.js and npm
- Git
- API credentials for **Google Gemini** and **ElevenLabs**

Verify installations:

```powershell
python --version
node --version
npm --version
git --version
```

---

## 🔑 Environment Configuration

### 1. Set up the backend `.env`

From the project root, navigate to the backend directory:

```powershell
cd backend
```

Create your local `.env` file from the template:

```powershell
Copy-Item .env.example .env
```

Open `backend/.env` and add your API credentials:

```env
GEMINI_API_KEY=your_gemini_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
ELEVENLABS_VOICE_ID=your_elevenlabs_voice_id
```

> **Security:** Never commit your real `.env` file or publish API keys.

---

## 🚀 Installation & Running

Run the backend and frontend in **two separate terminals**.

### Terminal 1 — Backend (FastAPI)

From the project root:

```powershell
cd backend
```

Create a virtual environment:

```powershell
python -m venv venv
```

Activate it (Windows PowerShell):

```powershell
.\venv\Scripts\Activate.ps1
```

Install Python dependencies:

```powershell
pip install -r requirements.txt
```

Create/configure the `.env` file as described above, then start the server:

```powershell
python -m uvicorn app.main:app --reload
```

Backend endpoints:

- API: `http://127.0.0.1:8000`
- Interactive API documentation: `http://127.0.0.1:8000/docs`

### Terminal 2 — Frontend (React + Vite)

Open another terminal at the project root:

```powershell
cd frontend
```

Install frontend dependencies:

```powershell
npm install
```

Start the frontend development server:

```powershell
npm run dev
```

Vite will print a local URL (typically `http://localhost:5173`). Open the printed URL in your browser.

---

## 🗣️ How to Use

1. Open the frontend in your browser.
2. Start a voice call/session using the dashboard.
3. Ask the receptionist about doctor availability.
4. Request an appointment and provide the requested information.
5. Listen while the assistant reads back your phone number and appointment details.
6. Confirm the booking when asked.
7. After booking succeeds, listen for the spoken appointment summary and arrival reminder.
8. To cancel, ask the receptionist to cancel your appointment, provide the requested details, and confirm when prompted.

### Example Voice Requests

- “Which doctors are available tomorrow?”
- “I would like to book an appointment with a dermatologist.”
- “Can I book Dr. [doctor name] at [time]?”
- “I need to cancel my appointment.”

---

## 💾 Appointment Data & Persistence

Appointment records are stored locally in:

```text
backend/app/appointments_data.json
```

- Booking records are saved to this JSON file.
- Appointment IDs are available for identifying appointments.
- Cancellation removes the relevant record and saves the updated data.
- The file is local and is not a production database.

### Prototype limitation

Appointment records persist across backend restarts. Doctor availability, however, is mock/in-memory data and may reset when the backend restarts. This means the prototype is not a production-ready scheduling system.

---

## 🔐 Safety, Privacy & Limitations

- This is a prototype that uses mock doctors and schedules.
- It is for administrative appointment tasks only; it does not diagnose conditions, prescribe medication, or provide treatment advice.
- For emergencies, seek immediate medical care or contact local emergency services. MediVoice AI is not an emergency-response service.
- Appointment records are stored locally in JSON and are not encrypted by this prototype.
- Avoid using real patient data during public demos or testing.
- Keep API credentials in the local `.env` file. Never commit secrets.
- **Automated SMS, email, or WhatsApp reminders are not implemented.** The current reminder is spoken after a successful booking and advises the patient to arrive 10–15 minutes early.

---

## 🛠️ Troubleshooting

| Issue | Suggested fix |
|---|---|
| Backend fails to start | Check Python version, activate the virtual environment, install `requirements.txt`, and verify `.env` values. |
| Frontend fails to start | Run `npm install` in `frontend`, then `npm run dev`. |
| Voice interaction fails | Check internet connectivity, Gemini/ElevenLabs API credentials, and backend terminal logs. |
| Appointment data does not save | Confirm write access to `backend/app/appointments_data.json` and check whether the JSON file is malformed. |

---

## 🔮 Future Enhancements

- Replace mock schedules with a real clinic scheduling database.
- Persist doctor availability and booking slots in a database.
- Implement automated scheduled SMS/email appointment reminders.
- Add authentication and role-based access control.
- Support additional languages.
- Add audit logs and stronger privacy/security protections.
- Deploy the frontend and backend to cloud infrastructure.

---

## 👩‍💻 Author

**MediVoice AI** — Voice-based AI receptionist prototype.


