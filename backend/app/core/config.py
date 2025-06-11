import os
from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Загрузка переменных окружения из файла .env
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=env_path)


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str
    TELEGRAM_TOKEN: str
    CHANNEL_ID: str
    POST_CHANNEL_ID: str
    PROVIDER_TOKEN: str
    REDIS_URL: str
    GOOGLE_API_KEY: str
    ELEVENLABS_API_KEY: str
    D_ID_API_KEY: str
    FASTAPI_ADMIN_SECRET_KEY: str

    class Config:
        env_file = env_path
        env_file_encoding = "utf-8"


settings = Settings() 