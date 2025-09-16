import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    BACKEND_HOST = os.getenv("BACKEND_HOST", "localhost")
    BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8000"))
    FRONTEND_PORT = int(os.getenv("FRONTEND_PORT", "8501"))

settings = Settings()