from telegram import Update, LabeledPrice
from telegram.ext import CommandHandler, ContextTypes, PreCheckoutQueryHandler, MessageHandler, filters
import httpx
from bot.config import PROVIDER_TOKEN

API_URL = "http://localhost:8000/api/v1/users/subscribe"  # Эндпоинт для обновления подписки

async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prices = [LabeledPrice("Подписка на месяц", 29900)]  # 299.00 RUB
    await context.bot.send_invoice(
        chat_id=update.effective_chat.id,
        title="Подписка на видео-бота",
        description="Безлимитная генерация видео на месяц",
        payload="subscribe-month",
        provider_token=PROVIDER_TOKEN,
        currency="RUB",
        prices=prices,
        start_parameter="subscribe",
    )

async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.pre_checkout_query
    await query.answer(ok=True)

async def successful_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    # Отправляем запрос на backend для обновления подписки
    async with httpx.AsyncClient() as client:
        await client.post(API_URL, json={"telegram_id": user.id})
    await update.message.reply_text("Спасибо за оплату! Ваша подписка активирована.")

subscribe_handler = CommandHandler("subscribe", subscribe)
precheckout_handler = PreCheckoutQueryHandler(precheckout_callback)
successful_payment_handler = MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback) 