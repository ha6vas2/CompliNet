import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    APP_NAME: str = os.getenv("APP_NAME", "CompliNet Dashboard")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() in ("true", "1", "t")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./test.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key")
    ALLOWED_HOSTS: list = os.getenv("ALLOWED_HOSTS", "").split(",") if os.getenv("ALLOWED_HOSTS") else []

config = Config()