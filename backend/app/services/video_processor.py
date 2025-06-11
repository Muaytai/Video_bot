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
    print(f"Начало рендеринга видео для пользователя {user_id}")
    
    # Словарь с путями к фоновым видео
    backgrounds = {
        "Природа": "assets/backgrounds/nature.mp4",
        "Офис": "assets/backgrounds/office.mp4",
        "Город": "assets/backgrounds/city.mp4",
        "Абстракция": "assets/backgrounds/abstract.mp4",
    }
    
    # Проверяем, выбран ли режим "Без фона"
    if background_name == "Без фона":
        print("Выбран режим без фона, будет создан прозрачный фон")
        background_path = None
    else:
        # Получаем путь к фоновому видео
        background_path = backgrounds.get(background_name)
        if not background_path:
            print(f"Фон не найден для {background_name}, будет создан цветной фон")
            background_path = None
    
    print(f"Путь к аватару: {animated_avatar_path}")
    
    # Загружаем анимированный аватар
    avatar_clip = VideoFileClip(animated_avatar_path)
    
    # Создаем фон
    if background_path:
        # Если есть путь к фоновому видео, используем его
        bg_clip = VideoFileClip(background_path)
        # Обрезаем или зацикливаем фоновое видео, чтобы оно соответствовало длине аватара
        if bg_clip.duration < avatar_clip.duration:
            bg_clip = bg_clip.loop(duration=avatar_clip.duration)
        else:
            bg_clip = bg_clip.subclip(0, avatar_clip.duration)
    else:
        # Если нет пути к фоновому видео, создаем белый фон
        if background_name == "Без фона":
            print("Создаем прозрачный фон (белый)")
            bg_color = (255, 255, 255)  # Белый цвет
        else:
            print("Создаем цветной фон")
            bg_color = (0, 120, 212)  # Синий цвет
        
        # Создаем цветной фон размером с аватар
        bg_clip = ColorClip(
            size=(avatar_clip.w, avatar_clip.h),
            color=bg_color,
            duration=avatar_clip.duration,
        )
    
    # Размещаем аватар по центру фона
    avatar_clip = avatar_clip.with_position("center")
    
    # Создаем композицию из фона и аватара
    final_clip = CompositeVideoClip([bg_clip, avatar_clip])
    
    # Сохраняем финальное видео
    output_path = f"media/user_{user_id}_final_video.mp4"
    final_clip.write_videofile(output_path, fps=24, codec="libx264")
    
    # Закрываем клипы для освобождения ресурсов
    avatar_clip.close()
    bg_clip.close()
    final_clip.close()
    
    print(f"Финальное видео сохранено в {output_path}")
    return output_path 