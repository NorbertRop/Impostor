import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
    FIREBASE_SERVICE_ACCOUNT = os.getenv("FIREBASE_SERVICE_ACCOUNT")
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
    PORT = int(os.getenv("PORT", 8000))
    WEB_BASE_URL = os.getenv("WEB_BASE_URL", "http://localhost:5173")

    @classmethod
    def validate(cls):
        if not cls.DISCORD_TOKEN:
            raise ValueError("DISCORD_TOKEN environment variable is required")
        if not cls.FIREBASE_SERVICE_ACCOUNT:
            raise ValueError(
                "FIREBASE_SERVICE_ACCOUNT environment variable is required"
            )


config = Config()
