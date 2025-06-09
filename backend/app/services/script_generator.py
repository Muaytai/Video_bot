import google.generativeai as genai
from app.core.config import settings

genai.configure(api_key=settings.GOOGLE_API_KEY)


def generate_script(theme: str, duration_seconds: int = 60) -> str:
    """
    Generates a video script using Gemini Pro.
    """
    model = genai.GenerativeModel("gemini-1.5-pro-latest")
    prompt = f"""
    Создай сценарий для короткого видео (до {duration_seconds} секунд)
    на тему: '{theme}'.
    Сценарий должен быть разбит на короткие сцены, подходящие для Reels/Shorts.
    Каждая сцена должна содержать описание происходящего и текст для озвучки.
    Структура:
    - Вступление (привлечение внимания)
    - Основная часть (раскрытие темы)
    - Заключение (призыв к действию)

    Пример:
    Сцена 1:
    [Описание: Крупный план человека, смотрящего в камеру]
    Текст: "Вы когда-нибудь задумывались, как...?"

    Сцена 2:
    [Описание: Быстрая смена кадров, иллюстрирующих тему]
    Текст: "Сегодня я расскажу вам о трех главных ошибках..."

    Пожалуйста, сгенерируй сценарий в таком формате.
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error generating script with Gemini: {e}")
        return "Не удалось сгенерировать сценарий. Попробуйте другую тему." 