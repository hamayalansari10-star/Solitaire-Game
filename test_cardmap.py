
from game.game_engine import GameEngine

game = GameEngine()

print("========== CARD MAP TEST ==========")

# Initial card count
print("Total cards:", game.count_all_cards())

# CardMap count
print("Mapped cards:", game.get_card_map_size())

# Check one stock card
stock_card = game.stock[-1]

print("\nStock card:", stock_card)
print("Its location:", game.get_card_location(stock_card))

# Check one tableau card
tableau_card = game.tableau[0][-1]

print("\nTableau card:", tableau_card)
print("Its location:", game.get_card_location(tableau_card))

# Draw a card
game.draw_from_stock()

print("\nAfter drawing a card:")

waste_card = game.waste[-1]

print("Drawn card:", waste_card)
print("New location:", game.get_card_location(waste_card))

# Check all cards
print("\nFinal card count:", game.count_all_cards())
print("Final mapped cards:", game.get_card_map_size())

# Verify
print("\nCardMap working:", game.get_card_map_size() == 52)
print("52 cards preserved:", game.count_all_cards() == 52)
