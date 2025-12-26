import pytest

from cards.card import Card
from bot.menu import create_card_locations, add_buttons_to_card_locations
from bot.location import MenuLocation


class TestMenuFunctions:
    """Test suite for menu.py functions."""

    @pytest.fixture
    def sample_cards(self) -> list[Card]:
        """Create sample cards for testing."""
        return [
            Card(
                name="Лысая гора",
                description="Древнее место силы",
                meaning="Встреча с тенью",
                keywords="Испытание, очищение",
                image_path=""
            ),
            Card(
                name="Птица Гамаюн",
                description="Вещая птица",
                meaning="Мудрость",
                keywords="Знание, правда",
                image_path=""
            ),
            Card(
                name="Русалка",
                description="Дух природы",
                meaning="Шалость",
                keywords="Неприятности",
                image_path=""
            )
        ]

    def test_create_card_locations_returns_correct_count(self, sample_cards: list[Card]) -> None:
        """Test that create_card_locations returns the correct number of locations."""
        locations = create_card_locations(sample_cards)

        assert len(locations) == len(sample_cards)

    def test_create_card_locations_returns_menu_locations(self, sample_cards: list[Card]) -> None:
        """Test that create_card_locations returns MenuLocation instances."""
        locations = create_card_locations(sample_cards)

        assert all(isinstance(loc, MenuLocation) for loc in locations)

    def test_create_card_locations_sets_correct_names(self, sample_cards: list[Card]) -> None:
        """Test that locations have correct names from cards."""
        locations = create_card_locations(sample_cards)

        for card, location in zip(sample_cards, locations):
            assert location._name == card.name

    def test_create_card_locations_creates_welcome_message(self, sample_cards: list[Card]) -> None:
        """Test that welcome messages contain card information."""
        locations = create_card_locations(sample_cards)

        for card, location in zip(sample_cards, locations):
            assert card.name in location._welcome_message
            assert card.description in location._welcome_message
            assert card.meaning in location._welcome_message

    def test_create_card_locations_with_empty_list(self) -> None:
        """Test that create_card_locations handles empty list."""
        locations = create_card_locations([])

        assert locations == []

    def test_add_buttons_to_card_locations_adds_handlers(self, sample_cards: list[Card]) -> None:
        """Test that add_buttons_to_card_locations adds handlers to locations."""
        locations = create_card_locations(sample_cards)

        # Before adding buttons, handlers should be empty
        for location in locations:
            assert location._handlers == []

        add_buttons_to_card_locations(locations)

        # After adding buttons, handlers should be present
        for location in locations:
            assert len(location._handlers) > 0

    def test_add_buttons_to_card_locations_adds_keyboard(self, sample_cards: list[Card]) -> None:
        """Test that add_buttons_to_card_locations adds keyboard to locations."""
        locations = create_card_locations(sample_cards)
        add_buttons_to_card_locations(locations)

        # All locations should have keyboards
        for location in locations:
            assert location._keyboard is not None

    def test_add_buttons_to_card_locations_with_empty_list(self) -> None:
        """Test that add_buttons_to_card_locations handles empty list."""
        # Should not raise an error
        add_buttons_to_card_locations([])
