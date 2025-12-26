import csv
from pathlib import Path
from typing import List

from cards.card import Card


class CardsReader:
    """Reads card descriptions from CSV file and converts them to Card objects."""

    def __init__(self, csv_path: str | Path):
        """
        Initialize the CardsReader with path to CSV file.

        Args:
            csv_path: Path to the CSV file containing card descriptions
        """
        self.csv_path = Path(csv_path)

    def read_cards(self) -> List[Card]:
        """
        Read cards from CSV file and convert to list of Card objects.

        Returns:
            List of Card objects parsed from the CSV file

        Raises:
            FileNotFoundError: If the CSV file doesn't exist
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

                    # TODO: Add image_path mapping logic
                    # For now, leaving it empty as requested
                    image_path = ""

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
