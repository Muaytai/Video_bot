import base64
import os
import time
from pathlib import Path

import httpx
from dotenv import load_dotenv

# Загружаем переменные окружения из .env в корне проекта
load_dotenv()

D_ID_API_KEY = os.getenv("D_ID_API_KEY")
if not D_ID_API_KEY:
    raise ValueError("D_ID_API_KEY не найден в .env файле")

# D-ID API использует Basic-аутентификацию
# Ключ нужно закодировать в Base64
# Важно: D-ID требует, чтобы в конце ключа не было символа ':'
encoded_key = base64.b64encode(D_ID_API_KEY.encode("utf-8")).decode("utf-8")
headers = {
    "accept": "application/json",
    "Authorization": f"Basic {encoded_key}",
}


def animate_avatar_with_d_id(user_id: int, avatar_path: str, audio_path: str) -> str:
    """
    Анимирует аватар с помощью аудио, используя D-ID API.

    Args:
        user_id: ID пользователя для создания уникального имени файла.
        avatar_path: Путь к изображению аватара.
        audio_path: Путь к аудиофайлу.

    Returns:
        Путь к сохраненному анимированному видео.
    """
    try:
        # 1. Отправляем запрос на создание "разговора" (talk)
        create_talk_url = "https://api.d-id.com/talks"
        with open(avatar_path, "rb") as image_file, open(audio_path, "rb") as audio_file:
            files = {
                "source_image": ("avatar.jpeg", image_file, "image/jpeg"),
                "driven_audio": ("audio.mp3", audio_file, "audio/mpeg"),
            }
            create_response = httpx.post(create_talk_url, headers=headers, files=files, timeout=60)
            create_response.raise_for_status()

        talk_id = create_response.json()["id"]
        print(f"D-ID: Talk создан с ID: {talk_id}")

        # 2. Ожидаем завершения генерации видео
        get_talk_url = f"https://api.d-id.com/talks/{talk_id}"
        result_url = None
        for _ in range(100):  # Таймаут примерно 5 минут
            get_response = httpx.get(get_talk_url, headers=headers, timeout=30)
            get_response.raise_for_status()
            status = get_response.json().get("status")
            print(f"D-ID: Статус генерации: {status}")

            if status == "done":
                result_url = get_response.json().get("result_url")
                break
            elif status == "error":
                error_details = get_response.json().get("error")
                raise Exception(f"D-ID: Ошибка генерации видео: {error_details}")
            time.sleep(3)
        else:
            raise Exception("D-ID: Таймаут ожидания генерации видео.")

        if not result_url:
            raise Exception("D-ID: Не удалось получить URL готового видео.")

        # 3. Скачиваем готовое видео
        video_response = httpx.get(result_url, timeout=60)
        video_response.raise_for_status()

        # Сохраняем видео
        media_dir = Path("media")
        media_dir.mkdir(exist_ok=True)
        output_path = media_dir / f"user_{user_id}_animated_avatar.mp4"
        with open(output_path, "wb") as f:
            f.write(video_response.content)

        print(f"D-ID: Анимированное видео сохранено в {output_path}")
        return str(output_path)

    except httpx.HTTPStatusError as e:
        print(f"D-ID: HTTP ошибка: {e.response.status_code} - {e.response.text}")
        raise
    except Exception as e:
        print(f"D-ID: Произошла ошибка: {e}")
        raise 