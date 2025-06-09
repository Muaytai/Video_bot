import os
import httpx
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

    os.makedirs(MEDIA_PATH, exist_ok=True)
    output_path = os.path.join(MEDIA_PATH, f"user_{user_id}_tts.mp3")

    try:
        with httpx.stream("POST", url, headers=headers, json=payload, timeout=60) as response:
            response.raise_for_status()
            with open(output_path, "wb") as f:
                for chunk in response.iter_bytes():
                    f.write(chunk)
        return output_path
    except Exception as e:
        print(f"Ошибка при генерации озвучки через ElevenLabs: {e}")
        raise 