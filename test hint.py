import random
from game.game_engine import GameEngine
from game.card import Card


def test(name, result):
    print(f"{name}: {'PASS' if result else 'FAIL'}")


def empty_game():
    g = GameEngine()
    g.tableau = [[] for _ in range(7)]
    g.stock = []
    g.waste = []
    for s in g.foundations:
        g.foundations[s] = []
    g.refresh_card_map()
    return g


def snapshot(g):
    return (
        [[(c.suit, c.rank, c.face_up) for c in p] for p in g.tableau],
        [(c.suit, c.rank, c.face_up) for c in g.stock],
        [(c.suit, c.rank, c.face_up) for c in g.waste],
        {s: len(p) for s, p in g.foundations.items()},
        g.score,
    )


def apply_hint(g, h):
    t = h["type"]
    if t == "waste_to_foundation":
        return g.move_waste_to_foundation()
    if t == "tableau_to_foundation":
        return g.move_tableau_to_foundation(h["source"])
    if t == "tableau_to_tableau":
        return g.move_tableau_to_tableau(h["source"], h["target"], h["card_index"])
    if t == "waste_to_tableau":
        return g.move_waste_to_tableau(h["target"])
    if t in ("draw", "recycle"):
        before = len(g.stock) + len(g.waste)
        g.draw_from_stock()
        return len(g.stock) + len(g.waste) == before
    return False


print("\n========== HINT TESTING ==========\n")

# 1. Foundation priority: Ace in waste
g = empty_game()
g.waste = [Card("Hearts", 1, True)]
g.tableau[0] = [Card("Clubs", 8, True)]
h = g.get_hint()
test("Waste ace -> foundation hint", h["type"] == "waste_to_foundation")

# 2. Tableau -> foundation
g = empty_game()
g.tableau[2] = [Card("Spades", 1, True)]
h = g.get_hint()
test("Tableau ace -> foundation hint",
     h["type"] == "tableau_to_foundation" and h["source"] == 2)

# 3. Reveal hidden card has priority over waste->tableau
g = empty_game()
g.tableau[0] = [Card("Spades", 5, False), Card("Hearts", 7, True)]
g.tableau[1] = [Card("Clubs", 8, True)]
g.waste = [Card("Diamonds", 6, True)]
g.tableau[2] = [Card("Spades", 7, True)]
h = g.get_hint()
test("Reveal-hidden move preferred",
     h["type"] == "tableau_to_tableau" and h["source"] == 0)

# 4. Waste -> tableau
g = empty_game()
g.waste = [Card("Hearts", 7, True)]
g.tableau[0] = [Card("Clubs", 8, True)]
h = g.get_hint()
test("Waste -> tableau hint",
     h["type"] == "waste_to_tableau" and h["target"] == 0)

# 5. King to empty column (with hidden card under it)
g = empty_game()
g.tableau[0] = [Card("Spades", 3, False), Card("Hearts", 13, True)]
h = g.get_hint()
test("King (with hidden below) -> empty column",
     h["type"] == "tableau_to_tableau" and h["target"] != 0)

# 6. Base King -> empty column must NOT be suggested
g = empty_game()
g.tableau[0] = [Card("Hearts", 13, True)]
g.stock = [Card("Clubs", 2, False)]
h = g.get_hint()
test("Base King -> empty column NOT suggested", h["type"] == "draw")

# 7. Multi-card sequence move
g = empty_game()
g.tableau[0] = [Card("Spades", 4, False), Card("Hearts", 7, True), Card("Clubs", 6, True)]
g.tableau[1] = [Card("Clubs", 8, True)]
h = g.get_hint()
test("Sequence move suggests correct start index",
     h["type"] == "tableau_to_tableau" and h["card_index"] == 1)

# 8. Draw / recycle / none
g = empty_game()
g.stock = [Card("Clubs", 2, False)]
test("Draw hint", g.get_hint()["type"] == "draw")

g = empty_game()
g.waste = [Card("Clubs", 2, True)]
test("Recycle hint", g.get_hint()["type"] == "recycle")

g = empty_game()
test("No moves hint", g.get_hint()["type"] == "none")

# 9. Face-down cards never suggested
g = empty_game()
g.tableau[0] = [Card("Hearts", 7, False)]
g.tableau[1] = [Card("Clubs", 8, True)]
test("Face-down card not suggested", g.get_hint()["type"] == "none")

# 10. Invalid partial sequence not suggested
g = empty_game()
g.tableau[0] = [Card("Hearts", 9, True), Card("Spades", 5, True)]  # broken sequence
g.tableau[1] = [Card("Clubs", 10, True)]
h = g.get_hint()
test("Broken sequence not suggested", h["type"] == "none")

# 11. Hint does not change the game
g = GameEngine()
before = snapshot(g)
g.get_hint(); g.get_hint()
test("Hint does not modify state", before == snapshot(g))

# 12. Stress: every hint must actually be executable
bad = 0
total = 0
wins = 0
for seed in range(500):
    random.seed(seed)
    g = GameEngine()
    g.set_draw_mode(random.choice([1, 3]))
    for _ in range(300):
        h = g.get_hint()
        if h["type"] == "none":
            break
        total += 1
        if not apply_hint(g, h):
            bad += 1
            print("  BAD HINT", seed, h)
            break
        if g.count_all_cards() != 52 or g.get_card_map_size() != 52:
            bad += 1
            break
        if g.check_win():
            wins += 1
            break

test(f"Stress: {total} hints all executable", bad == 0)
print(f"  (hint-bot won {wins}/500 games)")
# 13. Hint never loops forever
loops = 0
for seed in range(200):
    random.seed(seed)
    g = GameEngine()
    for _ in range(2000):
        h = g.get_hint()
        if h["type"] == "none" or g.check_win():
            break
        apply_hint(g, h)
    else:
        loops += 1
test("Hint never loops forever (200 games)", loops == 0)

# 14. No ping-pong between two columns
g = empty_game()
g.tableau[0] = [Card("Hearts", 7, True)]
g.tableau[1] = [Card("Clubs", 8, True)]
g.tableau[2] = [Card("Spades", 8, True)]
g.tableau[3] = [Card("Diamonds", 9, True)]
h = g.get_hint()
test("Hint suggests column-emptying move", h["type"] == "tableau_to_tableau" and h["card_index"] == 0)

print("\n========== HINT TESTING FINISHED ==========")