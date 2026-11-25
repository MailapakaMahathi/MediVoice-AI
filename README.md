MediVoice AI 🎙️
MediVoice AI is an AI-powered voice receptionist designed for a medical clinic. It lets patients speak naturally to a virtual receptionist to check doctor availability, book appointments, and cancel appointments. The assistant uses speech recognition, an LLM for conversation and tool selection, and text-to-speech to respond conversationally.
Project status: Demonstration/prototype using mock doctor and appointment data. It is not connected to a real clinic scheduling system.

✨ Features
- Voice-based conversations — patients interact with the receptionist by speaking.
- Doctor availability — checks mock doctor schedules and available slots.
- Appointment booking — collects patient name and phone number, confirms the details, and books an available slot.
- Booking confirmation — verbally summarizes the confirmed doctor's name, specialty, appointment date, and time.
- Arrival reminder — tells patients to arrive 10–15 minutes before the appointment.
- Appointment cancellation — supports cancellation using patient phone number and, when needed, appointment ID.
- Confirmation safeguards — reads back the phone number and appointment details and requires explicit confirmation before booking or cancellation.
- Appointment persistence — saves appointment records to a local JSON file so bookings survive application restarts.
- Web dashboard — provides the interface for starting/ending calls and viewing transcripts, doctor availability, and appointment information.
🧠 How It Works
MediVoice AI uses a pipeline of voice and AI components:
1. Patient speaks through the browser.
2. Speech-to-text (STT) converts the patient's speech into text.
3. Gemini understands the request, conducts the conversation, and decides when to use appointment tools.
4. Backend tools check doctor availability, book appointments, or cancel appointments.
5. Text-to-speech (TTS) generates the receptionist's spoken reply.
6. Frontend dashboard displays call state and related information.
Technology Stack
Area	Technologies
Frontend	React, Vite, JavaScript, CSS
Backend/API	Python, FastAPI, Uvicorn
Voice interaction	Pipecat, browser voice client / WebSocket transport
AI conversation	Google Gemini (Google GenAI SDK)
Speech generation	ElevenLabs
Data	Local JSON file for saved appointment records
Configuration	Environment variables via python-dotenv


🗂️ Project Structure
MediVoiceAI/
├── backend/
│   ├── app/
│   │   ├── appointment_tools.py      # Availability, booking, cancellation tools
│   │   ├── appointments.py           # Appointment data loading/saving
│   │   ├── appointments_data.json    # Created at runtime; ignored by Git
│   │   ├── config.py                 # Loads configuration from .env
│   │   ├── doctors.py                 # Mock doctor data and schedules
│   │   ├── gemini_bridge.py           # Bridge between voice pipeline and AI logic
│   │   ├── gemini_service.py           # Gemini instructions and tool orchestration
│   │   ├── main.py                    # FastAPI application entry point
│   │   ├── voice_assistant.py          # Voice assistant setup
│   │   └── voice_pipeline.py           # Voice pipeline components
│   │   ├── .env.example                # Example environment configuration
│   │   └── requirements.txt             # Backend dependencies (if present)
│   └── ...
├── frontend/
│   ├── src/
│   │   ├── App.jsx                     # Main dashboard UI
│   │   ├── App.css                     # Dashboard styles
│   │   ├── api.js                      # Backend communication
│   │   └── ...
│   ├── public/
│   ├── package.json
│   └── vite.config.js
├── .gitignore
└── README.md
Some files such as appointments_data.json, virtual environments, and .env files are generated locally and intentionally excluded from version control.

⚙️ Prerequisites
Install these before running the project:
- Python 3.10 (recommended to match the development environment)
- Node.js and npm
- Git
- API credentials for:
  - Google Gemini
  - ElevenLabs
Check installations:
python --version
node --version
npm --version
git --version
🔑 Environment Setup
1. Backend environment file
Open a terminal at the project root and go to the backend:
cd backend
Create your local environment file by copying the example:
Copy-Item .env.example .env
Open backend/.env and replace the placeholders with your own credentials:
GEMINI_API_KEY=your_gemini_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
ELEVENLABS_VOICE_ID=your_elevenlabs_voice_id
Keep .env private. Never commit or share real API keys.
🚀 Run the Project Locally
You need two terminals: one for the backend and one for the frontend.
Terminal 1 — Backend
From the project root:
cd backend
Create and activate a Python virtual environment (Windows PowerShell):
python -m venv venv
.\venv\Scripts\Activate.ps1
Install dependencies:
pip install -r requirements.txt
Create the .env file if you haven't already (see Environment Setup).

Start the FastAPI server:
python -m uvicorn app.main:app --reload
The backend typically runs at:
- API base: http://127.0.0.1:8000
- FastAPI Swagger docs: http://127.0.0.1:8000/docs
Terminal 2 — Frontend
From the project root, open a second terminal:
cd frontend
Install frontend packages (first run, or after dependency changes):
npm install
Start the development server:
npm run dev
Vite prints the local frontend URL in the terminal (often http://localhost:5173). Open that URL in your browser.
🗣️ Using MediVoice AI
1. Open the frontend URL in your browser.
2. Start a voice call/session from the dashboard.
3. Ask the receptionist about doctor availability.
4. Request an appointment and provide the requested details.
5. Listen as the assistant reads back the phone number and booking details for confirmation.
6. Clearly confirm when asked.
7. After a successful booking, listen for the appointment summary and arrival reminder.
8. To cancel, ask to cancel an appointment and provide the requested phone number/details; confirm the cancellation when prompted.
Example requests
- “Which doctors are available tomorrow?”
- “I want to book an appointment with a dermatologist.”
- “Can I book Dr. [name] at [time]?”
- “I need to cancel my appointment.”
💾 Appointment Data & Persistence
Appointment records are saved locally in:
backend/app/appointments_data.json
This file is generated by the application and is excluded from Git because it may contain personal information.
- Bookings are saved to the JSON file.
- The appointment ID is used to identify records where necessary.
- Cancellation removes the appointment record and saves the updated data.
- The file is local to the running application and is not a database-backed production system.
Important prototype limitation: Doctor availability is mock/in-memory data. Availability may reset when the backend restarts, while saved appointment records persist. This prototype does not provide a production-grade transactional scheduling database.
🔐 Safety, Privacy & Limitations
- This project is a prototype and uses mock doctor/schedule data.
- It does not provide medical diagnosis, treatment, or prescriptions.
- The AI receptionist is intended for administrative tasks only.
- In an emergency, users should contact local emergency services or seek immediate medical care; the assistant is not an emergency-response service.
- Appointment data is stored locally in JSON and is not encrypted by this prototype.
- Do not use real patient information in public demos.
- API keys belong in the local .env file and should never be committed.
- Automated SMS, email, or WhatsApp appointment reminders are not implemented. The current reminder is spoken during the booking confirmation and advises arriving 10–15 minutes early.
🛠️ Troubleshooting
Backend doesn't start
- Verify Python is installed and the virtual environment is activated.
- Confirm you are in the backend directory.
- Install dependencies with pip install -r requirements.txt.
- Check .env exists and API keys are valid.
Frontend doesn't start
- Verify Node.js/npm are installed.
- Run npm install inside frontend.
- Run npm run dev and use the URL shown by Vite.
Voice session or AI response fails
- Check your internet connection.
- Verify Gemini and ElevenLabs credentials in backend/.env.
- Review backend terminal logs for errors.
- Confirm the required packages are installed.
Appointment information doesn't persist
- Check that the backend has permission to write to backend/app/appointments_data.json.
- Confirm the JSON file is not manually corrupted.
🔮 Future Improvements
- Connect to a real clinic scheduling database.
- Persist doctor availability and booking slots in a database.
- Add automatic scheduled SMS/email reminders.
- Add authentication and role-based access control.
- Add multilingual voice support.
- Add appointment audit logs and stronger privacy/security controls.
- Deploy frontend and backend to cloud hosting.
👩‍💻 Author
MediVoice AI — AI Voice Receptionist prototype project.