
class Node:

    def __init__(self, data):
        self.data = data
        self.next = None


class LinkedList:

    def __init__(self):
        self.head = None
        self.tail = None
        self.length = 0

    def append(self, data):

        new_node = Node(data)

        if self.head is None:
            self.head = new_node
            self.tail = new_node

        else:
            self.tail.next = new_node
            self.tail = new_node

        self.length += 1

    def get_all(self):

        result = []
        current = self.head

        while current:
            result.append(current.data)
            current = current.next

        return result

    def get_last(self):

        if self.tail is None:
            return None

        return self.tail.data

    def remove_last(self):

        if self.head is None:
            return None

        if self.head == self.tail:
            removed = self.head.data
            self.head = None
            self.tail = None

        else:
            current = self.head

            while current.next != self.tail:
                current = current.next

            removed = self.tail.data
            current.next = None
            self.tail = current

        self.length -= 1
        return removed

    def size(self):
        return self.length
