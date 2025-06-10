import os
from dotenv import load_dotenv

# Загружаем .env из backend/.env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', 'backend', '.env'))

TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID")
PROVIDER_TOKEN = os.environ.get("PROVIDER_TOKEN") 