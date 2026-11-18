
from game.card import Card
from game.deck import Deck

from data_structures.queue import Queue
from data_structures.linked_list import LinkedList
from data_structures.card_map import CardMap


class GameEngine:

    def __init__(self):
        self.draw_count = 1
        self.new_game()

    # =========================================
    # NEW GAME
    # =========================================
    def new_game(self):

        self.deck = Deck()
        self.deck.shuffle()

        self.tableau = self.deck.deal_tableau()
        self.stock = self.deck.get_remaining_cards()

        self.waste = []

        self.foundations = {
            "Hearts": [],
            "Diamonds": [],
            "Clubs": [],
            "Spades": []
        }

        self.score = 0

        # Queue
        self.action_queue = Queue()

        # Linked List
        self.move_history = LinkedList()

        # CardMap
        self.card_map = CardMap()

        # Track all 52 cards
        self.refresh_card_map()

    # =========================================
    # CARD MAP
    # =========================================
    def refresh_card_map(self):

        self.card_map.clear()

        # Stock cards
        for card in self.stock:
            self.card_map.add(card, "Stock")

        # Waste cards
        for card in self.waste:
            self.card_map.add(card, "Waste")

        # Tableau cards
        for index, pile in enumerate(self.tableau):

            for card in pile:
                self.card_map.add(
                    card,
                    f"Tableau {index + 1}"
                )

        # Foundation cards
        for suit, pile in self.foundations.items():

            for card in pile:
                self.card_map.add(
                    card,
                    f"Foundation {suit}"
                )

    def get_card_location(self, card):

        return self.card_map.get(card)

    def get_card_map_size(self):

        return self.card_map.size()

    # =========================================
    # QUEUE: ACTION HISTORY
    # =========================================
    def record_action(self, action):

        self.action_queue.enqueue(action)

    def get_action_history(self):

        return self.action_queue.get_all()

    def process_next_action(self):

        return self.action_queue.dequeue()

    def clear_action_history(self):

        self.action_queue.clear()

    # =========================================
    # LINKED LIST: MOVE HISTORY
    # =========================================
    def record_move(self, move):

        self.move_history.append(move)

    def get_move_history(self):

        return self.move_history.get_all()

    def get_last_move(self):

        return self.move_history.get_last()

    def remove_last_move(self):

        return self.move_history.remove_last()

    # =========================================
    # DRAW MODE
    # =========================================
    def set_draw_mode(self, count):

        if count not in (1, 3):
            return False

        self.draw_count = count

        self.record_action(
            f"Draw mode changed to Draw {count}"
        )

        return True

    # =========================================
    # COUNT ALL CARDS
    # =========================================
    def count_all_cards(self):

        total = len(self.stock) + len(self.waste)

        for pile in self.foundations.values():
            total += len(pile)

        for pile in self.tableau:
            total += len(pile)

        return total

    # =========================================
    # DRAW FROM STOCK
    # =========================================
    def draw_from_stock(self):

        if self.stock:

            last_drawn_card = None

            for _ in range(self.draw_count):

                if not self.stock:
                    break

                card = self.stock.pop()
                card.face_up = True

                self.waste.append(card)

                self.record_action(
                    f"Drew {card}"
                )

                last_drawn_card = card

            self.refresh_card_map()

            return last_drawn_card

        # Recycle waste
        elif self.waste:

            recycled_count = len(self.waste)

            while self.waste:

                card = self.waste.pop()
                card.face_up = False

                self.stock.append(card)

            self.record_action(
                f"Recycled {recycled_count} cards into stock"
            )

            self.refresh_card_map()

            return None

        return None

    # =========================================
    # VALID TABLEAU MOVE
    # =========================================
    def is_valid_tableau_move(self, card, target_pile):

        if not card.face_up:
            return False

        if not target_pile:
            return card.rank == 13

        top_card = target_pile[-1]

        return (
            top_card.face_up
            and card.color != top_card.color
            and card.rank == top_card.rank - 1
        )

    # =========================================
    # WASTE TO TABLEAU
    # =========================================
    def move_waste_to_tableau(self, pile_index):

        if not self.waste:
            return False

        if not 0 <= pile_index < len(self.tableau):
            return False

        card = self.waste[-1]
        target_pile = self.tableau[pile_index]

        if self.is_valid_tableau_move(card, target_pile):

            moved_card = self.waste.pop()
            target_pile.append(moved_card)

            self.score += 5

            move = (
                f"{moved_card}: Waste to Tableau "
                f"{pile_index + 1}"
            )

            self.record_move(move)
            self.record_action(move)

            self.refresh_card_map()

            return True

        return False

    # =========================================
    # WASTE TO FOUNDATION
    # =========================================
    def move_waste_to_foundation(self):

        if not self.waste:
            return False

        card = self.waste[-1]
        foundation = self.foundations[card.suit]

        if self.is_valid_foundation_move(card, foundation):

            moved_card = self.waste.pop()
            foundation.append(moved_card)

            self.score += 10

            move = f"{moved_card}: Waste to Foundation"

            self.record_move(move)
            self.record_action(move)

            self.refresh_card_map()

            return True

        return False

    # =========================================
    # VALID FOUNDATION MOVE
    # =========================================
    def is_valid_foundation_move(self, card, foundation):

        if not card.face_up:
            return False

        if not foundation:
            return card.rank == 1

        top_card = foundation[-1]

        return (
            card.suit == top_card.suit
            and card.rank == top_card.rank + 1
        )

    # =========================================
    # TABLEAU TO TABLEAU
    # =========================================
    def move_tableau_to_tableau(
        self,
        source_index,
        target_index,
        source_card_index=None
    ):

        if source_index == target_index:
            return False

        if not (0 <= source_index < len(self.tableau)):
            return False

        if not (0 <= target_index < len(self.tableau)):
            return False

        source = self.tableau[source_index]
        target = self.tableau[target_index]

        if not source:
            return False

        face_up_indices = [
            i for i, card in enumerate(source)
            if card.face_up
        ]

        if not face_up_indices:
            return False

        if source_card_index is not None:
            moving_index = source_card_index
        else:
            moving_index = face_up_indices[-1]

        if not 0 <= moving_index < len(source):
            return False

        moving_card = source[moving_index]

        if not moving_card.face_up:
            return False

        if not self.is_valid_tableau_move(moving_card, target):
            return False

        cards_to_move = source[moving_index:]

        # Validate complete sequence
        for i in range(len(cards_to_move) - 1):

            upper_card = cards_to_move[i]
            lower_card = cards_to_move[i + 1]

            if not (
                upper_card.face_up
                and lower_card.face_up
                and upper_card.color != lower_card.color
                and upper_card.rank == lower_card.rank + 1
            ):
                return False

        moved_cards = [str(card) for card in cards_to_move]

        # Move cards
        for _ in range(len(cards_to_move)):
            target.append(source.pop(moving_index))

        # Flip newly exposed card
        if source and not source[-1].face_up:

            source[-1].face_up = True
            self.score += 5

        move = (
            f"{moved_cards}: Tableau {source_index + 1} "
            f"to Tableau {target_index + 1}"
        )

        self.record_move(move)
        self.record_action(move)

        self.refresh_card_map()

        return True

    # =========================================
    # TABLEAU TO FOUNDATION
    # =========================================
    def move_tableau_to_foundation(self, pile_index):

        if not 0 <= pile_index < len(self.tableau):
            return False

        source = self.tableau[pile_index]

        if not source:
            return False

        card = source[-1]

        if not card.face_up:
            return False

        foundation = self.foundations[card.suit]

        if self.is_valid_foundation_move(card, foundation):

            moved_card = source.pop()
            foundation.append(moved_card)

            self.score += 10

            if source and not source[-1].face_up:

                source[-1].face_up = True
                self.score += 5

            move = (
                f"{moved_card}: Tableau {pile_index + 1} "
                f"to Foundation"
            )

            self.record_move(move)
            self.record_action(move)

            self.refresh_card_map()

            return True

        return False

    # =========================================
    # WINNING CONDITION
    # =========================================
    def check_win(self):

        total_cards = sum(
            len(pile) for pile in self.foundations.values()
        )

        return total_cards == 52

    # =========================================
    # GAME STATUS
    # =========================================
    def show_status(self):

        print("\n========== GAME STATUS ==========")

        print("Score:", self.score)
        print("Draw Mode:", self.draw_count)
        print("Stock:", len(self.stock))
        print("Waste:", len(self.waste))

        print("\nTableau:")

        for i, pile in enumerate(self.tableau):
            print(
                f"Column {i + 1}:",
                [str(card) for card in pile]
            )

        print("\nFoundations:")

        for suit, pile in self.foundations.items():
            print(suit, [str(card) for card in pile])

        print("\nQueue - Action History:")

        for action in self.get_action_history():
            print(action)

        print("\nLinked List - Move History:")

        for move in self.get_move_history():
            print(move)

        print("\nCardMap Size:", self.get_card_map_size())

        print("\nTotal Cards:", self.count_all_cards())
        print("You Won:", self.check_win())
