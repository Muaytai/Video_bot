import time
from pathlib import Path

from moviepy.editor import VideoFileClip, CompositeVideoClip
from app.services.tts import generate_audio_from_text


def render_final_video(
    user_id: int, animated_avatar_path: str, background_name: str
) -> str:
    """
    Собирает финальное видео, накладывая анимированный аватар на фон.

    Args:
        user_id: ID пользователя для уникального имени файла.
        animated_avatar_path: Путь к видео с анимированным аватаром.
        background_name: Название фона (например, 'Природа').

    Returns:
        Путь к готовому финальному видео.
    """
    try:
        print(f"Начало рендеринга видео для пользователя {user_id}")

        # Определяем путь к фоновому видео.
        # В реальном проекте здесь может быть более сложная логика.
        # Пока мы предполагаем, что фоны лежат в 'assets/backgrounds'
        background_path = f"assets/backgrounds/{background_name}.mp4"

        # Загружаем клипы
        avatar_clip = VideoFileClip(animated_avatar_path)
        background_clip = VideoFileClip(background_path)

        # Обрезаем фон по длительности аватара
        background_clip = background_clip.subclip(0, avatar_clip.duration)

        # Масштабируем аватар, если нужно (например, до 50% от ширины фона)
        # avatar_clip = avatar_clip.resize(width=background_clip.w * 0.5)

        # Создаем композицию: аватар по центру поверх фона
        final_clip = CompositeVideoClip(
            [background_clip, avatar_clip.set_position("center")]
        )

        # Создаем директорию media, если она не существует
        media_dir = Path("media")
        media_dir.mkdir(exist_ok=True)

        # Сохраняем результат
        output_path = media_dir / f"user_{user_id}_final_video.mp4"
        final_clip.write_videofile(
            str(output_path),
            codec="libx264",
            audio_codec="aac",
            temp_audiofile="temp-audio.m4a",
            remove_temp=True,
        )

        # Закрываем клипы, чтобы освободить ресурсы
        avatar_clip.close()
        background_clip.close()
        final_clip.close()

        print(f"Финальное видео сохранено в {output_path}")
        return str(output_path)

    except Exception as e:
        print(f"Ошибка при рендеринге видео: {e}")
        # Здесь должно быть логирование
        raise 