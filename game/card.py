
from dataclasses import dataclass


@dataclass
class Card:
    suit: str
    rank: int
    face_up: bool = False

    @property
    def color(self):
        if self.suit in ["Hearts", "Diamonds"]:
            return "Red"
        return "Black"

    def get_rank_name(self):
        names = {
            1: "A",
            11: "J",
            12: "Q",
            13: "K"
        }

        return names.get(self.rank, str(self.rank))

    def __str__(self):
        if not self.face_up:
            return "[Hidden]"

        symbols = {
            "Hearts": "♥",
            "Diamonds": "♦",
            "Clubs": "♣",
            "Spades": "♠"
        }

        return f"{self.get_rank_name()}{symbols[self.suit]}"
