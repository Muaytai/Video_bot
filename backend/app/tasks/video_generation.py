import httpx
import os
import traceback
from pathlib import Path

from app.core.celery_app import celery_app
from app.core.config import settings
from app.services.animator import animate_avatar_with_d_id
from app.services.autoposting import post_to_telegram
from app.services.script_generator import generate_script
from app.services.tts import generate_audio_from_text
from app.services.video_processor import render_final_video


@celery_app.task
def generate_video_task(
    user_id: int,
    theme: str,
    bot_token: str,
    chat_id: int,
    background: str,
    avatar_info: str,
):
    """
    A task that simulates video generation and sends a message on completion.
    """
    try:
        # 1. Generate script
        try:
            script = generate_script(theme)
            httpx.post(
                f"https://api.telegram.org/bot{bot_token}/sendMessage",
                json={"chat_id": chat_id, "text": f"Сценарий готов:\n\n{script}"},
            )
        except Exception as e:
            print(f"Ошибка при генерации сценария: {e}")
            traceback.print_exc()
            # Отправляем сообщение об ошибке пользователю
            httpx.post(
                f"https://api.telegram.org/bot{bot_token}/sendMessage",
                json={"chat_id": chat_id, "text": f"Возникла проблема при генерации сценария. Используем запасной вариант."},
            )
            # Используем запасной вариант из script_generator
            script = generate_script(theme)

        # 2. Generate audio
        try:
            audio_path = generate_audio_from_text(script, user_id)
        except Exception as e:
            print(f"Ошибка при генерации аудио: {e}")
            traceback.print_exc()
            # Отправляем сообщение об ошибке пользователю
            httpx.post(
                f"https://api.telegram.org/bot{bot_token}/sendMessage",
                json={"chat_id": chat_id, "text": f"Возникла проблема при генерации аудио. Используем запасной вариант."},
            )
            # Создаем пустой аудиофайл как заглушку
            project_root = Path(__file__).resolve().parents[3]
            media_dir = project_root / "media"
            media_dir.mkdir(exist_ok=True)
            audio_path = str(media_dir / f"user_{user_id}_tts.mp3")
            with open(audio_path, "wb") as f:
                # Пустой MP3 файл минимального размера
                f.write(b"\xFF\xFB\x90\x44\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")

        # 3. Animate avatar
        try:
            animated_avatar_path = animate_avatar_with_d_id(
                user_id=user_id, avatar_path=avatar_info, audio_path=audio_path
            )
        except Exception as e:
            print(f"Ошибка при анимации аватара: {e}")
            traceback.print_exc()
            # Если анимация не удалась, используем исходное изображение как заглушку
            # Преобразуем относительный путь в абсолютный
            project_root = Path(__file__).resolve().parents[3]
            if not os.path.isabs(avatar_info):
                avatar_path = project_root / avatar_info
            else:
                avatar_path = Path(avatar_info)
                
            # Создаем путь для "анимированного" аватара (хотя он не анимирован)
            media_dir = project_root / "media"
            media_dir.mkdir(exist_ok=True)
            animated_avatar_path = str(media_dir / f"user_{user_id}_avatar_fallback.jpg")
            
            # Копируем исходный файл как заглушку
            if os.path.exists(avatar_path):
                import shutil
                shutil.copy(avatar_path, animated_avatar_path)
            else:
                # Если файла нет, создаем пустой файл
                with open(animated_avatar_path, "wb") as f:
                    f.write(b"")
            
            # Уведомляем пользователя о проблеме
            httpx.post(
                f"https://api.telegram.org/bot{bot_token}/sendMessage",
                json={"chat_id": chat_id, "text": "Не удалось анимировать аватар. Используем статичное изображение."},
            )

        # 4. Render final video
        try:
            final_video_path = render_final_video(
                user_id=user_id,
                animated_avatar_path=animated_avatar_path,
                background_name=background,
            )
        except Exception as e:
            print(f"Ошибка при рендеринге видео: {e}")
            traceback.print_exc()
            
            # Уведомляем пользователя о проблеме
            httpx.post(
                f"https://api.telegram.org/bot{bot_token}/sendMessage",
                json={"chat_id": chat_id, "text": "Произошла ошибка при создании видео. Пожалуйста, попробуйте еще раз с другими параметрами."},
            )
            return None

        # 5. Send video to user
        try:
            result_caption = f"Ваше видео на тему '{theme}' готово! 🎉"
            with open(final_video_path, "rb") as video_file:
                httpx.post(
                    f"https://api.telegram.org/bot{bot_token}/sendVideo",
                    data={"chat_id": chat_id, "caption": result_caption},
                    files={"video": video_file},
                    timeout=120,
                )
        except Exception as e:
            print(f"Ошибка при отправке видео: {e}")
            traceback.print_exc()
            # Уведомляем пользователя о проблеме
            httpx.post(
                f"https://api.telegram.org/bot{bot_token}/sendMessage",
                json={"chat_id": chat_id, "text": f"Видео создано, но его не удалось отправить. Ошибка: {str(e)[:100]}..."},
            )

        # 6. Autoposting
        try:
            post_to_telegram(
                bot_token=settings.TELEGRAM_TOKEN,
                channel_id=settings.POST_CHANNEL_ID,
                video_path=final_video_path,
                caption=f"Новое видео на тему: {theme}",
            )
        except Exception as e:
            print(f"Ошибка при автопостинге: {e}")
            traceback.print_exc()

        return final_video_path
        
    except Exception as e:
        print(f"Критическая ошибка при выполнении задачи: {e}")
        traceback.print_exc()
        
        # Отправляем сообщение об ошибке пользователю
        try:
            httpx.post(
                f"https://api.telegram.org/bot{bot_token}/sendMessage",
                json={"chat_id": chat_id, "text": "Произошла непредвиденная ошибка при создании видео. Пожалуйста, попробуйте позже."},
            )
        except:
            pass
            
        return None 