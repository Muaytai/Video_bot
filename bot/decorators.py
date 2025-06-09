from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
from bot.config import CHANNEL_ID

def check_subscription(func):
    @wraps(func)
    async def wrapper(
        update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs
    ):
        user_id = update.effective_user.id
        try:
            member = await context.bot.get_chat_member(
                chat_id=CHANNEL_ID, user_id=user_id
            )
            if member.status not in ["member", "administrator", "creator"]:
                await update.message.reply_text(
                    "Для использования бота необходимо подписаться на канал: "
                    f"{CHANNEL_ID}"
                )
                return
        except Exception:
            await update.message.reply_text(
                "Не удалось проверить подписку. "
                "Убедитесь, что бот является администратором канала."
            )
            return
        return await func(update, context, *args, **kwargs)

    return wrapper 