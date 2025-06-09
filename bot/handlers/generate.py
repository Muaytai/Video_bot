import os
import httpx
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
from bot.decorators import check_subscription

THEME, BACKGROUND, AVATAR = range(3)
API_URL = "http://localhost:8000/api/v1/videos/"
MEDIA_PATH = "media"


@check_subscription
async def generate_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks for a video theme."""
    await update.message.reply_text(
        "Введите тему для вашего видео. Например: 'Маркетинг в социальных сетях'."
    )
    return THEME


async def theme_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives the theme and asks for a background."""
    context.user_data["theme"] = update.message.text
    reply_keyboard = [["Изображение", "Видео", "Без фона"]]
    await update.message.reply_text(
        "Отлично! Теперь выберите фон для вашего видео.",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            one_time_keyboard=True,
            input_field_placeholder="Выберите фон",
        ),
    )
    return BACKGROUND


async def background_received(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Receives the background choice and asks for an avatar."""
    context.user_data["background"] = update.message.text
    await update.message.reply_text(
        "Теперь отправьте фото или видео для создания аватара."
    )
    return AVATAR


async def avatar_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives the avatar and starts the video generation task."""
    user = update.effective_user
    file_to_download = None
    file_extension = ""

    if update.message.photo:
        file_to_download = await update.message.photo[-1].get_file()
        file_extension = ".jpg"
    elif update.message.video:
        file_to_download = await update.message.video.get_file()
        file_extension = ".mp4"

    if not file_to_download:
        await update.message.reply_text("Не удалось получить файл. Попробуйте еще раз.")
        return AVATAR

    os.makedirs(MEDIA_PATH, exist_ok=True)
    file_id = file_to_download.file_unique_id
    avatar_path = os.path.join(MEDIA_PATH, f"{user.id}_{file_id}{file_extension}")
    await file_to_download.download_to_drive(avatar_path)

    video_data = {
        "user_id": user.id,
        "theme": context.user_data["theme"],
        "chat_id": update.message.chat_id,
        "background": context.user_data["background"],
        "avatar_info": avatar_path,
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(API_URL, json=video_data)
            response.raise_for_status()
            await update.message.reply_text(
                "Ваш запрос принят! Видео будет сгенерировано в ближайшее "
                "время. Вы получите уведомление, когда оно будет готово."
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 403:
                await update.message.reply_text(
                    "Вы уже использовали свое бесплатное видео. "
                    "Для дальнейшего использования, пожалуйста, оформите подписку."
                )
            else:
                await update.message.reply_text(
                    "Произошла ошибка при запуске генерации видео. "
                    "Попробуйте позже."
                )

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    await update.message.reply_text("Генерация видео отменена.")
    return ConversationHandler.END


generate_handler = ConversationHandler(
    entry_points=[CommandHandler("generate", generate_start)],
    states={
        THEME: [MessageHandler(filters.TEXT & ~filters.COMMAND, theme_received)],
        BACKGROUND: [
            MessageHandler(
                filters.Regex("^(Изображение|Видео|Без фона)$"), background_received
            )
        ],
        AVATAR: [MessageHandler(filters.PHOTO | filters.VIDEO, avatar_received)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
) 