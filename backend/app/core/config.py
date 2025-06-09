from pydantic_settings import BaseSettings
from dotenv import load_dotenv


class Settings(BaseSettings):
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
        pass


settings = Settings() 