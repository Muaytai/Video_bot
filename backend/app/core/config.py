from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    TELEGRAM_TOKEN: str
    GOOGLE_API_KEY: str
    POST_CHANNEL_ID: str

    class Config:
        env_file = ".env"


settings = Settings() 