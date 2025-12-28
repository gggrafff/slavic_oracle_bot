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
            # image_path should now be populated
            assert card.image_path, f"Card {i} has empty image_path"

    def test_first_card_has_correct_data(self, reader: CardsReader) -> None:
        """Test that the first card is parsed correctly."""
        cards = reader.read_cards()

        first_card = cards[0]
        assert first_card.name == "Лысая гора"
        assert "древнее место силы" in first_card.description
        assert "Встреча с тенью" in first_card.keywords
        # Check that image_path is populated and points to images directory
        assert first_card.image_path
        assert "images" in first_card.image_path
        assert first_card.name in first_card.image_path

    def test_reader_with_nonexistent_file_raises_error(self) -> None:
        """Test that reader raises FileNotFoundError for non-existent file."""
        reader = CardsReader("nonexistent_file.csv")

        with pytest.raises(FileNotFoundError):
            reader.read_cards()

    def test_reader_with_custom_images_dir(self, csv_path: Path) -> None:
        """Test that reader works with custom images directory."""
        images_dir = csv_path.parent / "images"
        reader = CardsReader(csv_path, images_dir=images_dir)
        cards = reader.read_cards()

        assert len(cards) > 0
        # All cards should have image paths
        for card in cards:
            assert card.image_path

    def test_reader_with_missing_images_dir(self, csv_path: Path) -> None:
        """Test that reader raises error when images directory doesn't exist."""
        reader = CardsReader(csv_path, images_dir="/nonexistent/images")

        with pytest.raises(ValueError, match="Images directory not found"):
            reader.read_cards()

    def test_image_path_format(self, reader: CardsReader) -> None:
        """Test that image paths have correct format."""
        cards = reader.read_cards()

        for card in cards:
            # Path should be relative and contain images directory
            assert not card.image_path.startswith('/')
            assert 'images' in card.image_path
            # Should have an image extension
            assert any(
                card.image_path.lower().endswith(ext)
                for ext in ['.png', '.jpg', '.jpeg']
            )
