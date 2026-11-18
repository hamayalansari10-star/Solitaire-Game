
class Queue:

    def __init__(self):
        self.items = []
        self.front_index = 0

    def enqueue(self, item):
        self.items.append(item)

    def dequeue(self):
        if self.is_empty():
            return None

        item = self.items[self.front_index]
        self.front_index += 1

        # Reset queue when all items have been processed
        if self.front_index == len(self.items):
            self.items = []
            self.front_index = 0

        return item

    def is_empty(self):
        return self.front_index >= len(self.items)

    def size(self):
        return len(self.items) - self.front_index

    def peek(self):
        if self.is_empty():
            return None

        return self.items[self.front_index]

    def get_all(self):
        return self.items[self.front_index:]

    def clear(self):
        self.items = []
        self.front_index = 0
