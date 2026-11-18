# Solitaire Game – DSA Project

A Python-based **Klondike Solitaire Card Game** developed using **PyQt6**. This project combines Data Structures and Algorithms (DSA) with an interactive graphical user interface.

Players can move cards between tableau columns, draw cards from the stock pile, build foundation piles, and use Undo/Redo to manage their moves.

## Features

- Interactive graphical user interface built with PyQt6.
- New Game and Restart options.
- Draw 1 and Draw 3 card modes.
- Seven tableau columns.
- Four foundation piles.
- Stock and Waste piles.
- Valid and invalid card movement checking.
- Automatic flipping of face-down cards.
- Undo and Redo functionality.
- Hint feature.
- Score, moves counter, and game timer.
- Move History and Action History.
- Card Location tracking.
- Win condition detection.

## Technologies Used

- **Language:** Python
- **GUI Framework:** PyQt6
- **Data Structures:** Stack, Queue, Linked List, Hash Map
- **Libraries:** `copy`, `sys`, `random`, `time` and PyQt6 modules

## Data Structures Implemented

This project implements four custom data structures:

### 1. Stack – Undo and Redo

Used to store previous game states.

- `push()` – Adds a game state to the stack.
- `pop()` – Removes and returns the latest state.
- `peek()` – Returns the latest state.
- `is_empty()` – Checks whether the stack is empty.

**Purpose:** Allows players to undo and redo their moves.

### 2. Queue – Action History

Used to maintain game actions in FIFO (First In, First Out) order.

- `enqueue()` – Adds an action.
- `dequeue()` – Removes the oldest action.
- `peek()` – Returns the next action.
- `get_all()` – Returns available actions.

**Purpose:** Maintains the sequence of recorded game actions.

### 3. Linked List – Move History

A custom singly linked list stores recorded moves.

- `append()` – Adds a move to the list.
- `get_all()` – Returns all recorded moves.
- `get_last()` – Returns the latest move.
- `remove_last()` – Removes the latest move.
- `size()` – Returns the number of recorded moves.

**Purpose:** Maintains the history of player moves.

### 4. Hash Map – Card Location Tracking

A dictionary-based custom CardMap tracks the current location of cards.

- `add()` – Adds a card location.
- `get()` – Retrieves a card's location.
- `update()` – Updates a card's location.
- `remove()` – Removes a card entry.
- `size()` – Returns the number of mapped cards.

**Purpose:** Helps identify whether a card is in the stock, waste, tableau, or foundation.

## Project Structure

```text
Solitaire_Game/
│
├── data_structures/
│   ├── stack.py
│   ├── queue.py
│   ├── linked_list.py
│   ├── card_map.py
│   │
│   └── interface/
│       ├── main.py
│       ├── main_window.py
│       └── requirements.txt
│
├── game/
│   ├── __init__.py
│   ├── card.py
│   ├── deck.py
│   └── game_engine.py
│
├── test_engine.py
├── test_queue.py
├── test_linkedlist.py
└── test_cardmap.py
```

## Game Rules

This project follows the basic rules of Klondike Solitaire:

1. The game uses a standard deck of 52 cards.
2. Seven tableau columns are created at the beginning.
3. Only the top card of each tableau column is initially face-up.
4. Tableau cards are arranged in descending order with alternating colors.
5. Foundation piles are built in ascending order, starting from Ace and ending at King.
6. Players can draw cards from the stock pile.
7. When the stock becomes empty, the waste pile can be recycled.
8. The player wins when all 52 cards are placed in the four foundation piles.

## Installation and Setup

### 1. Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

### 2. Open the Project Folder

```bash
cd Solitaire_Game
```

### 3. Create a Virtual Environment

```bash
python -m venv venv
```

### 4. Activate the Virtual Environment

**Windows:**

```bash
venv\Scripts\activate
```

### 5. Install Dependencies

```bash
pip install PyQt6
```

## Run the Game

Run the following command from the project root directory:

```bash
python -m data_structures.interface.main
```

## Testing

The project includes separate test files for the game engine and custom data structures.

Run the tests using:

```bash
python test_engine.py
python test_queue.py
python test_linkedlist.py
python test_cardmap.py
```

The game engine tests cover:

- Initial game setup.
- Total card count.
- Stock and waste operations.
- Valid and invalid moves.
- Tableau and foundation movements.
- Face-down card flipping.
- Stock recycling.
- Win condition.

**Testing Status:** The individual game engine and data structure tests have been completed successfully. GUI functionality has also been manually tested.

## Learning Outcomes

This project demonstrates practical implementation of:

- Stack and Queue operations.
- Singly Linked Lists.
- Hash Map / Dictionary-based searching.
- Object-Oriented Programming.
- Game logic and validation.
- GUI development with PyQt6.
- State management using Undo and Redo.
- Integration of multiple data structures in one application.

## Author

**Hamayal Ansari**

BS Computer Science Student  
University of Engineering and Technology (UET), Lahore

---

**Project:** Solitaire Game – Data Structures and Algorithms (DSA)
