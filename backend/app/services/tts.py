import os
import httpx
from pathlib import Path
from app.core.config import settings

MEDIA_PATH = "media"


def generate_audio_from_text(text: str, user_id: int) -> str:
    """
    Генерирует озвучку текста через ElevenLabs API и сохраняет mp3-файл.
    """
    api_key = settings.ELEVENLABS_API_KEY
    voice_id = "EXAVITQu4vr4xnSDxMaL"  # Можно заменить на другой voice_id
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
    }
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }

    # Используем абсолютный путь к директории media
    project_root = Path(__file__).resolve().parents[3]  # backend/app/services -> корень проекта
    media_dir = project_root / "media"
    media_dir.mkdir(exist_ok=True)
    output_path = media_dir / f"user_{user_id}_tts.mp3"

    try:
        with httpx.stream("POST", url, headers=headers, json=payload, timeout=60) as response:
            response.raise_for_status()
            with open(output_path, "wb") as f:
                for chunk in response.iter_bytes():
                    f.write(chunk)
        return str(output_path)
    except httpx.HTTPStatusError as e:
        # Сначала читаем тело ответа, потом парсим JSON
        error_content = e.response.read()
        try:
            error_details = e.response.json()
        except Exception:
            error_details = {"detail": error_content.decode()}

        print(f"Ошибка при генерации озвучки через ElevenLabs: {e}")
        print(f"Детали ошибки от API: {error_details}")
        raise e

    media_dir.mkdir(parents=True, exist_ok=True) 