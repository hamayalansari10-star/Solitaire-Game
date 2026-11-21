
from game.game_engine import GameEngine
from game.card import Card

game = GameEngine()

# Clear all existing piles
game.stock = []
game.waste = []
game.tableau = [[] for _ in range(7)]

# Put all 52 cards into their correct foundations
suits = ["Hearts", "Diamonds", "Clubs", "Spades"]

for suit in suits:

    game.foundations[suit] = []

    for rank in range(1, 14):

        card = Card(
            suit=suit,
            rank=rank,
            face_up=True
        )

        game.foundations[suit].append(card)

# Update CardMap
game.refresh_card_map()

# Test results
print("========== WIN CONDITION TEST ==========")

print("Total Cards:", game.count_all_cards())

print("Foundation Cards:", sum(
    len(pile) for pile in game.foundations.values()
))

print("CardMap Size:", game.get_card_map_size())

print("Game Won:", game.check_win())

if game.check_win() and game.count_all_cards() == 52:
    print("\nTEST PASSED: Win condition is working!")
else:
    print("\nTEST FAILED: Check game engine.")
