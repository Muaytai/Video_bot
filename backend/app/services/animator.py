import base64
import os
import time
import json
from pathlib import Path
import shutil

import httpx
from dotenv import load_dotenv

# Загружаем переменные окружения из .env в корне проекта
load_dotenv()

D_ID_API_KEY = os.getenv("D_ID_API_KEY")
if not D_ID_API_KEY:
    raise ValueError("D_ID_API_KEY не найден в .env файле")

# D-ID API использует заголовок Authorization с Basic Auth
# Создаем правильный заголовок Authorization
# Ключ уже должен быть в формате username:password в base64
headers = {
    "accept": "application/json",
    "Authorization": f"Basic {D_ID_API_KEY}",
    "Content-Type": "application/json"
}


def animate_avatar_with_d_id(user_id: int, avatar_path: str, audio_path: str) -> str:
    """
    Анимирует аватар с помощью аудио, используя D-ID API.

    Args:
        user_id: ID пользователя для создания уникального имени файла.
        avatar_path: Путь к изображению аватара.
        audio_path: Путь к аудио файлу.

    Returns:
        Путь к анимированному аватару (видео).
    """
    # Проверяем и корректируем пути
    if not os.path.exists(avatar_path):
        # Проверяем путь относительно корня проекта
        project_root = Path(__file__).parent.parent.parent.parent
        full_avatar_path = project_root / avatar_path
        if os.path.exists(full_avatar_path):
            avatar_path = str(full_avatar_path)
        else:
            raise FileNotFoundError(f"Файл аватара не найден: {avatar_path}")

    if not os.path.exists(audio_path):
        project_root = Path(__file__).parent.parent.parent.parent
        full_audio_path = project_root / audio_path
        if os.path.exists(full_audio_path):
            audio_path = str(full_audio_path)
        else:
            raise FileNotFoundError(f"Файл аудио не найден: {audio_path}")

    print(f"Использую путь к аватару: {avatar_path}")
    print(f"Использую путь к аудио: {audio_path}")

    # Проверяем размеры файлов
    avatar_size = os.path.getsize(avatar_path)
    audio_size = os.path.getsize(audio_path)
    print(f"Размер файла аватара: {avatar_size} байт")
    print(f"Размер аудио файла: {audio_size} байт")

    # Создаем директорию для сохранения результата, если ее нет
    media_dir = Path("media")
    media_dir.mkdir(exist_ok=True)

    # Путь для сохранения результата
    output_path = f"media/user_{user_id}_animated_avatar.mp4"
    full_output_path = Path(__file__).parent.parent.parent.parent / output_path

    try:
        # 1. Отправляем запрос на создание "разговора" (talk)
        create_talk_url = "https://api.d-id.com/talks"
        
        # Проверяем, что файлы существуют и доступны для чтения
        try:
            with open(avatar_path, "rb") as image_file, open(audio_path, "rb") as audio_file:
                # Создаем мультипарт запрос
                with httpx.Client(timeout=None) as client:
                    # Сначала загружаем изображение
                    files = {"image": (os.path.basename(avatar_path), image_file, "image/jpeg")}
                    response = client.post(
                        create_talk_url,
                        headers=headers,
                        files=files,
                        data={
                            "audio": audio_file.read(),
                            "driver_url": "bank://lively/",
                            "config": json.dumps({"stitch": True})
                        }
                    )
        except Exception as e:
            print(f"Ошибка при отправке файлов: {e}")
            raise

        print(f"HTTP Request: POST {create_talk_url} \"{response.status_code} {response.reason_phrase}\"")
        
        if response.status_code != 201:
            print(f"D-ID API вернул ошибку: {response.status_code}")
            print(f"Ответ: {response.text}")
            print(f"Детали ошибки: {response.text}")
            
            # Создаем заглушку - просто копируем исходное изображение
            fallback_path = f"media/user_{user_id}_avatar_fallback.jpg"
            full_fallback_path = Path(__file__).parent.parent.parent.parent / fallback_path
            shutil.copy(avatar_path, full_fallback_path)
            print(f"Создана заглушка аватара: {full_fallback_path} ")
            return str(full_fallback_path)
        
        # 2. Получаем ID созданного "разговора"
        talk_data = response.json()
        talk_id = talk_data["id"]
        
        # 3. Ждем, пока видео будет готово
        get_talk_url = f"https://api.d-id.com/talks/{talk_id}"
        status = "created"
        max_attempts = 60  # максимальное количество попыток
        attempt = 0
        
        while status != "done" and attempt < max_attempts:
            time.sleep(1)  # ждем 1 секунду между запросами
            response = httpx.get(get_talk_url, headers=headers)
            
            if response.status_code != 200:
                print(f"Ошибка при получении статуса: {response.status_code}")
                print(f"Ответ: {response.text}")
                break
            
            talk_data = response.json()
            status = talk_data["status"]
            print(f"Статус генерации: {status}")
            
            attempt += 1
        
        if status != "done":
            print("Превышено время ожидания или произошла ошибка")
            # Создаем заглушку
            fallback_path = f"media/user_{user_id}_avatar_fallback.jpg"
            full_fallback_path = Path(__file__).parent.parent.parent.parent / fallback_path
            shutil.copy(avatar_path, full_fallback_path)
            print(f"Создана заглушка аватара: {full_fallback_path}")
            return str(full_fallback_path)
        
        # 4. Скачиваем готовое видео
        result_url = talk_data["result_url"]
        response = httpx.get(result_url)
        
        if response.status_code != 200:
            print(f"Ошибка при скачивании видео: {response.status_code}")
            # Создаем заглушку
            fallback_path = f"media/user_{user_id}_avatar_fallback.jpg"
            full_fallback_path = Path(__file__).parent.parent.parent.parent / fallback_path
            shutil.copy(avatar_path, full_fallback_path)
            print(f"Создана заглушка аватара: {full_fallback_path}")
            return str(full_fallback_path)
        
        # Сохраняем видео
        with open(full_output_path, "wb") as f:
            f.write(response.content)
        
        print(f"Анимированный аватар сохранен в {full_output_path}")
        return str(full_output_path)
    
    except Exception as e:
        print(f"Ошибка при анимации аватара: {e}")
        # В случае любой ошибки создаем заглушку
        fallback_path = f"media/user_{user_id}_avatar_fallback.jpg"
        full_fallback_path = Path(__file__).parent.parent.parent.parent / fallback_path
        try:
            shutil.copy(avatar_path, full_fallback_path)
            print(f"Создана заглушка аватара: {full_fallback_path}")
            return str(full_fallback_path)
        except Exception as copy_error:
            print(f"Ошибка при создании заглушки: {copy_error}")
            raise 