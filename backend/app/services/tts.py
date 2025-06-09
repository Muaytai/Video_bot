import os
from pathlib import Path
from elevenlabs import Voice, VoiceSettings
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv

# Загружаем переменные окружения из .env в корне проекта
load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

if not ELEVENLABS_API_KEY:
    raise ValueError("ELEVENLABS_API_KEY не найден в .env файле")

client = ElevenLabs(api_key=ELEVENLABS_API_KEY)


def generate_audio_from_text(text: str, user_id: int) -> str:
    """
    Генерирует аудио из текста с помощью ElevenLabs и сохраняет его.

    Args:
        text: Текст для озвучки.
        user_id: ID пользователя для создания уникального имени файла.

    Returns:
        Путь к сохраненному аудиофайлу.
    """
    try:
        # Генерируем аудио
        audio = client.generate(
            text=text,
            voice=Voice(
                voice_id='21m00Tcm4TlvDq8ikWAM',  # Используем предопределенный голос Adam
                settings=VoiceSettings(stability=0.5, similarity_boost=0.75, style=0.0, use_speaker_boost=True)
            ),
            model='eleven_multilingual_v2'
        )

        # Создаем директорию media, если она не существует
        media_dir = Path("media")
        media_dir.mkdir(exist_ok=True)

        # Сохраняем аудиофайл
        output_path = media_dir / f"user_{user_id}_audio.mp3"
        with open(output_path, "wb") as f:
            f.write(audio)

        print(f"Аудио успешно сгенерировано и сохранено в {output_path}")
        return str(output_path)

    except Exception as e:
        print(f"Ошибка при генерации аудио: {e}")
        # В реальном проекте здесь будет логирование
        raise 