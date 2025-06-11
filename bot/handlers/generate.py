import logging
import os
import httpx
from pathlib import Path
from typing import Dict, Any
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
)
from bot.decorators import check_subscription

# Включаем логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Определяем состояния разговора
THEME, BACKGROUND, AVATAR = range(3)

# URL API бэкенда
BACKEND_URL = "http://localhost:8000/api/v1"

@check_subscription
async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начало генерации видео."""
    user = update.effective_user
    logger.info(f"Пользователь {user.id} запустил команду /generate")
    
    # Создаем пользователя, если его нет
    try:
        response = httpx.post(
            f"{BACKEND_URL}/users/",
            json={"telegram_id": user.id, "username": user.username or ""}
        )
    except Exception as e:
        logger.error(f"Ошибка при создании пользователя: {e}")
    
    # Запрашиваем тему видео
    await update.message.reply_text(
        "Выберите тему для вашего видео:",
        reply_markup=ReplyKeyboardMarkup(
            [["продажи", "бизнес", "реклама"]], one_time_keyboard=True
        ),
    )
    
    return THEME

async def theme_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка выбора темы."""
    user = update.effective_user
    theme = update.message.text
    logger.info(f"Получена тема: {theme}")
    
    # Сохраняем тему в контексте
    context.user_data["theme"] = theme
    
    # Запрашиваем выбор фона
    await update.message.reply_text(
        "Отлично! Теперь выберите фон для вашего видео.",
        reply_markup=ReplyKeyboardMarkup(
            [["С фоном", "Без фона"]], one_time_keyboard=True
        ),
    )
    
    return BACKGROUND

async def background_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка выбора фона."""
    background = update.message.text
    logger.info(f"Получен выбор фона: {background}")
    
    # Сохраняем выбор фона в контексте
    context.user_data["background"] = background
    
    # Запрашиваем фото или видео для аватара
    await update.message.reply_text(
        "Теперь отправьте фото или видео для создания аватара.",
    )
    
    return AVATAR

async def avatar_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка полученного фото или видео для аватара."""
    user = update.effective_user
    logger.info(f"Получено фото для аватара от пользователя {user.id}")
    
    # Создаем директорию для медиафайлов, если её нет
    media_dir = Path("media")
    media_dir.mkdir(exist_ok=True)
    
    # Получаем фото
    photo = update.message.photo[-1]  # Берем фото с наилучшим качеством
    file = await context.bot.get_file(photo.file_id)
    
    # Создаем уникальное имя файла
    file_extension = os.path.splitext(file.file_path)[1]
    if not file_extension:
        file_extension = ".jpg"  # По умолчанию для фото
    
    file_name = f"{user.id}_{photo.file_id}{file_extension}"
    file_path = media_dir / file_name
    
    # Скачиваем файл
    await file.download_to_drive(file_path)
    logger.info(f"Файл аватара сохранен по пути: {file_path}")
    
    # Подготавливаем относительный путь для API
    relative_path = f"media/{file_name}"
    logger.info(f"Относительный путь к аватару для API: {relative_path}")
    
    # Отправляем запрос на генерацию видео
    theme = context.user_data.get("theme", "бизнес")
    background = context.user_data.get("background", "С фоном")
    
    # Подготавливаем данные для запроса
    data = {
        "user_id": user.id,
        "theme": theme,
        "chat_id": update.effective_chat.id,
        "background": background,
        "avatar_info": relative_path
    }
    
    logger.info(f"Отправка запроса на генерацию видео: {data}")
    logger.info(f"Отправка POST запроса на {BACKEND_URL}/videos/")
    
    try:
        response = httpx.post(f"{BACKEND_URL}/videos/", json=data)
        logger.info(f"Получен ответ: статус {response.status_code}, тело: {response.text}")
        
        if response.status_code == 200:
            await update.message.reply_text(
                "Ваше видео генерируется! Это может занять некоторое время. "
                "Мы отправим вам результат, как только он будет готов."
            )
        else:
            logger.error(f"Ошибка HTTP: {response.status_code} - {response.text}")
            await update.message.reply_text(
                "Произошла ошибка при создании видео. Пожалуйста, "
                "попробуйте еще раз с другими параметрами."
            )
    except Exception as e:
        logger.error(f"Ошибка при отправке запроса: {e}")
        await update.message.reply_text(
            "Произошла ошибка при подключении к серверу. "
            "Пожалуйста, попробуйте позже."
        )
    
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отмена генерации видео."""
    await update.message.reply_text(
        "Генерация видео отменена.", reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

async def reset_count(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Сбросить счетчик видео для пользователя."""
    user = update.effective_user
    logger.info(f"Пользователь {user.id} запустил команду /reset_count")
    
    try:
        response = httpx.post(
            f"{BACKEND_URL}/users/reset-video-count",
            params={"telegram_id": user.id}
        )
        
        if response.status_code == 200:
            await update.message.reply_text("Счетчик видео успешно сброшен!")
        else:
            await update.message.reply_text(f"Ошибка при сбросе счетчика: {response.text}")
    except Exception as e:
        logger.error(f"Ошибка при сбросе счетчика: {e}")
        await update.message.reply_text("Произошла ошибка при подключении к серверу.")

# Создаем обработчик разговора
generate_handler = ConversationHandler(
    entry_points=[CommandHandler("generate", generate)],
    states={
        THEME: [MessageHandler(filters.TEXT & ~filters.COMMAND, theme_selected)],
        BACKGROUND: [MessageHandler(filters.TEXT & ~filters.COMMAND, background_selected)],
        AVATAR: [MessageHandler(filters.PHOTO, avatar_received)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

# Обработчик для сброса счетчика видео
reset_count_handler = CommandHandler("reset_count", reset_count) 