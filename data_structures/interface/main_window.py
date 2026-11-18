
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
    CARD_GAP = 29

    def __init__(self):
        super().__init__()

        self.game = GameEngine()

        self.undo_stack = Stack()
        self.redo_stack = Stack()

        self.selected = None
        self.moves = 0
        self.seconds = 0
        self.won_message_shown = False

        self.setWindowTitle("Solitaire - Klondike")
        self.setMinimumSize(1100, 760)
        self.resize(1360, 850)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #075b3b;
            }

            QWidget {
                color: white;
                font-family: Arial;
            }

            QPushButton {
                font-family: Arial;
                font-weight: bold;
            }
        """)

        self.build_ui()
        self.refresh_board()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)

    # ==========================================
    # USER INTERFACE
    # ==========================================

    def build_ui(self):

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(22, 15, 22, 16)
        main_layout.setSpacing(13)

        # TOP HEADER

        top_bar = QHBoxLayout()

        title = QLabel("♠  SOLITAIRE")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))

        self.score_label = QLabel("SCORE: 0")
        self.moves_label = QLabel("MOVES: 0")
        self.time_label = QLabel("TIME: 00:00")

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

        # UNDO / REDO

        history_bar = QHBoxLayout()
        history_bar.setSpacing(8)

        self.undo_button = self.create_history_button(
            "UNDO (undo_move)"
        )

        self.redo_button = self.create_history_button(
            "REDO (redo_move)"
        )

        self.undo_button.clicked.connect(self.undo_move)
        self.redo_button.clicked.connect(self.redo_move)

        self.undo_button.setEnabled(False)
        self.redo_button.setEnabled(False)

        history_bar.addWidget(self.undo_button)
        history_bar.addWidget(self.redo_button)
        history_bar.addStretch()

        main_layout.addLayout(history_bar)

        # STOCK, WASTE, FOUNDATIONS

        top_area = QHBoxLayout()
        top_area.setSpacing(14)

        self.stock_button = QPushButton()
        self.stock_button.setFixedSize(
            self.CARD_W, self.CARD_H
        )
        self.stock_button.clicked.connect(self.draw_card)

        self.waste_button = QPushButton()
        self.waste_button.setFixedSize(
            self.CARD_W, self.CARD_H
        )
        self.waste_button.clicked.connect(self.select_waste)

        top_area.addWidget(self.stock_button)
        top_area.addWidget(self.waste_button)
        top_area.addStretch()

        self.foundation_buttons = {}

        for suit in ["Hearts", "Diamonds", "Clubs", "Spades"]:

            button = QPushButton()
            button.setFixedSize(
                self.CARD_W, self.CARD_H
            )

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

        self.status_label.setStyleSheet(
            "color: #e2e9df; font-size: 12px;"
        )

        main_layout.addWidget(self.status_label)

        # DRAW MODE BUTTONS

        draw_mode_bar = QHBoxLayout()
        draw_mode_bar.setSpacing(8)

        self.draw1_button = self.create_history_button("DRAW 1")
        self.draw3_button = self.create_history_button("DRAW 3")

        self.draw1_button.setCheckable(True)
        self.draw3_button.setCheckable(True)

        self.draw1_button.clicked.connect(
            lambda: self.set_draw_mode(1)
        )

        self.draw3_button.clicked.connect(
            lambda: self.set_draw_mode(3)
        )

        draw_mode_bar.addWidget(self.draw1_button)
        draw_mode_bar.addWidget(self.draw3_button)
        draw_mode_bar.addStretch()

        main_layout.addLayout(draw_mode_bar)

        self.update_draw_mode_buttons()

        # TABLEAU SCROLL AREA

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.scroll_area.setFrameShape(
            QScrollArea.Shape.NoFrame
        )

        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        self.scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }

            QScrollBar:vertical {
                background: #064b32;
                width: 9px;
                border-radius: 4px;
            }

            QScrollBar::handle:vertical {
                background: #d9b75d;
                border-radius: 4px;
                min-height: 25px;
            }

            QScrollBar:horizontal {
                background: #064b32;
                height: 9px;
            }

            QScrollBar::handle:horizontal {
                background: #d9b75d;
                border-radius: 4px;
            }
        """)

        self.tableau_content = QWidget()

        self.tableau_layout = QHBoxLayout(
            self.tableau_content
        )

        self.tableau_layout.setContentsMargins(2, 4, 2, 4)
        self.tableau_layout.setSpacing(13)

        self.tableau_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop |
            Qt.AlignmentFlag.AlignLeft
        )

        self.tableau_columns = []

        for _ in range(7):

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

        # BOTTOM TOOLBAR

        bottom_bar = QHBoxLayout()
        bottom_bar.setSpacing(8)

        new_button = self.create_toolbar_button("NEW GAME")
        new_button.clicked.connect(self.new_game)

        hint_button = self.create_toolbar_button("HINT")
        hint_button.clicked.connect(self.show_hint)

        restart_button = self.create_toolbar_button("RESTART")
        restart_button.clicked.connect(self.restart_game)

        move_history_button = self.create_toolbar_button(
            "MOVE HISTORY"
        )
        move_history_button.clicked.connect(
            self.show_move_history
        )

        action_history_button = self.create_toolbar_button(
            "ACTION HISTORY"
        )
        action_history_button.clicked.connect(
            self.show_action_history
        )

        card_location_button = self.create_toolbar_button(
            "CARD LOCATION"
        )
        card_location_button.clicked.connect(
            self.show_card_location
        )

        bottom_bar.addWidget(new_button)
        bottom_bar.addWidget(hint_button)
        bottom_bar.addWidget(restart_button)
        bottom_bar.addWidget(move_history_button)
        bottom_bar.addWidget(action_history_button)
        bottom_bar.addWidget(card_location_button)

        main_layout.addLayout(bottom_bar)

    # ==========================================
    # BUTTON DESIGN
    # ==========================================

    def create_history_button(self, text):

        button = QPushButton(text)
        button.setFixedSize(155, 38)

        button.setStyleSheet("""
            QPushButton {
                background-color: #e5bd62;
                color: #263b2e;
                border: none;
                border-radius: 7px;
                font-size: 11px;
                font-weight: bold;
                padding: 4px;
            }

            QPushButton:hover {
                background-color: #f0ce7b;
            }

            QPushButton:disabled {
                background-color: #9c895e;
                color: #d6d0bd;
            }
        """)

        return button

    def create_toolbar_button(self, text):

        button = QPushButton(text)
        button.setMinimumHeight(42)
        button.setMinimumWidth(100)

        button.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed
        )

        button.setStyleSheet("""
            QPushButton {
                background-color: #e5bd62;
                color: #263b2e;
                border: none;
                border-radius: 7px;
                font-size: 10px;
                font-weight: bold;
                padding: 5px;
            }

            QPushButton:hover {
                background-color: #f0ce7b;
            }

            QPushButton:disabled {
                background-color: #9c895e;
                color: #d6d0bd;
            }
        """)

        return button

    # ==========================================
    # DRAW MODE
    # ==========================================

    def set_draw_mode(self, count):

        if not self.game.set_draw_mode(count):
            return

        self.update_draw_mode_buttons()

        self.status_label.setText(
            f"Draw mode changed to Draw {count}."
        )

    def update_draw_mode_buttons(self):

        count = self.game.draw_count

        self.draw1_button.setChecked(count == 1)
        self.draw3_button.setChecked(count == 3)

        active_style = """
            QPushButton {
                background-color: #f0ce7b;
                color: #173c2c;
                border: 3px solid white;
                border-radius: 7px;
                font-size: 11px;
                font-weight: bold;
            }
        """

        inactive_style = """
            QPushButton {
                background-color: #e5bd62;
                color: #263b2e;
                border: 1px solid #c5a34f;
                border-radius: 7px;
                font-size: 11px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #f0ce7b;
            }
        """

        self.draw1_button.setStyleSheet(
            active_style if count == 1 else inactive_style
        )

        self.draw3_button.setStyleSheet(
            active_style if count == 3 else inactive_style
        )

    # ==========================================
    # CARD DESIGN
    # ==========================================

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

    def create_card_button(
        self,
        card,
        callback,
        selected=False
    ):

        button = QPushButton()
        button.setFixedSize(self.CARD_W, self.CARD_H)

        if card.face_up:

            color = (
                "#d92735"
                if card.color == "Red"
                else "#17202a"
            )

            border = (
                "3px solid #f4ce72"
                if selected
                else "1px solid #d6d1c5"
            )

            button.setText(self.card_display_text(card))

            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: #fffdf5;
                    color: {color};
                    border: {border};
                    border-radius: 8px;
                    font-size: 25px;
                    font-weight: bold;
                }}

                QPushButton:hover {{
                    background-color: #f5f0df;
                    border: 3px solid #e8bf5e;
                }}
            """)

        else:

            button.setText("✥")

            button.setStyleSheet("""
                QPushButton {
                    background-color: #19458d;
                    color: #e6edff;
                    border: 4px solid #e4c875;
                    border-radius: 8px;
                    font-size: 31px;
                }

                QPushButton:hover {
                    background-color: #2456a4;
                }
            """)

        button.clicked.connect(callback)

        return button

    # ==========================================
    # UNDO / REDO SYSTEM
    # ==========================================

    def save_history(self):

        snapshot = (
            deepcopy(self.game),
            self.moves
        )

        self.undo_stack.push(snapshot)

        self.redo_stack = Stack()

        self.update_history_buttons()

    def restore_snapshot(self, snapshot):

        self.game = snapshot[0]
        self.moves = snapshot[1]

        self.selected = None
        self.won_message_shown = False

        self.update_draw_mode_buttons()
        self.refresh_board()

        if not self.game.check_win():
            self.timer.start(1000)

    def undo_move(self):

        if self.undo_stack.is_empty():

            self.status_label.setText("Nothing to undo!")
            return

        current_snapshot = (
            deepcopy(self.game),
            self.moves
        )

        self.redo_stack.push(current_snapshot)

        previous_snapshot = self.undo_stack.pop()

        self.restore_snapshot(previous_snapshot)

        self.status_label.setText(
            "UNDO: Previous move restored."
        )

        self.update_history_buttons()

    def redo_move(self):

        if self.redo_stack.is_empty():

            self.status_label.setText("Nothing to redo!")
            return

        current_snapshot = (
            deepcopy(self.game),
            self.moves
        )

        self.undo_stack.push(current_snapshot)

        next_snapshot = self.redo_stack.pop()

        self.restore_snapshot(next_snapshot)

        self.status_label.setText(
            "REDO: Move restored again."
        )

        self.update_history_buttons()

    def update_history_buttons(self):

        self.undo_button.setEnabled(
            not self.undo_stack.is_empty()
        )

        self.redo_button.setEnabled(
            not self.redo_stack.is_empty()
        )

    # ==========================================
    # REFRESH BOARD
    # ==========================================

    def refresh_board(self):

        # STOCK

        if self.game.stock:

            self.stock_button.setText("✥")

            self.stock_button.setStyleSheet("""
                QPushButton {
                    background-color: #19458d;
                    color: white;
                    border: 4px solid #e4c875;
                    border-radius: 8px;
                    font-size: 32px;
                }
            """)

        else:

            self.stock_button.setText("↻")

            self.stock_button.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: 2px dashed #d2dfd4;
                    border-radius: 8px;
                    font-size: 30px;
                }
            """)

        # WASTE

        if self.game.waste:

            card = self.game.waste[-1]

            color = (
                "#d92735"
                if card.color == "Red"
                else "#17202a"
            )

            self.waste_button.setText(
                self.card_display_text(card)
            )

            self.waste_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: #fffdf5;
                    color: {color};
                    border: 1px solid #d6d1c5;
                    border-radius: 8px;
                    font-size: 23px;
                }}
            """)

        else:

            self.waste_button.setText("WASTE")

            self.waste_button.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: 2px dashed #d2dfd4;
                    border-radius: 8px;
                    font-size: 13px;
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
                    "#d92735"
                    if card.color == "Red"
                    else "#17202a"
                )

                button.setText(
                    self.card_display_text(card)
                )

                button.setStyleSheet(f"""
                    QPushButton {{
                        background-color: #fffdf5;
                        color: {color};
                        border: 1px solid #d6d1c5;
                        border-radius: 8px;
                        font-size: 23px;
                    }}
                """)

            else:

                button.setText(symbols[suit])

                button.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        border: 2px dashed #d2dfd4;
                        border-radius: 8px;
                        color: #d2dfd4;
                        font-size: 30px;
                    }
                """)

        # TABLEAU

        max_cards = max(
            (len(pile) for pile in self.game.tableau),
            default=0
        )

        board_height = max(
            self.CARD_H + 8,
            self.CARD_H +
            max(0, max_cards - 1) * self.CARD_GAP + 8
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
                        background: transparent;
                        border: 2px dashed #d2dfd4;
                        border-radius: 8px;
                        color: #d2dfd4;
                        font-size: 22px;
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
                    selected=is_selected
                )

                button.setParent(column)

                button.move(
                    0,
                    card_index * self.CARD_GAP
                )

                button.show()

        # SCORE AND MOVES

        self.score_label.setText(
            f"SCORE: {self.game.score}"
        )

        self.moves_label.setText(
            f"MOVES: {self.moves}"
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
                "Congratulations!",
                f"You won the Solitaire game!\n\n"
                f"Final Score: {self.game.score}\n"
                f"Total Moves: {self.moves}"
            )

    # ==========================================
    # STOCK AND WASTE
    # ==========================================

    def draw_card(self):

        if self.game.stock:

            self.save_history()

            draw_mode = self.game.draw_count

            self.game.draw_from_stock()
            self.moves += 1

            self.status_label.setText(
                f"Draw {draw_mode}: Cards drawn from stock."
            )

        elif self.game.waste:

            self.save_history()

            self.game.draw_from_stock()
            self.moves += 1

            self.status_label.setText(
                "Stock recycled. Cards returned to stock."
            )

        else:

            self.status_label.setText(
                "No cards available in stock or waste."
            )

        self.selected = None
        self.refresh_board()

    def select_waste(self):

        if not self.game.waste:
            return

        self.selected = ("waste", None, None)

        self.status_label.setText(
            "Waste card selected. Choose a destination."
        )

        self.refresh_board()

    # ==========================================
    # TABLEAU SELECTION
    # ==========================================

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
                f"Selected {card}. Choose a destination column."
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
                f"Selected {card}. Choose a destination column."
            )

            self.refresh_board()
            return

        self.perform_tableau_destination(pile_index)

    # ==========================================
    # TABLEAU MOVEMENT
    # ==========================================

    def perform_tableau_destination(self, target_index):

        if self.selected is None:
            return

        source_type, source_index, source_card_index = self.selected

        if source_type == "waste":

            if not self.game.waste:
                self.finish_move(False)
                return

            moving_card = self.game.waste[-1]

            if not self.game.is_valid_tableau_move(
                moving_card,
                self.game.tableau[target_index]
            ):

                self.finish_move(False)
                return

            self.save_history()

            success = self.game.move_waste_to_tableau(
                target_index
            )

        else:

            if source_index == target_index:

                self.selected = None
                self.refresh_board()
                return

            source = self.game.tableau[source_index]
            target = self.game.tableau[target_index]

            if source_card_index >= len(source):
                self.finish_move(False)
                return

            moving_cards = source[source_card_index:]

            sequence_valid = all(
                card.face_up for card in moving_cards
            )

            for i in range(len(moving_cards) - 1):

                current_card = moving_cards[i]
                next_card = moving_cards[i + 1]

                if (
                    current_card.color == next_card.color
                    or current_card.rank != next_card.rank + 1
                ):

                    sequence_valid = False
                    break

            if (
                not sequence_valid
                or not self.game.is_valid_tableau_move(
                    moving_cards[0], target
                )
            ):

                self.finish_move(False)
                return

            self.save_history()

            success = self.game.move_tableau_to_tableau(
                source_index,
                target_index,
                source_card_index
            )

        self.finish_move(success)

    # ==========================================
    # EMPTY COLUMN MOVEMENT
    # ==========================================

    def select_empty_column(self, pile_index):

        if self.selected is None:
            return

        source_type, source_index, source_card_index = self.selected

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

            source = self.game.tableau[source_index]

            if source_index == pile_index:

                self.selected = None
                self.refresh_board()
                return

            if source_card_index >= len(source):
                self.finish_move(False)
                return

            moving_cards = source[source_card_index:]

            valid = (
                bool(moving_cards)
                and moving_cards[0].rank == 13
                and all(card.face_up for card in moving_cards)
            )

            for i in range(len(moving_cards) - 1):

                if (
                    moving_cards[i].color == moving_cards[i + 1].color
                    or moving_cards[i].rank != moving_cards[i + 1].rank + 1
                ):

                    valid = False
                    break

            if not valid:
                self.finish_move(False)
                return

            self.save_history()

            success = self.game.move_tableau_to_tableau(
                source_index,
                pile_index,
                source_card_index
            )

        self.finish_move(success)

    # ==========================================
    # FOUNDATION MOVEMENT
    # ==========================================

    def move_to_foundation(self, suit):

        if self.selected is None:
            return

        source_type, source_index, source_card_index = self.selected

        success = False

        if source_type == "waste":

            if (
                self.game.waste
                and self.game.waste[-1].suit == suit
                and self.game.is_valid_foundation_move(
                    self.game.waste[-1],
                    self.game.foundations[suit]
                )
            ):

                self.save_history()

                success = self.game.move_waste_to_foundation()

        elif source_type == "tableau":

            pile = self.game.tableau[source_index]

            if (
                pile
                and source_card_index == len(pile) - 1
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

    # ==========================================
    # FINISH MOVE
    # ==========================================

    def finish_move(self, success):

        if success:

            self.moves += 1

            self.status_label.setText(
                "Move successful!"
            )

        else:

            self.status_label.setText(
                "Invalid move!"
            )

        self.selected = None
        self.refresh_board()

    # ==========================================
    # LINKED LIST: MOVE HISTORY
    # ==========================================

    def show_move_history(self):

        moves = self.game.get_move_history()

        if not moves:
            history_text = "No card moves recorded yet."
        else:
            history_text = "\n\n".join(
                f"{i + 1}. {move}"
                for i, move in enumerate(moves)
            )

        msg = QMessageBox(self)
        msg.setWindowTitle("Linked List - Move History")
        msg.setText(history_text)

        msg.setStyleSheet("""
            QMessageBox {
                background-color: white;
            }

            QMessageBox QLabel {
                color: black;
                font-size: 13px;
            }

            QMessageBox QPushButton {
                background-color: #e5bd62;
                color: black;
                padding: 6px 18px;
                border-radius: 5px;
                font-weight: bold;
            }
        """)

        msg.exec()

    # ==========================================
    # QUEUE: ACTION HISTORY
    # ==========================================

    def show_action_history(self):

        actions = self.game.get_action_history()

        if not actions:
            history_text = "No actions recorded yet."
        else:
            history_text = "\n\n".join(
                f"{i + 1}. {action}"
                for i, action in enumerate(actions)
            )

        msg = QMessageBox(self)
        msg.setWindowTitle("Queue - Action History")
        msg.setText(history_text)

        msg.setStyleSheet("""
            QMessageBox {
                background-color: white;
            }

            QMessageBox QLabel {
                color: black;
                font-size: 13px;
            }

            QMessageBox QPushButton {
                background-color: #e5bd62;
                color: black;
                padding: 6px 18px;
                border-radius: 5px;
                font-weight: bold;
            }
        """)

        msg.exec()

    # ==========================================
    # CARD MAP: LOCATION
    # ==========================================

    def show_card_location(self):

        selected_card = None

        if self.selected is not None:

            source_type, source_index, card_index = self.selected

            if source_type == "waste":

                if self.game.waste:
                    selected_card = self.game.waste[-1]

            elif source_type == "tableau":

                pile = self.game.tableau[source_index]

                if 0 <= card_index < len(pile):
                    selected_card = pile[card_index]

        if selected_card is not None:

            location = self.game.get_card_location(
                selected_card
            )

            message = (
                f"Card: {selected_card}\n"
                f"Current Location: {location}"
            )

        else:

            stock_count = len(self.game.stock)
            waste_count = len(self.game.waste)

            tableau_count = sum(
                len(pile) for pile in self.game.tableau
            )

            foundation_count = sum(
                len(pile)
                for pile in self.game.foundations.values()
            )

            message = (
                "CARD LOCATION SUMMARY\n\n"
                f"Stock: {stock_count}\n"
                f"Waste: {waste_count}\n"
                f"Tableau: {tableau_count}\n"
                f"Foundations: {foundation_count}\n\n"
                f"Mapped Cards: {self.game.get_card_map_size()}"
            )

        msg = QMessageBox(self)
        msg.setWindowTitle("CardMap - Card Location")
        msg.setText(message)

        msg.setStyleSheet("""
            QMessageBox {
                background-color: white;
            }

            QMessageBox QLabel {
                color: black;
                font-size: 13px;
            }

            QMessageBox QPushButton {
                background-color: #e5bd62;
                color: black;
                padding: 6px 18px;
                border-radius: 5px;
                font-weight: bold;
            }
        """)

        msg.exec()

    # ==========================================
    # HINT
    # ==========================================

    def show_hint(self):

        if self.game.waste:

            card = self.game.waste[-1]

            for i, pile in enumerate(self.game.tableau):

                if self.game.is_valid_tableau_move(card, pile):

                    self.status_label.setText(
                        f"Hint: Move {card} to column {i + 1}."
                    )

                    return

            if self.game.is_valid_foundation_move(
                card,
                self.game.foundations[card.suit]
            ):

                self.status_label.setText(
                    "Hint: Move the waste card to its foundation."
                )

                return

        for source_index, source in enumerate(self.game.tableau):

            if not source:
                continue

            card = source[-1]

            if not card.face_up:
                continue

            if self.game.is_valid_foundation_move(
                card,
                self.game.foundations[card.suit]
            ):

                self.status_label.setText(
                    f"Hint: Move the top card of column "
                    f"{source_index + 1} to its foundation."
                )

                return

            for target_index, target in enumerate(self.game.tableau):

                if (
                    source_index != target_index
                    and self.game.is_valid_tableau_move(card, target)
                ):

                    self.status_label.setText(
                        f"Hint: Move the top card of column "
                        f"{source_index + 1} to column "
                        f"{target_index + 1}."
                    )

                    return

        self.status_label.setText(
            "Hint: Draw a card or check your tableau."
        )

    # ==========================================
    # NEW GAME AND RESTART
    # ==========================================

    def new_game(self):

        self.game.new_game()

        self.undo_stack = Stack()
        self.redo_stack = Stack()

        self.selected = None
        self.moves = 0
        self.seconds = 0
        self.won_message_shown = False

        self.timer.start(1000)

        self.status_label.setText(
            "New game started!"
        )

        self.time_label.setText("TIME: 00:00")

        self.update_draw_mode_buttons()
        self.refresh_board()

    def restart_game(self):

        self.new_game()

    # ==========================================
    # TIMER
    # ==========================================

    def update_timer(self):

        self.seconds += 1

        minutes = self.seconds // 60
        seconds = self.seconds % 60

        self.time_label.setText(
            f"TIME: {minutes:02d}:{seconds:02d}"
        )


if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
