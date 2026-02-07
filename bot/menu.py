from collections import deque
from typing import TYPE_CHECKING

from cards.card import Card
from cards.cards_reader import CardsReader
import random
from bot.location import MenuLocation, Message

if TYPE_CHECKING:
    from telegram.ext import ContextTypes

# How many draws before a card can repeat for the same user
CARD_HISTORY_SIZE = 5

main_menu_location = MenuLocation(
    name='Главное меню',
    welcome_message=Message('Это оракул. Тяни карту и получи предсказание.')
)


def create_card_locations(cards: list[Card]) -> list[MenuLocation]:
    locations: list[MenuLocation] = []
    for card in cards:
        # Create message with card text and image path
        # Wrap meaning in spoiler tag so user can reveal it when ready
        card_text = '<b>' + card.name + '</b>' + \
            '\n\n' + card.description + \
            '\n\n' + 'Толкование:\n<span class="tg-spoiler">' + \
            card.meaning + '</span>'
        welcome_message = Message(text=card_text, image_path=card.image_path)

        location = MenuLocation(
            name=card.name,
            welcome_message=welcome_message,
            send_photo_separately=True  # Send text and photo separately to avoid cropping
        )
        locations.append(location)
    return locations


def get_card_with_history(context: 'ContextTypes.DEFAULT_TYPE', all_cards: list[MenuLocation]) -> MenuLocation:
    """Select a card that hasn't been drawn in the last CARD_HISTORY_SIZE draws for this user."""
    # Get or create history deque for this user
    if 'card_history' not in context.user_data:
        context.user_data['card_history'] = deque(maxlen=CARD_HISTORY_SIZE)
    history: deque[str] = context.user_data['card_history']
    
    # Get cards not in recent history
    available = [c for c in all_cards if c._name not in history]
    if not available:
        # Fallback if all cards are in history (shouldn't happen with enough cards)
        available = all_cards
    
    card = random.choice(available)
    history.append(card._name)
    return card


def add_buttons_to_card_locations(locations: list[MenuLocation]) -> None:
    for location in locations:
        location.add_func_button_with_context(
            'Взять ещё одну карту',
            lambda ctx: get_card_with_history(ctx, locations),
            locations
        )
        location.add_back_buttons([main_menu_location], pre_text='Вернуться в ')


cards = CardsReader('cards/card_descriptions.csv', 'cards/images').read_cards()
card_locations = create_card_locations(cards)
add_buttons_to_card_locations(card_locations)

main_menu_location.add_func_button_with_context(
    'Взять карту',
    lambda ctx: get_card_with_history(ctx, card_locations),
    card_locations
)
main_menu_location.add_info_button('О нас', """Всем привет! Мы команда из четырех иллюстраторов🍄

Kinoko House Illustrators — дом, где рождаются рисунки, идеи и новые проекты. \
Здесь мы рассказываем о создании иллюстрации от первых штрихов до готовых работ \
и делимся тем, что вдохновляет нас в искусстве.

https://t.me/kinoko_house""")
