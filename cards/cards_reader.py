import csv
from pathlib import Path
from typing import List

from cards.card import Card


class CardsReader:
    """Reads card descriptions from CSV file and converts them to Card objects."""

    def __init__(self, csv_path: str | Path, images_dir: str | Path | None = None):
        """
        Initialize the CardsReader with path to CSV file.

        Args:
            csv_path: Path to the CSV file containing card descriptions
            images_dir: Path to directory with card images (default: cards/images relative to CSV)
        """
        self.csv_path = Path(csv_path)
        if images_dir is None:
            # Default: images directory next to CSV file
            self.images_dir = self.csv_path.parent / "images"
        else:
            self.images_dir = Path(images_dir)

    def _find_image_for_card(self, card_name: str) -> str:
        """
        Find image file for a card by its name.

        Args:
            card_name: Name of the card

        Returns:
            Relative path to the image file

        Raises:
            FileNotFoundError: If no matching image file is found
        """
        if not self.images_dir.exists():
            raise FileNotFoundError(f"Images directory not found: {self.images_dir}")

        # Common image extensions to search for
        supported_extensions = ['.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG']

        # Try to find file with exact card name and any supported extension
        for ext in supported_extensions:
            image_path = self.images_dir / f"{card_name}{ext}"
            if image_path.exists():
                # Return path relative to CSV file location
                return str(image_path.relative_to(self.csv_path.parent.parent))

        # If not found, raise an exception
        raise FileNotFoundError(
            f"Image file not found for card '{card_name}'. "
            f"Searched in {self.images_dir} with extensions: {supported_extensions}"
        )

    def read_cards(self) -> List[Card]:
        """
        Read cards from CSV file and convert to list of Card objects.

        Returns:
            List of Card objects parsed from the CSV file

        Raises:
            FileNotFoundError: If the CSV file doesn't exist or image not found
            ValueError: If CSV file has invalid format
        """
        if not self.csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {self.csv_path}")

        cards = []

        with open(self.csv_path, 'r', encoding='utf-8') as csvfile:
            # Read CSV with proper handling of quotes and multiline fields
            reader = csv.DictReader(csvfile)

            for row_num, row in enumerate(reader, start=2):  # start=2 because row 1 is header
                try:
                    # Extract fields from CSV row
                    # Column names from CSV: Название, Описание (основной текст),
                    # Совет (толкование карты), Ключевое значение (слова, словосочетания)
                    name = row['Название'].strip()
                    description = row['Описание (основной текст)'].strip()
                    meaning = row['Совет (толкование карты)'].strip()
                    keywords = row['Ключевое значение (слова, словосочетания)'].strip()

                    # Find corresponding image file for this card
                    try:
                        image_path = self._find_image_for_card(name)
                    except FileNotFoundError as e:
                        raise ValueError(f"Error at row {row_num}: {e}")

                    card = Card(
                        name=name,
                        description=description,
                        meaning=meaning,
                        keywords=keywords,
                        image_path=image_path
                    )

                    cards.append(card)

                except KeyError as e:
                    raise ValueError(
                        f"Invalid CSV format at row {row_num}: missing column {e}"
                    )
                except Exception as e:
                    raise ValueError(
                        f"Error parsing row {row_num}: {e}"
                    )

        return cards
