from typing import List, Tuple, Literal
from copy import deepcopy

# The initial state of the game board.
# 'h' denotes a horizontal car part, 'v' a vertical one, and 0 is empty.
ESTADO_INICIAL = [
    [0, 0, 0, 0, 0],
    [0, 0, "v", 0, 0],
    [0, 0, "v", 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, "h", "h"],
]

# The target state for the game to be won.
ESTADO_OBJETIVO = [
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, "h", "h"],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
]


class Car:
    """
    Represents a single car on the game board.
    It stores the car's start and end coordinates and its orientation.
    """

    def __init__(
        self,
        start_pos: Tuple[int, int],
        end_pos: Tuple[int, int],
        orientation: Literal["vertical", "horizontal"],
    ):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.orientation = orientation
        self.length = self._calculate_length()

    def _calculate_length(self) -> int:
        """Calculates the length of the car based on its coordinates."""
        if self.orientation == "horizontal":
            return self.end_pos[1] - self.start_pos[1] + 1
        else:
            return self.end_pos[0] - self.start_pos[0] + 1

    def __repr__(self):
        """Provides a developer-friendly representation of the Car object."""
        return (
            f"Car(start={self.start_pos}, end={self.end_pos}, "
            f"orientation='{self.orientation}', length={self.length})"
        )


class Game:
    """
    Manages the game state, including the board and the list of cars.
    """

    def __init__(self, board_dimension=5):
        self.board_dimension = board_dimension
        # Initialize the board with the starting state
        self.board = ESTADO_INICIAL
        self.cars: List[Car] = []

    def __repr__(self):
        """Returns a string representation of the board for printing."""

        out = ""
        out += "Board State:\n"
        for row in self.board:
            for item in row:
                out += f"{item} "
            out += "\n"
        out += "\n"
        out += "Identified Cars:\n"
        for car in self.cars:
            out += f"{car}\n"
        return out

    def __str__(self):
        self.find_cars()
        board = deepcopy(self.board)
        for n, car in enumerate(self.cars):
            start_pos = car.start_pos
            end_pos = car.end_pos
            orientation = car.orientation

            if orientation == "vertical":
                start_i, j = start_pos
                end_i = end_pos[0] + 1
                for i in range(start_i, end_i):
                    board[i][j] = n + 1
                continue

            if orientation == "horizontal":
                i, start_j = start_pos
                end_j = end_pos[1] + 1
                for j in range(start_j, end_j):
                    board[i][j] = n + 1
                continue

        out = ""
        for row in board:
            for col in row:
                out += f"{col} "
            out += "\n"
        return out

    def find_cars(self):
        """
        Scans the board to identify all cars and populates the self.cars list.
        This method uses a depth-first search (DFS) to find all connected
        parts of each car.
        """
        # Reset the list of cars before scanning
        self.cars = []
        # Create a visited grid to keep track of processed car parts
        visited = [
            [False for _ in range(self.board_dimension)]
            for _ in range(self.board_dimension)
        ]

        # Iterate over every cell in the board
        for r in range(self.board_dimension):
            for c in range(self.board_dimension):
                # If a cell contains a car part and hasn't been visited,
                # it's the start of a new car to identify.
                if self.board[r][c] != 0 and not visited[r][c]:
                    car_type = self.board[r][c]
                    orientation = "horizontal" if car_type == "h" else "vertical"

                    # This list will store all coordinates of the current car
                    car_parts = []
                    # The stack for our iterative DFS
                    stack = [(r, c)]

                    # Perform DFS to find all parts of this car
                    while stack:
                        curr_r, curr_c = stack.pop()

                        # Boundary and type checks
                        is_valid_row = 0 <= curr_r < self.board_dimension
                        is_valid_col = 0 <= curr_c < self.board_dimension

                        if not (is_valid_row and is_valid_col):
                            continue

                        # If already visited or not part of the same car, skip
                        if (
                            visited[curr_r][curr_c]
                            or self.board[curr_r][curr_c] != car_type
                        ):
                            continue

                        # Mark as visited and add to our list of parts
                        visited[curr_r][curr_c] = True
                        car_parts.append((curr_r, curr_c))

                        # Explore neighbors based on orientation
                        if orientation == "horizontal":
                            stack.append((curr_r, curr_c + 1))  # Right
                            stack.append((curr_r, curr_c - 1))  # Left
                        else:  # Vertical
                            stack.append((curr_r + 1, curr_c))  # Down
                            stack.append((curr_r - 1, curr_c))  # Up

                    # After finding all parts, create the Car object
                    if car_parts:
                        # Determine start (min row/col) and end (max row/col)
                        start_pos = (
                            min(p[0] for p in car_parts),
                            min(p[1] for p in car_parts),
                        )
                        end_pos = (
                            max(p[0] for p in car_parts),
                            max(p[1] for p in car_parts),
                        )

                        new_car = Car(start_pos, end_pos, orientation)
                        self.cars.append(new_car)

    def _move_up(self, car_num):
        car = self.cars[car_num - 1]
        orientation = "v" if car.orientation == "vertical" else "h"

        if orientation == "h":
            i, start_j = car.start_pos
            end_j = car.end_pos[1]

            for j in range(start_j, end_j + 1):
                self.board[i][j] = 0
                self.board[i - 1][j] = orientation

        if orientation == "v":
            start_i, j = car.start_pos
            end_i = car.end_pos[0]

            for i in range(start_i, end_i + 1):
                self.board[i][j] = 0
            for i in range(start_i, end_i + 1):
                self.board[i - 1][j] = orientation

    def _move_down(self, car_num):
        car = self.cars[car_num - 1]
        orientation = "v" if car.orientation == "vertical" else "h"
        print(car)

        if orientation == "h":
            start_i, start_j = car.start_pos
            end_i, end_j = start_i + 1, car.end_pos[1]

            for j in range(start_j, end_j + 1):
                self.board[start_i][j] = 0
                self.board[end_i][j] = orientation

        if orientation == "v":
            start_i, j = car.start_pos
            end_i = car.end_pos[0]

            for i in range(start_i, end_i + 1):
                self.board[i][j] = 0
            for i in range(start_i, end_i + 1):
                self.board[i + 1][j] = orientation

    def move(self, car_idx: int, direction: Literal["up", "down", "left", "right"]):
        pass


# --- Example Usage ---
if __name__ == "__main__":
    # 1. Create a new game instance.
    my_game = Game()

    my_game.find_cars()

    # 4. Print the list of identified cars.
    print(my_game)
    my_game._move_up(1)
    my_game._move_up(2)
    print(my_game)
    my_game._move_down(1)
    my_game._move_down(2)
    print(my_game)
