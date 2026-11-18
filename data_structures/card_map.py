
class CardMap:

    def __init__(self):
        self.locations = {}

    # Add card location
    def add(self, card, location):
        self.locations[id(card)] = location

    # Get card location
    def get(self, card):
        return self.locations.get(id(card))

    # Update card location
    def update(self, card, location):
        self.locations[id(card)] = location

    # Remove card
    def remove(self, card):
        self.locations.pop(id(card), None)

    # Total mapped cards
    def size(self):
        return len(self.locations)

    # Clear all locations
    def clear(self):
        self.locations.clear()
