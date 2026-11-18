
from game.game_engine import GameEngine
from game.card import Card


def test(name, result):
    print(f"{name}: {'PASS' if result else 'FAIL'}")


print("\n========== GAME ENGINE TESTING ==========\n")


# ---------------------------------
# 1. INITIAL GAME
# ---------------------------------
game = GameEngine()

test("52 cards created", game.count_all_cards() == 52)
test("7 tableau columns", len(game.tableau) == 7)
test("28 tableau cards", sum(len(p) for p in game.tableau) == 28)
test("24 stock cards", len(game.stock) == 24)
test("4 foundation piles", len(game.foundations) == 4)


# ---------------------------------
# 2. STOCK DRAWING
# ---------------------------------
game.draw_from_stock()

test("Stock draw successful", len(game.stock) == 23)
test("Waste contains one card", len(game.waste) == 1)
test("Total cards preserved", game.count_all_cards() == 52)


# ---------------------------------
# 3. WASTE TO FOUNDATION
# ---------------------------------
game = GameEngine()

ace = next(card for card in game.stock if card.rank == 1)

game.stock.remove(ace)
game.stock.append(ace)

game.draw_from_stock()

test(
    "Waste to foundation",
    game.move_waste_to_foundation()
)

test(
    "Foundation contains one card",
    sum(len(p) for p in game.foundations.values()) == 1
)


# ---------------------------------
# 4. WASTE TO TABLEAU
# ---------------------------------
game = GameEngine()

game.waste = [Card("Hearts", 7, True)]
game.tableau[0] = [Card("Clubs", 8, True)]

test(
    "Waste to tableau",
    game.move_waste_to_tableau(0)
)


# ---------------------------------
# 5. TABLEAU TO TABLEAU
# ---------------------------------
game = GameEngine()

game.tableau = [
    [Card("Hearts", 7, True)],
    [Card("Clubs", 8, True)],
    [],
    [],
    [],
    [],
    []
]

test(
    "Valid tableau move",
    game.move_tableau_to_tableau(0, 1)
)

test(
    "Source pile empty",
    len(game.tableau[0]) == 0
)


# ---------------------------------
# 6. INVALID MOVE
# ---------------------------------
game = GameEngine()

game.tableau = [
    [Card("Hearts", 7, True)],
    [Card("Hearts", 8, True)],
    [],
    [],
    [],
    [],
    []
]

test(
    "Invalid same-color move rejected",
    not game.move_tableau_to_tableau(0, 1)
)


# ---------------------------------
# 7. FACE-DOWN CARD FLIP
# ---------------------------------
game = GameEngine()

game.tableau = [
    [
        Card("Spades", 5, False),
        Card("Hearts", 7, True)
    ],
    [Card("Clubs", 8, True)],
    [],
    [],
    [],
    [],
    []
]

game.move_tableau_to_tableau(0, 1)

test(
    "Face-down card flipped",
    game.tableau[0][-1].face_up
)


# ---------------------------------
# 8. STOCK RECYCLING
# ---------------------------------
game = GameEngine()

while game.stock:
    game.draw_from_stock()

test("Stock becomes empty", len(game.stock) == 0)
test("Waste contains 24 cards", len(game.waste) == 24)

game.draw_from_stock()

test("Stock recycling", len(game.stock) == 24)
test("Waste becomes empty", len(game.waste) == 0)


# ---------------------------------
# 9. WIN CONDITION
# ---------------------------------
game = GameEngine()

for suit in ["Hearts", "Diamonds", "Clubs", "Spades"]:

    for rank in range(1, 14):

        game.foundations[suit].append(
            Card(suit, rank, True)
        )

test("Win condition", game.check_win())


# ---------------------------------
# 10. INVALID SEQUENCE TEST
# ---------------------------------
game = GameEngine()

game.tableau = [
    [
        Card("Hearts", 9, True),
        Card("Diamonds", 8, True)
    ],
    [Card("Clubs", 10, True)],
    [],
    [],
    [],
    [],
    []
]

test(
    "Invalid sequence rejected",
    not game.move_tableau_to_tableau(0, 1)
)


# ---------------------------------
# TESTING FINISHED
# ---------------------------------
print("\n========== TESTING FINISHED ==========")
