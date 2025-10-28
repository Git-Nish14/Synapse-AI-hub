import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")

settings = Settings()
