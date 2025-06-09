import asyncio
import logging

from telegram.ext import Application

from bot.config import TOKEN
from bot.handlers.generate import generate_handler
from bot.handlers.start import start_handler
from bot.handlers.subscribe import subscribe_handler, precheckout_handler, successful_payment_handler

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def main() -> None:
    """Start the bot."""
    application = Application.builder().token(TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(start_handler)
    application.add_handler(generate_handler)
    application.add_handler(subscribe_handler)
    application.add_handler(precheckout_handler)
    application.add_handler(successful_payment_handler)

    # Run the bot until the user presses Ctrl-C
    await application.run_polling()


if __name__ == "__main__":
    asyncio.run(main()) 