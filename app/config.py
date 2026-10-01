import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent

load_dotenv(PROJECT_DIR / ".env")

APP_NAME = "FitBuddy – AI Fitness Plan Generator"

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{PROJECT_DIR / 'fitbuddy.db'}"
)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

# Keep the model configurable through .env.
# If your Gemini account uses a different available model,
# change these values without changing Python code.
GEMINI_WORKOUT_MODEL = os.getenv(
    "GEMINI_WORKOUT_MODEL",
    "gemini-2.5-flash"
)

GEMINI_NUTRITION_MODEL = os.getenv(
    "GEMINI_NUTRITION_MODEL",
    "gemini-2.5-flash"
)

GEMINI_TEMPERATURE = float(
    os.getenv("GEMINI_TEMPERATURE", "0.3")
)

GEMINI_MAX_OUTPUT_TOKENS = int(
    os.getenv("GEMINI_MAX_OUTPUT_TOKENS", "1600")
)

# DEMO_MODE=true allows the complete application to run
# without making Gemini API calls.
DEMO_MODE = os.getenv(
    "DEMO_MODE",
    "true"
).lower() == "true"