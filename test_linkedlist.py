
from game.game_engine import GameEngine

game = GameEngine()

print("========== LINKED LIST TEST ==========")

# Check initial linked list
print("Initial move history:", game.get_move_history())

# Find a valid move using available cards
game.tableau = [
    [ ],
    [ ],
    [ ],
    [ ],
    [ ],
    [ ],
    [ ]
]

from game.card import Card

# Create a controlled test situation
game.tableau[0] = [Card("Hearts", 7, True)]
game.tableau[1] = [Card("Clubs", 8, True)]

# Move 7 Hearts onto 8 Clubs
result = game.move_tableau_to_tableau(0, 1)

print("\nMove successful:", result)

print("\nLinked List History:")
for move in game.get_move_history():
    print(move)

print("\nTotal moves:", game.move_history.size())

print("\nLast move:", game.get_last_move())

print("\nTotal cards in game:", game.count_all_cards())
