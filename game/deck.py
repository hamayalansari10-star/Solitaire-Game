
import random

from game.card import Card


class Deck:

    def __init__(self):
        self.cards = []

        self.suits = [
            "Hearts",
            "Diamonds",
            "Clubs",
            "Spades"
        ]

        self.create_deck()

    def create_deck(self):

        self.cards = []

        for suit in self.suits:

            for rank in range(1, 14):

                card = Card(
                    suit=suit,
                    rank=rank,
                    face_up=False
                )

                self.cards.append(card)

    def shuffle(self):

        random.shuffle(self.cards)

    def deal_tableau(self):

        tableau = []

        for pile_number in range(1, 8):

            pile = []

            for i in range(pile_number):

                card = self.cards.pop()

                if i == pile_number - 1:
                    card.face_up = True

                pile.append(card)

            tableau.append(pile)

        return tableau

    def get_remaining_cards(self):

        return self.cards

    def show_deck_count(self):

        return len(self.cards)
