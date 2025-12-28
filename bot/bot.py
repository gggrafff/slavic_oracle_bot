from telegram.ext._handlers.messagehandler import MessageHandler
from bot.location import Location
from telegram.ext._handlers.commandhandler import CommandHandler
from telegram.ext._handlers.conversationhandler import ConversationHandler
from .menu import main_menu_location
import logging

from telegram import ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes, BaseHandler, filters

from utils import prepare_logging


prepare_logging()
logger = logging.getLogger()


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user if update.message else None
    logger.info("user %s canceled the conversation.", user.first_name if user else 'unknown')
    if update.message:
        await update.message.reply_text(
            "Bye! I hope you'll come back later.", reply_markup=ReplyKeyboardRemove()
        )

    return ConversationHandler.END


def create_fallbacks() -> list[BaseHandler[Update, ContextTypes.DEFAULT_TYPE, object]]:
    fallbacks: list[BaseHandler[Update, ContextTypes.DEFAULT_TYPE, object]]
    fallbacks = [CommandHandler("cancel", cancel)]
    logger.info(f"number of fallbacks: {len(fallbacks)}")
    return fallbacks


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Exception while handling an update:", exc_info=context.error)


async def handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Location:
    await main_menu_location.send_welcome_message(update, context)
    return main_menu_location


def create_entry_points() -> list[BaseHandler[Update, ContextTypes.DEFAULT_TYPE, object]]:
    entry_points: list[BaseHandler[Update, ContextTypes.DEFAULT_TYPE, object]]
    entry_points = [
        CommandHandler("start", handle_main_menu),
        *main_menu_location._handlers,
        MessageHandler(filters.Regex('.*'), handle_main_menu),
    ]
    logger.info(f"number of entry points: {len(entry_points)}")
    return entry_points


def create_states() -> dict[object, list[BaseHandler[Update, ContextTypes.DEFAULT_TYPE, object]]]:
    logger.info("states creating...")

    states: dict[object, list[BaseHandler[Update, ContextTypes.DEFAULT_TYPE, object]]] = {}
    main_menu_location.add_states(states)

    created_states: list[str] = []
    for k in states.keys():
        created_states.append(str(k))
    logger.info(f"number of states: {len(states)}")
    logger.info(f"created states: {created_states}")

    return states
