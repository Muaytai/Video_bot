import os
import traceback
from pathlib import Path
import asyncio
from telegram import Bot

from app.core.celery_app import celery_app
from app.core.config import settings
from app.services.animator import animate_avatar_with_d_id
from app.services.script_generator import generate_script
from app.services.tts import generate_audio_from_text
from app.services.video_processor import render_final_video
from app.services.autoposting import post_to_telegram


@celery_app.task
def generate_video_task(
    user_id: int, theme: str, chat_id: int, background: str, avatar_info: str
) -> str:
    """
    Асинхронная задача для генерации видео.
    
    Args:
        user_id: ID пользователя.
        theme: Тема видео.
        chat_id: ID чата для отправки результата.
        background: Название фона.
        avatar_info: Путь к аватару или информация о нем.
    
    Returns:
        Путь к готовому видео.
    """
    bot = Bot(token=settings.TELEGRAM_TOKEN)

    async def send_message(text):
        await bot.send_message(chat_id=chat_id, text=text)

    try:
        # 1. Генерация сценария
        try:
            script = generate_script(theme)
        except Exception as e:
            print(f"Error generating script with Gemini: {e}")
            from app.services.script_generator import DEFAULT_SCRIPTS
            script = DEFAULT_SCRIPTS.get(theme, "Сценарий по умолчанию...")
        
        asyncio.run(send_message(f"Сценарий готов:\n\n{script}"))
        
        # 2. Генерация аудио
        lines = [line.split('"')[1] for line in script.split('\n') if line.strip().startswith("Текст:")]
        full_text = " ".join(lines)
        audio_path = generate_audio_from_text(user_id, full_text)
        
        # 3. Resolve paths
        project_root = Path(__file__).resolve().parent.parent.parent.parent
        
        full_avatar_path = project_root / avatar_info
        if not full_avatar_path.is_file():
             raise FileNotFoundError(f"Файл аватара не найден: {full_avatar_path}")

        full_audio_path = project_root / audio_path
        if not full_audio_path.is_file():
            backend_audio_path = Path.cwd() / audio_path
            if backend_audio_path.is_file():
                full_audio_path = backend_audio_path
            else:
                 raise FileNotFoundError(f"Аудио файл не найден: {full_audio_path} or {backend_audio_path}")

        # 4. Анимация аватара
        try:
            animated_avatar_path = animate_avatar_with_d_id(
                user_id=user_id,
                avatar_path=str(full_avatar_path),
                audio_path=str(full_audio_path)
            )
        except Exception as e:
            print(f"Ошибка при анимации аватара: {e}")
            traceback.print_exc()
            asyncio.run(send_message("Не удалось анимировать аватар. Используем статичное изображение."))
            animated_avatar_path = str(full_avatar_path)
        
        # 5. Рендеринг финального видео
        final_video_path = render_final_video(
            user_id=user_id,
            animated_avatar_path=animated_avatar_path,
            background_name=background
        )
        
        # 6. Autoposting
        try:
            post_to_telegram(
                bot_token=settings.TELEGRAM_TOKEN,
                video_path=final_video_path,
                caption=f"Новое видео на тему: {theme}",
                channel_ids=settings.POST_CHANNEL_ID
            )
        except Exception as e:
            print(f"Ошибка при автопостинге: {e}")
            traceback.print_exc()
        
        # 7. Отправка видео пользователю
        async def send_final_video():
            with open(final_video_path, "rb") as video_file:
                await bot.send_video(
                    chat_id=chat_id,
                    video=video_file,
                    caption=f"Ваше видео на тему \"{theme}\" готово!"
                )
        asyncio.run(send_final_video())
        
        return final_video_path
    
    except Exception as e:
        print(f"Ошибка при генерации видео: {e}")
        traceback.print_exc()
        try:
            asyncio.run(send_message("Произошла ошибка при создании видео. Пожалуйста, попробуйте еще раз с другими параметрами."))
        except Exception as telegram_err:
            print(f"Failed to send error message to telegram: {telegram_err}")
        return None 