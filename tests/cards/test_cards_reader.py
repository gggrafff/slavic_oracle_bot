import pytest
from pathlib import Path

from cards.cards_reader import CardsReader
from cards.card import Card


class TestCardsReader:
    """Test suite for CardsReader class."""

    @pytest.fixture
    def csv_path(self) -> Path:
        """Return path to the card descriptions CSV file."""
        # Path relative to project root
        return Path(__file__).parent.parent.parent / "cards" / "card_descriptions.csv"

    @pytest.fixture
    def reader(self, csv_path: Path) -> CardsReader:
        """Create a CardsReader instance."""
        return CardsReader(csv_path)

    def test_read_cards_returns_correct_cards(self, reader: CardsReader) -> None:
        """Test that reader parses the correct number of cards from CSV."""
        cards = reader.read_cards()

        assert isinstance(cards, list)
        assert all(isinstance(card, Card) for card in cards)
        assert len(cards) == 41, f"Expected 41 cards, but got {len(cards)}"
        for i, card in enumerate(cards, start=1):
            assert card.name, f"Card {i} has empty name"
            assert card.description, f"Card {i} has empty description"
            assert card.meaning, f"Card {i} has empty meaning"
            assert card.keywords, f"Card {i} has empty keywords"
            # image_path is expected to be empty (TODO)

    def test_first_card_has_correct_data(self, reader: CardsReader) -> None:
        """Test that the first card is parsed correctly."""
        cards = reader.read_cards()

        first_card = cards[0]
        assert first_card.name == "Лысая гора"
        assert "древнее место силы" in first_card.description
        assert "Встреча с тенью" in first_card.keywords
        assert first_card.image_path == ""  # TODO: not implemented yet

    def test_reader_with_nonexistent_file_raises_error(self) -> None:
        """Test that reader raises FileNotFoundError for non-existent file."""
        reader = CardsReader("nonexistent_file.csv")

        with pytest.raises(FileNotFoundError):
            reader.read_cards()
