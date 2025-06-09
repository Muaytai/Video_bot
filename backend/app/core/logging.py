import logging
import os
from logging.handlers import RotatingFileHandler

import httpx

from app.core.config import settings

LOG_PATH = "logs"
os.makedirs(LOG_PATH, exist_ok=True)


class TelegramHandler(logging.Handler):
    def __init__(self, token, chat_id):
        super().__init__()
        self.token = token
        self.chat_id = chat_id

    def emit(self, record):
        log_entry = self.format(record)
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {"chat_id": self.chat_id, "text": log_entry}
        try:
            httpx.post(url, json=payload)
        except Exception:
            pass  # Avoid logging loops


def setup_logging():
    log_file_path = os.path.join(LOG_PATH, "app.log")
    # File handler
    file_handler = RotatingFileHandler(
        log_file_path, maxBytes=10000000, backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(file_formatter)

    # Telegram handler for critical errors
    # Or a dedicated admin chat
    telegram_handler = TelegramHandler(
        token=settings.TELEGRAM_TOKEN, chat_id=settings.POST_CHANNEL_ID
    )
    telegram_handler.setLevel(logging.CRITICAL)
    telegram_formatter = logging.Formatter(
        "🚨 CRITICAL ERROR in %(name)s 🚨\n\n%(message)s"
    )
    telegram_handler.setFormatter(telegram_formatter)

    # Root logger
    logging.basicConfig(
        level=logging.INFO,
        handlers=[logging.StreamHandler(), file_handler, telegram_handler],
    ) 