
from game.game_engine import GameEngine

game = GameEngine()

print("========== QUEUE TEST ==========")

print("Initial cards:", game.count_all_cards())
print("Initial stock:", len(game.stock))

# Test Draw 1
game.set_draw_mode(1)
game.draw_from_stock()

print("\nAfter Draw 1:")
print("Stock:", len(game.stock))
print("Waste:", len(game.waste))

# Test Draw 3
game.set_draw_mode(3)
game.draw_from_stock()

print("\nAfter Draw 3:")
print("Stock:", len(game.stock))
print("Waste:", len(game.waste))

# Display Queue
print("\n========== ACTION QUEUE ==========")

for action in game.get_action_history():
    print(action)

# Test dequeue
print("\n========== PROCESS NEXT ACTION ==========")

print(game.process_next_action())

print("Remaining actions:", game.action_queue.size())

# Final card count
print("\nTotal cards:", game.count_all_cards())
