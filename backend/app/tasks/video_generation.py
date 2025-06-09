import httpx

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
    # 1. Generate script
    script = generate_script(theme)
    httpx.post(
        f"https://api.telegram.org/bot{bot_token}/sendMessage",
        json={"chat_id": chat_id, "text": f"Сценарий готов:\n\n{script}"},
    )

    # 2. Generate audio
    audio_path = generate_audio_from_text(script, user_id)

    # 3. Animate avatar
    animated_avatar_path = animate_avatar_with_d_id(
        user_id=user_id, avatar_path=avatar_info, audio_path=audio_path
    )

    # 4. Render final video
    final_video_path = render_final_video(
        user_id=user_id,
        animated_avatar_path=animated_avatar_path,
        background_name=background,
    )

    # 5. Send video to user
    result_caption = f"Ваше видео на тему '{theme}' готово! 🎉"
    with open(final_video_path, "rb") as video_file:
        httpx.post(
            f"https://api.telegram.org/bot{bot_token}/sendVideo",
            data={"chat_id": chat_id, "caption": result_caption},
            files={"video": video_file},
            timeout=120,
        )

    # 6. Autoposting
    post_to_telegram(
        bot_token=settings.TELEGRAM_TOKEN,
        channel_id=settings.POST_CHANNEL_ID,
        video_path=final_video_path,
        caption=f"Новое видео на тему: {theme}",
    )

    return final_video_path 