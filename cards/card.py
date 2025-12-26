from dataclasses import dataclass


@dataclass
class Card:
    name: str
    description: str
    meaning: str
    keywords: str
    image_path: str
