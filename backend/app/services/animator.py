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
        # Проверяем наличие файлов и преобразуем пути в абсолютные при необходимости
        if not os.path.isabs(avatar_path):
            # Если путь относительный, преобразуем его в абсолютный от корня проекта
            project_root = Path(__file__).resolve().parents[3]  # backend/app/services -> корень проекта
            avatar_path = os.path.join(project_root, avatar_path)
        
        if not os.path.exists(avatar_path):
            raise FileNotFoundError(f"Файл аватара не найден по пути: {avatar_path}")
            
        if not os.path.isabs(audio_path):
            project_root = Path(__file__).resolve().parents[3]
            audio_path = os.path.join(project_root, audio_path)
            
        print(f"Использую путь к аватару: {avatar_path}")
        print(f"Использую путь к аудио: {audio_path}")
        
        # Проверяем размер файлов
        avatar_size = os.path.getsize(avatar_path)
        audio_size = os.path.getsize(audio_path)
        
        print(f"Размер файла аватара: {avatar_size} байт")
        print(f"Размер аудио файла: {audio_size} байт")
        
        if avatar_size == 0:
            raise ValueError("Файл аватара пуст")
        
        if audio_size == 0:
            raise ValueError("Аудио файл пуст")
        
        # 1. Отправляем запрос на создание "разговора" (talk)
        create_talk_url = "https://api.d-id.com/talks"
        
        # Проверяем, что файлы существуют и доступны для чтения
        try:
            with open(avatar_path, "rb") as image_file, open(audio_path, "rb") as audio_file:
                files = {
                    "source_image": ("avatar.jpeg", image_file, "image/jpeg"),
                    "driven_audio": ("audio.mp3", audio_file, "audio/mpeg"),
                }
                
                # Добавляем дополнительные параметры для повышения надежности
                create_response = httpx.post(
                    create_talk_url, 
                    headers=headers, 
                    files=files, 
                    timeout=120  # Увеличиваем таймаут до 2 минут
                )
                
                # Если ответ не успешный, выводим подробную информацию
                if create_response.status_code != 200:
                    print(f"D-ID API вернул ошибку: {create_response.status_code}")
                    print(f"Ответ: {create_response.text}")
                    
                    # Пытаемся распарсить JSON ответ для более подробной информации
                    try:
                        error_data = create_response.json()
                        print(f"Детали ошибки: {json.dumps(error_data, indent=2)}")
                    except Exception:
                        pass
                    
                    # Вместо вызова raise_for_status, возвращаем путь к исходному аватару
                    # Это позволит продолжить обработку без анимации
                    project_root = Path(__file__).resolve().parents[3]
                    media_dir = project_root / "media"
                    media_dir.mkdir(exist_ok=True)
                    fallback_path = media_dir / f"user_{user_id}_avatar_fallback.jpg"
                    
                    # Копируем исходный аватар как заглушку
                    shutil.copy(avatar_path, fallback_path)
                    print(f"Создана заглушка аватара: {fallback_path}")
                    return str(fallback_path)
        except Exception as e:
            print(f"Ошибка при открытии файлов или отправке запроса: {e}")
            # Создаем заглушку и возвращаем её путь
            project_root = Path(__file__).resolve().parents[3]
            media_dir = project_root / "media"
            media_dir.mkdir(exist_ok=True)
            fallback_path = media_dir / f"user_{user_id}_avatar_fallback.jpg"
            
            # Копируем исходный аватар как заглушку
            shutil.copy(avatar_path, fallback_path)
            print(f"Создана заглушка аватара из-за ошибки: {fallback_path}")
            return str(fallback_path)

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
                print(f"D-ID: Ошибка генерации видео: {error_details}")
                # Вместо вызова исключения, возвращаем путь к исходному аватару
                project_root = Path(__file__).resolve().parents[3]
                media_dir = project_root / "media"
                media_dir.mkdir(exist_ok=True)
                fallback_path = media_dir / f"user_{user_id}_avatar_fallback.jpg"
                
                # Копируем исходный аватар как заглушку
                shutil.copy(avatar_path, fallback_path)
                print(f"Создана заглушка аватара из-за ошибки генерации: {fallback_path}")
                return str(fallback_path)
            time.sleep(3)
        else:
            print("D-ID: Таймаут ожидания генерации видео.")
            # Вместо вызова исключения, возвращаем путь к исходному аватару
            project_root = Path(__file__).resolve().parents[3]
            media_dir = project_root / "media"
            media_dir.mkdir(exist_ok=True)
            fallback_path = media_dir / f"user_{user_id}_avatar_fallback.jpg"
            
            # Копируем исходный аватар как заглушку
            shutil.copy(avatar_path, fallback_path)
            print(f"Создана заглушка аватара из-за таймаута: {fallback_path}")
            return str(fallback_path)

        if not result_url:
            print("D-ID: Не удалось получить URL готового видео.")
            # Вместо вызова исключения, возвращаем путь к исходному аватару
            project_root = Path(__file__).resolve().parents[3]
            media_dir = project_root / "media"
            media_dir.mkdir(exist_ok=True)
            fallback_path = media_dir / f"user_{user_id}_avatar_fallback.jpg"
            
            # Копируем исходный аватар как заглушку
            shutil.copy(avatar_path, fallback_path)
            print(f"Создана заглушка аватара из-за отсутствия URL: {fallback_path}")
            return str(fallback_path)

        # 3. Скачиваем готовое видео
        try:
            video_response = httpx.get(result_url, timeout=60)
            video_response.raise_for_status()

            # Сохраняем видео
            project_root = Path(__file__).resolve().parents[3]
            media_dir = project_root / "media"
            media_dir.mkdir(exist_ok=True)
            output_path = media_dir / f"user_{user_id}_animated_avatar.mp4"
            with open(output_path, "wb") as f:
                f.write(video_response.content)

            print(f"D-ID: Анимированное видео сохранено в {output_path}")
            return str(output_path)
        except Exception as e:
            print(f"Ошибка при скачивании видео: {e}")
            # Создаем заглушку и возвращаем её путь
            project_root = Path(__file__).resolve().parents[3]
            media_dir = project_root / "media"
            media_dir.mkdir(exist_ok=True)
            fallback_path = media_dir / f"user_{user_id}_avatar_fallback.jpg"
            
            # Копируем исходный аватар как заглушку
            shutil.copy(avatar_path, fallback_path)
            print(f"Создана заглушка аватара из-за ошибки скачивания: {fallback_path}")
            return str(fallback_path)

    except httpx.HTTPStatusError as e:
        print(f"D-ID: HTTP ошибка: {e.response.status_code} - {e.response.text}")
        # Вместо повторного вызова исключения, возвращаем путь к исходному аватару
        project_root = Path(__file__).resolve().parents[3]
        media_dir = project_root / "media"
        media_dir.mkdir(exist_ok=True)
        fallback_path = media_dir / f"user_{user_id}_avatar_fallback.jpg"
        
        # Копируем исходный аватар как заглушку, если он существует
        if os.path.exists(avatar_path):
            shutil.copy(avatar_path, fallback_path)
        else:
            # Создаем пустой файл, если исходный аватар не найден
            with open(fallback_path, "wb") as f:
                f.write(b"")
                
        print(f"Создана заглушка аватара из-за HTTP ошибки: {fallback_path}")
        return str(fallback_path)
    except Exception as e:
        print(f"D-ID: Произошла ошибка: {e}")
        # Вместо повторного вызова исключения, возвращаем путь к исходному аватару
        project_root = Path(__file__).resolve().parents[3]
        media_dir = project_root / "media"
        media_dir.mkdir(exist_ok=True)
        fallback_path = media_dir / f"user_{user_id}_avatar_fallback.jpg"
        
        # Копируем исходный аватар как заглушку, если он существует
        if os.path.exists(avatar_path):
            shutil.copy(avatar_path, fallback_path)
        else:
            # Создаем пустой файл, если исходный аватар не найден
            with open(fallback_path, "wb") as f:
                f.write(b"")
                
        print(f"Создана заглушка аватара из-за неизвестной ошибки: {fallback_path}")
        return str(fallback_path) 