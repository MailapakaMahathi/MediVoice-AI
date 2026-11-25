
import os
from pathlib import Path
from dotenv import load_dotenv

# Locate the backend .env file
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"

# Load environment variables
load_dotenv(ENV_FILE)

# API keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "")

# Application settings
APP_NAME = "MediVoice AI"
APP_VERSION = "1.0.0"
