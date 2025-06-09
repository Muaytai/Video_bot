import httpx
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

API_URL = "http://localhost:8000/api/v1/users/"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends explanation on how to use the bot and registers the user."""
    user = update.effective_user
    user_data = {
        "telegram_id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(API_URL, json=user_data)
            response.raise_for_status()
            message = (
                f"Привет, {user.mention_html()}! Вы успешно зарегистрированы. 👋\n\n"
                "Используйте команду /generate, чтобы создать видео."
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 400:
                message = (
                    f"Привет, {user.mention_html()}! Вы уже были зарегистрированы. 👋\n\n"
                    "Используйте команду /generate, чтобы создать видео."
                )
            else:
                message = "Произошла ошибка при регистрации. Попробуйте позже."

    await update.message.reply_html(message, reply_markup=None)


start_handler = CommandHandler("start", start) 