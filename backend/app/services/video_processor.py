import time
import os
from pathlib import Path
import numpy as np

from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.VideoClip import ColorClip, ImageClip
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
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

        # Преобразуем пути в абсолютные при необходимости
        if not os.path.isabs(animated_avatar_path):
            project_root = Path(__file__).resolve().parents[3]  # backend/app/services -> корень проекта
            animated_avatar_path = os.path.join(project_root, animated_avatar_path)
            
        # Определяем путь к фоновому видео.
        # В реальном проекте здесь может быть более сложная логика.
        # Пока мы предполагаем, что фоны лежат в 'assets/backgrounds'
        project_root = Path(__file__).resolve().parents[3]
        
        # Проверяем различные расширения для фона
        background_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.jpg', '.jpeg', '.png', '.gif', '.txt']
        background_path = None
        
        for ext in background_extensions:
            test_path = project_root / f"assets/backgrounds/{background_name}{ext}"
            if os.path.exists(test_path):
                background_path = test_path
                break
        
        if background_path:
            print(f"Найден фон: {background_path}")
        else:
            print(f"Фон не найден для {background_name}, будет создан цветной фон")
        
        print(f"Путь к аватару: {animated_avatar_path}")
        
        if not os.path.exists(animated_avatar_path):
            raise FileNotFoundError(f"Файл аватара не найден: {animated_avatar_path}")
        
        # Проверяем, видео это или изображение
        avatar_clip = None
        avatar_duration = 10  # Длительность по умолчанию, если это изображение
        is_image = False
        
        # Определяем тип файла по расширению
        file_ext = os.path.splitext(animated_avatar_path)[1].lower()
        if file_ext in ['.mp4', '.avi', '.mov', '.mkv']:
            # Это видео
            avatar_clip = VideoFileClip(str(animated_avatar_path))
            avatar_duration = avatar_clip.duration
        else:
            # Это изображение, создаем из него клип длительностью 10 секунд
            is_image = True
            try:
                # Создаем последовательность из одного и того же изображения
                avatar_clip = ImageSequenceClip([str(animated_avatar_path)], durations=[avatar_duration])
            except Exception as e:
                print(f"Ошибка при создании клипа из изображения: {e}")
                # Создаем пустой цветной клип как заглушку
                avatar_clip = ColorClip(
                    size=(640, 480),
                    color=(100, 100, 100),
                    duration=avatar_duration
                )
        
        # Проверяем наличие фона и его тип
        background_clip = None
        if background_path:
            bg_ext = os.path.splitext(str(background_path))[1].lower()
            if bg_ext in ['.mp4', '.avi', '.mov', '.mkv']:
                # Это видео
                background_clip = VideoFileClip(str(background_path))
                # Обрезаем фон по длительности аватара
                background_clip = background_clip.subclip(0, avatar_duration)
            elif bg_ext in ['.jpg', '.jpeg', '.png', '.gif']:
                # Это изображение
                try:
                    background_image = ImageClip(str(background_path))
                    background_clip = background_image.set_duration(avatar_duration)
                except Exception as e:
                    print(f"Ошибка при создании фона из изображения: {e}")
                    background_clip = None
            else:
                # Это текстовый файл или другой формат - игнорируем
                background_clip = None
        
        if not background_clip:
            print(f"Создаем простой цветной фон.")
            # Создаем простой цветной фон
            if background_name.lower() == "изображение":
                bg_color = (30, 100, 200)  # Синий
            elif background_name.lower() == "видео":
                bg_color = (30, 150, 50)   # Зеленый
            else:
                bg_color = (50, 50, 50)    # Серый
                
            background_clip = ColorClip(
                size=(1280, 720),  # HD разрешение
                color=bg_color,
                duration=avatar_duration
            )

        # Масштабируем аватар, если нужно (например, до 50% от ширины фона)
        if is_image:
            # Для ImageSequenceClip используем метод resized вместо resize
            avatar_clip = avatar_clip.resized(width=background_clip.w * 0.5)
        else:
            # Для VideoFileClip используем метод resize
            avatar_clip = avatar_clip.resize(width=background_clip.w * 0.5)

        # Создаем композицию: аватар по центру поверх фона
        final_clip = CompositeVideoClip(
            [background_clip, avatar_clip.set_position("center")]
        )

        # Создаем директорию media, если она не существует
        media_dir = project_root / "media"
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