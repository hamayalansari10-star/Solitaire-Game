
import sys
from copy import deepcopy

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QMessageBox,
    QScrollArea,
    QSizePolicy,
)

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

from game.game_engine import GameEngine
from data_structures.stack import Stack


class MainWindow(QMainWindow):

    CARD_W = 78
    CARD_H = 108
    CARD_GAP = 30

    def __init__(self):
        super().__init__()

        self.game = GameEngine()

        self.undo_stack = Stack()
        self.redo_stack = Stack()

        self.selected = None
        self.moves = 0
        self.seconds = 0
        self.won_message_shown = False

        # Hint rotation
        self.hint_index = 0

        self.setWindowTitle("Klondike Solitaire")
        self.resize(1200, 850)
        self.setMinimumSize(950, 700)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #087a43;
            }

            QWidget {
                color: white;
                font-family: Arial;
            }
        """)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)

        self.build_ui()
        self.refresh_board()

        self.timer.start(1000)

    # =====================================
    # USER INTERFACE
    # =====================================

    def build_ui(self):

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(15, 12, 15, 12)
        main_layout.setSpacing(12)

        # TOP BAR

        top_bar = QHBoxLayout()

        title = QLabel("♠  SOLITAIRE")
        title.setFont(QFont("Arial", 23, QFont.Weight.Bold))

        self.score_label = QLabel("Score: 0")
        self.moves_label = QLabel("Moves: 0")
        self.time_label = QLabel("Time: 00:00")

        for label in (
            self.score_label,
            self.moves_label,
            self.time_label
        ):
            label.setFont(QFont("Arial", 11, QFont.Weight.Bold))

        top_bar.addWidget(title)
        top_bar.addStretch()
        top_bar.addWidget(self.score_label)
        top_bar.addSpacing(15)
        top_bar.addWidget(self.moves_label)
        top_bar.addSpacing(15)
        top_bar.addWidget(self.time_label)

        main_layout.addLayout(top_bar)

        # GAME BUTTONS

        button_bar = QHBoxLayout()
        button_bar.setSpacing(7)

        self.new_button = self.create_button("NEW GAME")
        self.undo_button = self.create_button("UNDO")
        self.redo_button = self.create_button("REDO")
        self.hint_button = self.create_button("HINT")
        self.auto_button = self.create_button("AUTO")
        self.draw_button = self.create_button("DRAW 1")
        self.draw3_button = self.create_button("DRAW 3")

        self.new_button.clicked.connect(self.new_game)
        self.undo_button.clicked.connect(self.undo_move)
        self.redo_button.clicked.connect(self.redo_move)
        self.hint_button.clicked.connect(self.show_hint)
        self.auto_button.clicked.connect(self.auto_move)

        self.draw_button.clicked.connect(
            lambda: self.set_draw_mode(1)
        )

        self.draw3_button.clicked.connect(
            lambda: self.set_draw_mode(3)
        )

        for button in (
            self.new_button,
            self.undo_button,
            self.redo_button,
            self.hint_button,
            self.auto_button,
            self.draw_button,
            self.draw3_button
        ):
            button_bar.addWidget(button)

        main_layout.addLayout(button_bar)

        # STOCK, WASTE AND FOUNDATIONS

        top_area = QHBoxLayout()
        top_area.setSpacing(12)

        self.stock_button = QPushButton()
        self.stock_button.setFixedSize(self.CARD_W, self.CARD_H)
        self.stock_button.clicked.connect(self.draw_card)

        self.waste_button = QPushButton()
        self.waste_button.setFixedSize(self.CARD_W, self.CARD_H)
        self.waste_button.clicked.connect(self.select_waste)

        top_area.addWidget(self.stock_button)
        top_area.addWidget(self.waste_button)
        top_area.addStretch()

        suits = ["Hearts", "Diamonds", "Clubs", "Spades"]

        self.foundation_buttons = {}

        for suit in suits:

            button = QPushButton()
            button.setFixedSize(self.CARD_W, self.CARD_H)

            button.clicked.connect(
                lambda checked=False, s=suit:
                self.move_to_foundation(s)
            )

            self.foundation_buttons[suit] = button
            top_area.addWidget(button)

        main_layout.addLayout(top_area)

        # STATUS

        self.status_label = QLabel(
            "Select a face-up card, then select its destination."
        )

        main_layout.addWidget(self.status_label)

        # TABLEAU SCROLL AREA

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setMinimumHeight(430)

        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #087a43;
                border: none;
            }

            QScrollBar:vertical {
                background: #075b35;
                width: 10px;
            }

            QScrollBar:handle:vertical {
                background: #c7e5d2;
                min-height: 25px;
            }

            QScrollBar:horizontal {
                background: #075b35;
                height: 10px;
            }

            QScrollBar:handle:horizontal {
                background: #c7e5d2;
            }
        """)

        self.tableau_content = QWidget()

        self.tableau_layout = QHBoxLayout(
            self.tableau_content
        )

        self.tableau_layout.setContentsMargins(3, 5, 3, 5)
        self.tableau_layout.setSpacing(13)

        self.tableau_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop |
            Qt.AlignmentFlag.AlignLeft
        )

        self.tableau_columns = []

        for i in range(7):

            column = QWidget()
            column.setFixedWidth(self.CARD_W)

            column.setSizePolicy(
                QSizePolicy.Policy.Fixed,
                QSizePolicy.Policy.Fixed
            )

            self.tableau_layout.addWidget(column)
            self.tableau_columns.append(column)

        self.scroll_area.setWidget(self.tableau_content)

        main_layout.addWidget(
            self.scroll_area,
            stretch=1
        )

        self.update_history_buttons()
        self.update_draw_buttons()

    # =====================================
    # BUTTON DESIGN
    # =====================================

    def create_button(self, text):

        button = QPushButton(text)
        button.setMinimumHeight(38)

        button.setStyleSheet("""
            QPushButton {
                background-color: #075b35;
                color: white;
                border: 1px solid #b8e0c7;
                padding: 6px;
                font-size: 11px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #0b9251;
            }

            QPushButton:disabled {
                background-color: #477c60;
                color: #c5d5cb;
            }
        """)

        return button

    # =====================================
    # DRAW MODE
    # =====================================

    def set_draw_mode(self, count):

        self.game.set_draw_mode(count)

        self.status_label.setText(
            f"Draw mode changed to Draw {count}."
        )

        self.update_draw_buttons()

    def update_draw_buttons(self):

        if self.game.draw_count == 1:

            self.draw_button.setStyleSheet("""
                QPushButton {
                    background-color: #e5c75e;
                    color: black;
                    border: 2px solid white;
                    padding: 6px;
                    font-size: 11px;
                    font-weight: bold;
                }
            """)

            self.draw3_button.setStyleSheet("""
                QPushButton {
                    background-color: #075b35;
                    color: white;
                    border: 1px solid #b8e0c7;
                    padding: 6px;
                    font-size: 11px;
                    font-weight: bold;
                }
            """)

        else:

            self.draw3_button.setStyleSheet("""
                QPushButton {
                    background-color: #e5c75e;
                    color: black;
                    border: 2px solid white;
                    padding: 6px;
                    font-size: 11px;
                    font-weight: bold;
                }
            """)

            self.draw_button.setStyleSheet("""
                QPushButton {
                    background-color: #075b35;
                    color: white;
                    border: 1px solid #b8e0c7;
                    padding: 6px;
                    font-size: 11px;
                    font-weight: bold;
                }
            """)

    # =====================================
    # CARD DISPLAY
    # =====================================

    def card_display_text(self, card):

        symbols = {
            "Hearts": "♥",
            "Diamonds": "♦",
            "Clubs": "♣",
            "Spades": "♠"
        }

        ranks = {
            1: "A",
            11: "J",
            12: "Q",
            13: "K"
        }

        rank = ranks.get(card.rank, str(card.rank))

        return f"{rank}\n{symbols[card.suit]}"

    def create_card_button(self, card, callback, selected=False):

        button = QPushButton()
        button.setFixedSize(self.CARD_W, self.CARD_H)

        if card.face_up:

            color = (
                "#d71932"
                if card.color == "Red"
                else "#111111"
            )

            border = (
                "3px solid #e5c75e"
                if selected
                else "1px solid #cccccc"
            )

            button.setText(self.card_display_text(card))

            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: #fffdf5;
                    color: {color};
                    border: {border};
                    font-size: 24px;
                    font-weight: bold;
                    text-align: center;
                }}
            """)

        else:

            button.setText("✥")

            button.setStyleSheet("""
                QPushButton {
                    background-color: #075b35;
                    color: white;
                    border: 2px solid #b8e0c7;
                    font-size: 30px;
                }
            """)

        button.clicked.connect(callback)

        return button

    # =====================================
    # UNDO AND REDO
    # =====================================

    def save_history(self):

        snapshot = (
            deepcopy(self.game),
            self.moves
        )

        self.undo_stack.push(snapshot)
        self.redo_stack = Stack()

        self.update_history_buttons()

    def update_history_buttons(self):

        self.undo_button.setEnabled(
            not self.undo_stack.is_empty()
        )

        self.redo_button.setEnabled(
            not self.redo_stack.is_empty()
        )

    def restore_snapshot(self, snapshot):

        self.game = snapshot[0]
        self.moves = snapshot[1]

        self.selected = None
        self.won_message_shown = False

        self.hint_index = 0

        self.update_draw_buttons()
        self.refresh_board()

        if not self.game.check_win():
            self.timer.start(1000)

    def undo_move(self):

        if self.undo_stack.is_empty():

            self.status_label.setText("Nothing to undo.")
            return

        current = (
            deepcopy(self.game),
            self.moves
        )

        self.redo_stack.push(current)

        previous = self.undo_stack.pop()

        self.restore_snapshot(previous)

        self.status_label.setText("Previous move restored.")

        self.update_history_buttons()

    def redo_move(self):

        if self.redo_stack.is_empty():

            self.status_label.setText("Nothing to redo.")
            return

        current = (
            deepcopy(self.game),
            self.moves
        )

        self.undo_stack.push(current)

        next_state = self.redo_stack.pop()

        self.restore_snapshot(next_state)

        self.status_label.setText("Move restored again.")

        self.update_history_buttons()

    # =====================================
    # REFRESH BOARD
    # =====================================

    def refresh_board(self):

        # STOCK

        if self.game.stock:

            self.stock_button.setText("✥")

            self.stock_button.setStyleSheet("""
                QPushButton {
                    background-color: #075b35;
                    color: white;
                    border: 2px solid #b8e0c7;
                    font-size: 30px;
                }
            """)

        else:

            self.stock_button.setText("↻")

            self.stock_button.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: white;
                    border: 2px dashed #b8e0c7;
                    font-size: 28px;
                }
            """)

        # WASTE

        if self.game.waste:

            card = self.game.waste[-1]

            color = (
                "#d71932"
                if card.color == "Red"
                else "#111111"
            )

            self.waste_button.setText(
                self.card_display_text(card)
            )

            self.waste_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: #fffdf5;
                    color: {color};
                    border: 1px solid #cccccc;
                    font-size: 24px;
                    font-weight: bold;
                }}
            """)

        else:

            self.waste_button.setText("WASTE")

            self.waste_button.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: white;
                    border: 2px dashed #b8e0c7;
                }
            """)

        # FOUNDATIONS

        symbols = {
            "Hearts": "♥",
            "Diamonds": "♦",
            "Clubs": "♣",
            "Spades": "♠"
        }

        for suit, button in self.foundation_buttons.items():

            pile = self.game.foundations[suit]

            if pile:

                card = pile[-1]

                color = (
                    "#d71932"
                    if card.color == "Red"
                    else "#111111"
                )

                button.setText(
                    self.card_display_text(card)
                )

                button.setStyleSheet(f"""
                    QPushButton {{
                        background-color: #fffdf5;
                        color: {color};
                        border: 1px solid #cccccc;
                        font-size: 24px;
                        font-weight: bold;
                    }}
                """)

            else:

                button.setText(symbols[suit])

                button.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        color: white;
                        border: 2px dashed #b8e0c7;
                        font-size: 30px;
                    }
                """)

        # TABLEAU

        max_cards = max(
            (len(pile) for pile in self.game.tableau),
            default=0
        )

        board_height = (
            self.CARD_H
            + max(0, max_cards - 1) * self.CARD_GAP
            + 180
        )

        for column in self.tableau_columns:

            for child in column.findChildren(QPushButton):
                child.deleteLater()

            column.setFixedHeight(board_height)

        self.tableau_content.setMinimumHeight(board_height)

        for index, pile in enumerate(self.game.tableau):

            column = self.tableau_columns[index]

            if not pile:

                empty = QPushButton("K", column)

                empty.setGeometry(
                    0, 0, self.CARD_W, self.CARD_H
                )

                empty.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        color: white;
                        border: 2px dashed #b8e0c7;
                        font-size: 25px;
                    }
                """)

                empty.clicked.connect(
                    lambda checked=False, i=index:
                    self.select_empty_column(i)
                )

                empty.show()

            for card_index, card in enumerate(pile):

                is_selected = (
                    self.selected is not None
                    and self.selected[0] == "tableau"
                    and self.selected[1] == index
                    and card_index >= self.selected[2]
                )

                button = self.create_card_button(
                    card,
                    lambda checked=False, i=index, ci=card_index:
                    self.select_tableau(i, ci),
                    is_selected
                )

                button.setParent(column)

                button.move(
                    0,
                    card_index * self.CARD_GAP
                )

                button.show()

        # SCORE AND MOVES

        self.score_label.setText(
            f"Score: {self.game.score}"
        )

        self.moves_label.setText(
            f"Moves: {self.moves}"
        )

        self.update_history_buttons()

        # WIN CONDITION

        if (
            self.game.check_win()
            and not self.won_message_shown
        ):

            self.won_message_shown = True
            self.timer.stop()

            QMessageBox.information(
                self,
                "You Win!",
                f"Congratulations!\n\n"
                f"Score: {self.game.score}\n"
                f"Moves: {self.moves}"
            )

    # =====================================
    # DRAW CARD
    # =====================================

    def draw_card(self):

        self.save_history()

        self.game.draw_from_stock()
        self.moves += 1

        self.hint_index = 0
        self.selected = None

        self.status_label.setText(
            f"Draw {self.game.draw_count}: Cards drawn."
        )

        self.refresh_board()

    # =====================================
    # SELECT WASTE
    # =====================================

    def select_waste(self):

        if not self.game.waste:
            return

        self.selected = ("waste", None, None)

        self.status_label.setText(
            "Waste card selected. Choose destination."
        )

        self.refresh_board()

    # =====================================
    # SELECT TABLEAU
    # =====================================

    def select_tableau(self, pile_index, card_index):

        pile = self.game.tableau[pile_index]

        if card_index >= len(pile):
            return

        card = pile[card_index]

        if not card.face_up:
            return

        if self.selected is None:

            self.selected = (
                "tableau",
                pile_index,
                card_index
            )

            self.status_label.setText(
                "Card selected. Choose destination."
            )

            self.refresh_board()
            return

        source_type, source_index, source_card_index = self.selected

        if (
            source_type == "tableau"
            and source_index == pile_index
        ):

            self.selected = (
                "tableau",
                pile_index,
                card_index
            )

            self.status_label.setText(
                "New card sequence selected."
            )

            self.refresh_board()
            return

        self.move_to_tableau(pile_index)

    # =====================================
    # MOVE TO TABLEAU
    # =====================================

    def move_to_tableau(self, target_index):

        if self.selected is None:
            return

        source_type, source_index, card_index = self.selected

        if source_type == "waste":

            if not self.game.waste:
                self.finish_move(False)
                return

            card = self.game.waste[-1]

            if not self.game.is_valid_tableau_move(
                card,
                self.game.tableau[target_index]
            ):

                self.finish_move(False)
                return

            self.save_history()

            success = self.game.move_waste_to_tableau(
                target_index
            )

        else:

            source = self.game.tableau[source_index]
            target = self.game.tableau[target_index]

            if source_index == target_index:

                self.selected = None
                self.refresh_board()
                return

            moving_cards = source[card_index:]

            if not moving_cards:
                self.finish_move(False)
                return

            valid = True

            for card in moving_cards:

                if not card.face_up:
                    valid = False
                    break

            for i in range(len(moving_cards) - 1):

                first = moving_cards[i]
                second = moving_cards[i + 1]

                if (
                    first.color == second.color
                    or first.rank != second.rank + 1
                ):

                    valid = False
                    break

            if (
                not valid
                or not self.game.is_valid_tableau_move(
                    moving_cards[0],
                    target
                )
            ):

                self.finish_move(False)
                return

            self.save_history()

            success = self.game.move_tableau_to_tableau(
                source_index,
                target_index,
                card_index
            )

        self.finish_move(success)

    # =====================================
    # EMPTY TABLEAU COLUMN
    # =====================================

    def select_empty_column(self, pile_index):

        if self.selected is None:
            return

        source_type, source_index, card_index = self.selected

        if source_type == "waste":

            if not self.game.waste:
                self.finish_move(False)
                return

            card = self.game.waste[-1]

            if not self.game.is_valid_tableau_move(
                card,
                self.game.tableau[pile_index]
            ):

                self.finish_move(False)
                return

            self.save_history()

            success = self.game.move_waste_to_tableau(
                pile_index
            )

        else:

            if source_index == pile_index:

                self.selected = None
                self.refresh_board()
                return

            moving_cards = self.game.tableau[source_index][card_index:]

            if not moving_cards or moving_cards[0].rank != 13:
                self.finish_move(False)
                return

            self.save_history()

            success = self.game.move_tableau_to_tableau(
                source_index,
                pile_index,
                card_index
            )

        self.finish_move(success)

    # =====================================
    # MOVE TO FOUNDATION
    # =====================================

    def move_to_foundation(self, suit):

        if self.selected is None:
            return

        source_type, source_index, card_index = self.selected

        success = False

        if source_type == "waste":

            if self.game.waste:

                card = self.game.waste[-1]

                if (
                    card.suit == suit
                    and self.game.is_valid_foundation_move(
                        card,
                        self.game.foundations[suit]
                    )
                ):

                    self.save_history()
                    success = self.game.move_waste_to_foundation()

        else:

            pile = self.game.tableau[source_index]

            if (
                pile
                and card_index == len(pile) - 1
                and pile[-1].suit == suit
                and self.game.is_valid_foundation_move(
                    pile[-1],
                    self.game.foundations[suit]
                )
            ):

                self.save_history()

                success = self.game.move_tableau_to_foundation(
                    source_index
                )

        self.finish_move(success)

    # =====================================
    # FINISH MOVE
    # =====================================

    def finish_move(self, success):

        if success:

            self.moves += 1
            self.hint_index = 0

            self.status_label.setText("Move successful.")

        else:

            self.status_label.setText("Invalid move.")

        self.selected = None
        self.refresh_board()

    # =====================================
    # HINT SYSTEM
    # =====================================

    def show_hint(self):

        possible_moves = []

        # -------------------------------------
        # 1. WASTE CARD MOVES
        # -------------------------------------

        if self.game.waste:

            card = self.game.waste[-1]

            # Waste to Tableau

            for i, pile in enumerate(self.game.tableau):

                if self.game.is_valid_tableau_move(card, pile):

                    possible_moves.append({
                        "type": "waste_tableau",
                        "target": i
                    })

            # Waste to Foundation

            if self.game.is_valid_foundation_move(
                card,
                self.game.foundations[card.suit]
            ):

                possible_moves.append({
                    "type": "waste_foundation",
                    "suit": card.suit
                })

        # -------------------------------------
        # 2. TABLEAU TO TABLEAU MOVES
        # -------------------------------------

        for source_index, source in enumerate(self.game.tableau):

            for card_index, card in enumerate(source):

                if not card.face_up:
                    continue

                moving_cards = source[card_index:]

                valid_sequence = True

                for i in range(len(moving_cards) - 1):

                    first = moving_cards[i]
                    second = moving_cards[i + 1]

                    if not (
                        first.face_up
                        and second.face_up
                        and first.color != second.color
                        and first.rank == second.rank + 1
                    ):

                        valid_sequence = False
                        break

                if not valid_sequence:
                    continue

                for target_index, target in enumerate(self.game.tableau):

                    if source_index == target_index:
                        continue

                    if self.game.is_valid_tableau_move(card, target):

                        possible_moves.append({
                            "type": "tableau_tableau",
                            "source": source_index,
                            "card_index": card_index,
                            "target": target_index
                        })

        # -------------------------------------
        # 3. TABLEAU TO FOUNDATION MOVES
        # -------------------------------------

        for source_index, pile in enumerate(self.game.tableau):

            if not pile:
                continue

            card = pile[-1]

            if self.game.is_valid_foundation_move(
                card,
                self.game.foundations[card.suit]
            ):

                possible_moves.append({
                    "type": "tableau_foundation",
                    "source": source_index,
                    "card_index": len(pile) - 1,
                    "suit": card.suit
                })

        # -------------------------------------
        # 4. CHECK IF MOVES EXIST
        # -------------------------------------

        if not possible_moves:

            self.selected = None

            if self.game.stock:
                message = (
                    "No direct moves available. "
                    "Try drawing cards from Stock."
                )

            elif self.game.waste:
                message = (
                    "No direct moves available. "
                    "Try recycling the Waste pile."
                )

            else:
                message = "No possible moves available."

            self.status_label.setText(message)
            self.refresh_board()
            return

        # -------------------------------------
        # 5. ROTATE HINTS
        # -------------------------------------

        self.hint_index %= len(possible_moves)

        hint = possible_moves[self.hint_index]

        self.hint_index += 1

        self.selected = None

        # -------------------------------------
        # 6. SHOW WASTE TO TABLEAU HINT
        # -------------------------------------

        if hint["type"] == "waste_tableau":

            target = hint["target"]

            self.selected = ("waste", None, None)

            message = (
                f"Hint: Move Waste card to "
                f"Column {target + 1}."
            )

        # -------------------------------------
        # 7. SHOW WASTE TO FOUNDATION HINT
        # -------------------------------------

        elif hint["type"] == "waste_foundation":

            suit = hint["suit"]

            self.selected = ("waste", None, None)

            message = (
                f"Hint: Move Waste card to "
                f"{suit} Foundation."
            )

        # -------------------------------------
        # 8. SHOW TABLEAU TO TABLEAU HINT
        # -------------------------------------

        elif hint["type"] == "tableau_tableau":

            source = hint["source"]
            target = hint["target"]
            card_index = hint["card_index"]

            self.selected = (
                "tableau",
                source,
                card_index
            )

            message = (
                f"Hint: Move selected sequence from "
                f"Column {source + 1} to "
                f"Column {target + 1}."
            )

        # -------------------------------------
        # 9. SHOW TABLEAU TO FOUNDATION HINT
        # -------------------------------------

        else:

            source = hint["source"]
            suit = hint["suit"]
            card_index = hint["card_index"]

            self.selected = (
                "tableau",
                source,
                card_index
            )

            message = (
                f"Hint: Move Column {source + 1} "
                f"card to {suit} Foundation."
            )

        self.status_label.setText(message)

        self.refresh_board()

    # =====================================
    # AUTO MOVE
    # =====================================

    def auto_move(self):

        moved = False

        if self.game.waste:

            card = self.game.waste[-1]

            if self.game.is_valid_foundation_move(
                card,
                self.game.foundations[card.suit]
            ):

                self.save_history()

                moved = self.game.move_waste_to_foundation()

        if not moved:

            for index, pile in enumerate(self.game.tableau):

                if not pile:
                    continue

                card = pile[-1]

                if self.game.is_valid_foundation_move(
                    card,
                    self.game.foundations[card.suit]
                ):

                    self.save_history()

                    moved = self.game.move_tableau_to_foundation(
                        index
                    )

                    if moved:
                        break

        if moved:

            self.moves += 1
            self.hint_index = 0

            self.status_label.setText(
                "Card moved to foundation."
            )

        else:

            self.status_label.setText(
                "No automatic move available."
            )

        self.selected = None
        self.refresh_board()

    # =====================================
    # NEW GAME
    # =====================================

    def new_game(self):

        self.game.new_game()

        self.undo_stack = Stack()
        self.redo_stack = Stack()

        self.selected = None
        self.moves = 0
        self.seconds = 0
        self.won_message_shown = False

        self.hint_index = 0

        self.timer.start(1000)

        self.time_label.setText("Time: 00:00")

        self.status_label.setText("New game started.")

        self.update_draw_buttons()
        self.refresh_board()

    # =====================================
    # TIMER
    # =====================================

    def update_timer(self):

        self.seconds += 1

        minutes = self.seconds // 60
        seconds = self.seconds % 60

        self.time_label.setText(
            f"Time: {minutes:02d}:{seconds:02d}"
        )


# =====================================
# RUN GAME
# =====================================

if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
