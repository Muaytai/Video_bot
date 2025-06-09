import httpx
from app.core.config import settings
import logging
from typing import List, Union


def post_to_telegram(
    video_path: str,
    caption: str,
    channel_ids: Union[str, List[str]] = None,
    bot_token: str = None,
):
    """
    Отправляет видео в один или несколько Telegram-каналов.
    channel_ids: str или список str (ID или username канала)
    bot_token: если не указан, берётся из settings
    """
    if bot_token is None:
        bot_token = settings.TELEGRAM_TOKEN
    if channel_ids is None:
        channel_ids = [settings.POST_CHANNEL_ID]
    if isinstance(channel_ids, str):
        channel_ids = [channel_ids]

    url = f"https://api.telegram.org/bot{bot_token}/sendVideo"
    for channel_id in channel_ids:
        try:
            with open(video_path, "rb") as video_file:
                response = httpx.post(
                    url,
                    data={"chat_id": channel_id, "caption": caption},
                    files={"video": video_file},
                    timeout=120,
                )
                response.raise_for_status()
            logging.info(f"Видео успешно отправлено в канал {channel_id}")
        except Exception as e:
            logging.error(f"Ошибка при отправке видео в Telegram канал {channel_id}: {e}")

