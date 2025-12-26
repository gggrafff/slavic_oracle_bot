from bot.bot import error_handler
from bot.bot import create_fallbacks
from bot.bot import create_entry_points
from bot.bot import create_states
import logging
import argparse

from telegram import Update
from telegram.ext import (
    Application,
    ConversationHandler,
)

from utils import prepare_logging
prepare_logging()
logger = logging.getLogger()


def main() -> None:
    logger.info("slavic oracle bot starting ...")
    parser = argparse.ArgumentParser(description='SlavicOracle telegram bot, metaphorical cards')
    parser.add_argument('token', type=str, help='Telegram bot token')
    args = parser.parse_args()

    logger.info("conversation preparing...")
    application = Application.builder().token(args.token).build()
    conv_handler = ConversationHandler(
        entry_points=create_entry_points(),
        states=create_states(),
        fallbacks=create_fallbacks(),
    )
    application.add_handler(conv_handler)
    application.add_error_handler(error_handler)

    logger.info("run polling...")
    application.run_polling(allowed_updates=Update.ALL_TYPES, bootstrap_retries=-1)
    logger.info("slavic oracle bot finished")


if __name__ == "__main__":
    main()
