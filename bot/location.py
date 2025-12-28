"""
This package was taken from another project of mine as is,
so it might not perfectly match the current task, although it fulfills it.
"""

from typing import Sequence
import logging
from typing import Callable
from dataclasses import dataclass

from telegram import KeyboardButton, Message as TgMessage, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import MessageHandler, ContextTypes, BaseHandler, filters

from utils import chunks, prepare_logging, unique


prepare_logging()
logger = logging.getLogger()


@dataclass
class Message:
    text: str
    image_path: str | None = None


class Location:
    def __init__(
            self, name: str, handlers: list[MessageHandler[ContextTypes.DEFAULT_TYPE, object]],
            welcome_message: Message, keyboard: ReplyKeyboardMarkup | ReplyKeyboardRemove = ReplyKeyboardRemove(),
            is_implemented: bool = True,
            send_photo_separately: bool = False,
    ) -> None:
        self._name = name
        self._handlers = handlers
        self._welcome_message = welcome_message
        self._keyboard = keyboard
        self._is_implemented = is_implemented
        self._send_photo_separately = send_photo_separately

    def __str__(self) -> str:
        return f'Location "{self._name}"'

    async def send_welcome_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> TgMessage | None:
        if update.message:
            # If image_path is provided
            if self._welcome_message.image_path:
                if self._send_photo_separately:
                    # Send text and photo as two separate messages
                    await update.message.reply_photo(
                        photo=open(self._welcome_message.image_path, 'rb')
                    )
                    return await update.message.reply_text(
                        self._welcome_message.text,
                        reply_markup=self._keyboard,
                        parse_mode='HTML'
                    )
                else:
                    # Send photo with text as caption (default behavior)
                    return await update.message.reply_photo(
                        photo=open(self._welcome_message.image_path, 'rb'),
                        caption=self._welcome_message.text,
                        reply_markup=self._keyboard,
                        parse_mode='HTML'
                    )
            else:
                # Otherwise send regular text message
                return await update.message.reply_text(
                    self._welcome_message.text,
                    reply_markup=self._keyboard,
                    parse_mode='HTML'
                )
        return None

    def add_states(self, states: dict[object, list[BaseHandler[Update, ContextTypes.DEFAULT_TYPE, object]]]) -> None:
        if self not in states:
            states[self] = self._handlers  # type: ignore


class MenuLocation(Location):
    def __init__(
        self, name: str, welcome_message: Message = Message('Choose the menu'),
        send_photo_separately: bool = False,
    ) -> None:
        super().__init__(name, [], welcome_message, is_implemented=False, send_photo_separately=send_photo_separately)

    def __str__(self) -> str:
        return super().__str__()

    def add_children_buttons(self, children: list[Location], children_names: list[str] | None = None) -> None:
        self._children = children
        self._is_implemented = any([child._is_implemented for child in children])
        if not self._is_implemented:
            logger.info(f'{self} is not implemented')

        if children_names:
            children_names_actual = children_names
        else:
            children_names_actual = [child._name for child in children]
        children_buttons: list[str] = []
        for child, name in zip(children, children_names_actual):
            button_text = name
            if not child._is_implemented:
                logger.info(f'{name} is not implemented')
                button_text += " (soon)"
            children_buttons.append(button_text)

        async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> object:
            if update.message and update.message.text:
                for child, name in zip(children, children_buttons):
                    if name in update.message.text:
                        logger.info(f'user {update.message.from_user} entered the {child}')
                        await child.send_welcome_message(update, context)
                        return child
            else:
                logger.error('failed to check button name for children buttons')
            return None

        buttons_regex = '|'.join([f'^{button}$' for button in children_buttons])
        self._handlers = [MessageHandler(filters.Regex(buttons_regex), menu_handler)]

        logger.info(f"menu {self} has children buttons: {children_buttons}")
        buttons_layout = list(chunks(children_buttons, 3))
        self._keyboard = ReplyKeyboardMarkup(buttons_layout)

    def add_back_buttons(self, back_menus: list[Location], pre_text: str = 'Back to ') -> None:
        if not self._handlers:
            logger.error('back buttons added before children buttons')
            return

        back_buttons = [f'{pre_text}{menu._name}' for menu in unique(back_menus)]
        current_handler = self._handlers[-1].callback

        async def new_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> object:
            new_location = await current_handler(update, context)
            if new_location:
                return new_location

            if update.message and update.message.text:
                for back_menu, name in zip(back_menus, back_buttons):
                    if name in update.message.text:
                        await back_menu.send_welcome_message(update, context)
                        return back_menu
            else:
                logger.error('failed to check button name for back buttons')
            return None

        current_buttons = self._get_button_names()
        buttons_regex = '|'.join([f'^{button}$' for button in (current_buttons + back_buttons)])
        self._handlers = [MessageHandler(filters.Regex(buttons_regex), new_handler)]

        layout = self._get_button_layout()
        layout.append([KeyboardButton(name) for name in back_buttons])
        self._keyboard = ReplyKeyboardMarkup(layout)

    def add_func_button(self, button_text: str, func: Callable[[], Location], children: Sequence[Location]) -> None:
        self._children = list(children)
        self._is_implemented = any([child._is_implemented for child in children])
        if not self._is_implemented:
            logger.info(f'{self} is not implemented')

        async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> object:
            if update.message and update.message.text:
                if update.message.text == button_text:
                    logger.info(f'user {update.message.from_user} entered the {button_text}')
                    next_location = func()
                    await next_location.send_welcome_message(update, context)
                    return next_location
            else:
                logger.error('failed to check button name for func button')
            return None

        buttons_regex = f'^{button_text}$'
        self._handlers = [MessageHandler(filters.Regex(buttons_regex), menu_handler)]

        logger.info(f"menu {self} has func buttons: {buttons_regex}")
        buttons_layout = list(chunks([button_text], 3))
        self._keyboard = ReplyKeyboardMarkup(buttons_layout)

    def add_info_button(self, button_text: str, info_text: str) -> None:
        self._is_implemented = True

        current_handler = self._handlers[-1].callback

        async def new_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> object:
            new_location = await current_handler(update, context)
            if new_location:
                return new_location

            if update.message and update.message.text:
                if update.message.text == button_text:
                    logger.info(f'user {update.message.from_user} entered the {button_text}')
                    if update.effective_chat:
                        await context.bot.send_message(chat_id=update.effective_chat.id, text=info_text)
                    else:
                        logger.error('failed to send info message')
                    return self
            else:
                logger.error('failed to check button name for func button')
            return None

        current_buttons = self._get_button_names()
        buttons_regex = '|'.join([f'^{button}$' for button in (current_buttons + [button_text])])
        self._handlers = [MessageHandler(filters.Regex(buttons_regex), new_handler)]

        layout = self._get_button_layout()
        layout.append([KeyboardButton(button_text)])
        self._keyboard = ReplyKeyboardMarkup(layout)

        logger.info(f"menu {self} has info buttons: {buttons_regex}")

    def _get_button_names(self) -> list[str]:
        names: list[str] = []
        if isinstance(self._keyboard, ReplyKeyboardMarkup):
            for row in self._keyboard.keyboard:
                for button in row:
                    names.append(button.text)
        return names

    def _get_button_layout(self) -> list[list[KeyboardButton]]:
        layout: list[list[KeyboardButton]] = []
        if isinstance(self._keyboard, ReplyKeyboardMarkup):
            for row in self._keyboard.keyboard:
                layout.append([button for button in row])
        return layout

    def add_fallback(self, fallback_location: Location | None = None) -> None:
        if not self._handlers:
            logger.error('fallback added before another buttons')
            return

        current_handler = self._handlers[-1].callback

        async def new_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> object:
            new_location = await current_handler(update, context)
            if new_location:
                return new_location
            if update.message:
                await update.message.reply_text('Something went wrong. Try again.')
            new_location = fallback_location or self
            await new_location.send_welcome_message(update, context)
            return new_location

        self._handlers = [MessageHandler(filters.ALL, new_handler)]

    def add_states(self, states: dict[object, list[BaseHandler[Update, ContextTypes.DEFAULT_TYPE, object]]]) -> None:
        if self not in states:
            states[self] = self._handlers  # type: ignore
            for child in self._children:
                child.add_states(states)


class FuncLocation(Location):
    def __init__(self, name: str, text_func: Callable[[str], str] | None = None,
                 welcome_func: Callable[[], str] | None = None,
                 welcome_message: Message = Message('Input the data'),
                 error_message: Message = Message('Something went wrong. Try again.')) -> None:
        super().__init__(name, [], welcome_message)
        self._welcome_func = welcome_func
        self._text_func = text_func
        self._redirect: Location | None = None
        self._error_message = error_message

    def __str__(self) -> str:
        return super().__str__()

    def set_redirect(self, location: Location) -> None:
        logger.info(f'set redirect from {self} to {location}')
        self._redirect = location

    def prepare_handler(self) -> None:
        logger.info(f'preparing handler for {self}')
        if not self._redirect:
            logger.error(f'redirect is not set for {self}')

        async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> object:
            if update.message:
                try:
                    await update.message.reply_text(
                        self._text_func(update.message.text or "") if self._text_func else "Undefined handler",
                    )
                except Exception as e:
                    logger.error(f'error in {self} handler: {e}')
                    await update.message.reply_text(self._error_message.text)
            if self._redirect:
                await self._redirect.send_welcome_message(update, context)
            return self._redirect

        self._handlers = [MessageHandler(filters.ALL, handler)]
