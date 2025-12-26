from cards.card import Card
from cards.cards_reader import CardsReader
import random
from bot.location import MenuLocation

main_menu_location = MenuLocation(
    name='Главное меню',
    welcome_message='Это оракул. Тяни карту и получи предсказание.'
)


def create_card_locations(cards: list[Card]) -> list[MenuLocation]:
    locations: list[MenuLocation] = []
    for card in cards:
        location = MenuLocation(
            name=card.name,
            welcome_message=card.name + '\n\n' + card.description + '\n\n' + card.meaning,
        )
        locations.append(location)
    return locations


def add_buttons_to_card_locations(locations: list[MenuLocation]) -> None:
    for location in locations:
        location.add_func_button('Взять ещё одну карту', lambda: random.choice(locations), locations)
        location.add_back_buttons([main_menu_location])


cards = CardsReader('cards/card_descriptions.csv').read_cards()
card_locations = create_card_locations(cards)
add_buttons_to_card_locations(card_locations)

main_menu_location.add_func_button('Взять карту', lambda: random.choice(card_locations), card_locations)
