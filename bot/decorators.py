from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
from bot.config import CHANNEL_ID
import logging

# Настройка логирования
logger = logging.getLogger(__name__)

def check_subscription(func):
    @wraps(func)
    async def wrapper(
        update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs
    ):
        # Временно отключаем проверку подписки - просто вызываем функцию
        logger.info("Проверка подписки временно отключена")
        return await func(update, context, *args, **kwargs)
        
        # Закомментированный код проверки подписки
        """
        user_id = update.effective_user.id
        try:
            # Логируем для отладки
            logger.info(f"Проверка подписки для пользователя {user_id} на канал {CHANNEL_ID}")
            
            # Проверяем, что CHANNEL_ID не пустой
            if not CHANNEL_ID:
                logger.error("CHANNEL_ID не задан в конфигурации")
                await update.message.reply_text(
                    "Ошибка конфигурации: ID канала не задан. Обратитесь к администратору."
                )
                return
                
            member = await context.bot.get_chat_member(
                chat_id=CHANNEL_ID, user_id=user_id
            )
            
            # Логируем результат для отладки
            logger.info(f"Статус пользователя {user_id} в канале: {member.status}")
            
            if member.status not in ["member", "administrator", "creator"]:
                await update.message.reply_text(
                    "Для использования бота необходимо подписаться на канал: "
                    f"{CHANNEL_ID}"
                )
                return
        except Exception as e:
            # Расширенное логирование ошибки
            logger.error(f"Ошибка при проверке подписки: {str(e)}")
            await update.message.reply_text(
                f"Не удалось проверить подписку. "
                f"Убедитесь, что бот является администратором канала. "
                f"Ошибка: {str(e)}"
            )
            return
        return await func(update, context, *args, **kwargs)
        """

    return wrapper 