import A_Star_Search
from wall_direction import WallDirection
from Color import Color

from rich.console import Console
from rich.table import Table
import numpy as np
from copy import copy
import threading
import copy
from rich.console import Console
from rich.table import Table
from rich.style import Style
from rich.text import Text


console = Console()

class Status:
    FILLED_BY_PLAYER_1 = 1
    FILLED_BY_PLAYER_2 = 2
    FILLED_BY_WALL = 5
    FREE_PLAYER = 3
    FREE_WALL = 4

class Mappings:
    INPUT_MAPPINGS = {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4, "F": 5, "G": 6, "H": 7, "I": 8, "J": 9, "K": 10,
                      "L": 11, "M": 12, "N": 13, "O": 14, "P": 15, "Q": 16}
    INPUT_MAPPINGS_REVERSED = {0: "A", 1: "B", 2: "C", 3: "D", 4: "E", 5: "F", 6: "G", 7: "H", 8: "I", 9: "J",
                               10: "K",
                               11: "L", 12: "M", 13: "N", 14: "O", 15: "P", 16: "Q"}
    INPUT_LETTERS = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q"]

class Environment:
    def __init__(self, is_simulation=False, initialize=True):
        self.is_simulation = is_simulation
        self.player_one = True
        self.rows = 13
        self.cols = 13
        self.player_one_walls_num = 10
        self.player_two_walls_num = 10
        self.lock = threading.Lock()

        if initialize:
            self.player_one_pos = np.array([12, 6])
            self.player_two_pos = np.array([0, 6])

            self.board = np.zeros((289,), dtype=int)
            self.set_up_board()

    def copy(self):
        new_env = Environment(is_simulation=self.is_simulation, initialize=False)
        new_env.player_one = self.player_one
        new_env.rows = self.rows
        new_env.cols = self.cols
        new_env.player_one_walls_num = self.player_one_walls_num
        new_env.player_two_walls_num = self.player_two_walls_num
        new_env.player_one_pos = np.copy(self.player_one_pos)
        new_env.player_two_pos = np.copy(self.player_two_pos)
        new_env.board = np.copy(self.board)
        new_env.lock = threading.Lock()
        return new_env

    def set_up_board(self):
        for i in range(self.rows):
            for j in range(self.cols):
                if i % 2 == 0 and j % 2 == 0:
                    self.board[i * self.cols + j] = Status.FREE_PLAYER
                else:
                    self.board[i * self.cols + j] = Status.FREE_WALL

        self.board[self.player_one_pos[0] * self.cols + self.player_one_pos[1]] = Status.FILLED_BY_PLAYER_1
        self.board[self.player_two_pos[0] * self.cols + self.player_two_pos[1]] = Status.FILLED_BY_PLAYER_2

    def print_game_stats(self):
        table = Table(title="Game Stats", show_header=True, header_style="bold magenta")
        table.add_column("Player 1 Walls", style="green", justify="center")
        table.add_column("Player 2 Walls", style="red", justify="center")
        table.add_row(str(self.player_one_walls_num), str(self.player_two_walls_num))
        console.print(table)

    def print_board(self):
        print("    ", end="")
        for i in range(0, len(Mappings.INPUT_LETTERS) - 3, 2):
            upper = Mappings.INPUT_LETTERS[i]
            lower = Mappings.INPUT_LETTERS[i + 1].lower()
            if i == len(Mappings.INPUT_LETTERS) - 3 - 2:
                print(f"  {upper} ", end="")
            else:
                print(f"  {upper} " + Color.YELLOW + f"  {lower}" + Color.RESET + " ", end="")
        print()

        for i in range(self.rows):
            label = Mappings.INPUT_LETTERS[i]
            if i % 2 == 0:
                print(f"{label:>2}  ", end="")
            else:
                print(Color.YELLOW + f"{label.lower():>2}  " + Color.RESET, end="")

            for j in range(self.cols):
                index = i * self.cols + j
                cell = self.board[index]

                if cell == Status.FREE_PLAYER:
                    print("     ", end="")
                elif cell == Status.FILLED_BY_PLAYER_1:
                    print(Color.GREEN + "  ♟  " + Color.RESET, end="")
                elif cell == Status.FILLED_BY_PLAYER_2:
                    print(Color.RED + "  ♟  " + Color.RESET, end="")
                else:
                    if i % 2 == 1 and j % 2 == 0:
                        if cell == Status.FREE_WALL:
                            print("─────", end="")
                        else:
                            print(Color.YELLOW + "━━━━━" + Color.RESET, end="")
                    elif i % 2 == 0 and j % 2 == 1:
                        if cell == Status.FREE_WALL:
                            print(" │ ", end="")
                        else:
                            print(Color.YELLOW + " ┃ " + Color.RESET, end="")
                    elif i % 2 == 1 and j % 2 == 1:
                        if cell == Status.FREE_WALL:
                            print("─┼─", end="")
                        else:
                            print(Color.YELLOW + "━╋━" + Color.RESET, end="")
            print()

    def is_pawn_filled(self, i, j):
        index = i * self.cols + j
        return self.board[index] == Status.FILLED_BY_PLAYER_1 or self.board[index] == Status.FILLED_BY_PLAYER_2

    def is_not_pawn_filled(self, i, j):
        return not self.is_pawn_filled(i, j)

    def is_wall_filled(self, i, j):
        return self.board[i * self.cols + j] == Status.FILLED_BY_WALL

    def is_not_wall_filled(self, i, j):
        return not self.is_wall_filled(i, j)

    def is_jump(self, move):
        if self.player_one:
            return abs(self.player_one_pos[0] - move[0]) == 4
        else:
            return abs(self.player_two_pos[0] - move[0]) == 4

    def is_diagonal(self, move):
        if self.player_one:
            return abs(self.player_one_pos[0] - move[0]) == 2 and abs(self.player_one_pos[1] - move[1]) == 2
        else:
            return abs(self.player_two_pos[0] - move[0]) == 2 and abs(self.player_two_pos[1] - move[1]) == 2

    def is_goal_state(self):
        if self.player_one:
            return self.player_one_pos[0] == 0
        else:
            return self.player_two_pos[0] == 12

    def distance_to_goal(self):
        if self.player_one:
            return self.player_one_pos[0]
        else:
            return 12 - self.player_two_pos[0]

    def get_child_states_with_moves(self):
        available_moves = self.get_available_moves(False)
        children = []
        for move in available_moves:
            child = self.copy()
            child.move_pawn(move)
            cost = 1000
            if self.is_jump(move):
                cost = 500
            elif self.is_diagonal(move):
                cost = 500
            if child.player_one:
                pos = child.player_one_pos
            else:
                pos = child.player_two_pos
            simplified_child_state = ((pos[0], pos[1]), (move[0], move[1]), cost)

            children.append((child, simplified_child_state))
        return children

    def get_all_child_states(self, player_one_maximizer, include_state=True):

        children = []
        available_moves = self.get_available_moves(include_state)
        for move in available_moves:
            children.append(move)

        available_wall_placements = []
        if not self.player_one and not player_one_maximizer:
            available_wall_placements = self.get_available_wall_placements_for_player_two(include_state)

        if self.player_one and player_one_maximizer:
            available_wall_placements = self.get_available_wall_placements_for_player_one(include_state)

        for wall_placement in available_wall_placements:
            children.append(wall_placement)

        return children

    def get_north_pos(self, include_state=True):

        if self.player_one:
            i, j = self.player_one_pos
            move = -2
            wall = -1
        else:
            i, j = self.player_two_pos
            move = 2
            wall = 1

        if 0 <= i + move <= 12 and 0 <= i + wall <= 12:
            if self.is_not_pawn_filled(i + move, j) and self.is_not_wall_filled(i + wall, j):
                position = (i + move, j)
                if include_state:
                    copy_state = self.copy()
                    copy_state.move_pawn(position)
                    copy_state.player_one = not self.player_one
                    return copy_state, position
                else:
                    return position
            else:
                return None
        else:
            return None

    def get_south_pos(self, include_state=True):

        if self.player_one:
            i, j = self.player_one_pos
            move_x = 2
            wall_x = 1
        else:
            i, j = self.player_two_pos
            move_x = -2
            wall_x = -1

        if 0 <= i + move_x <= 12 and 0 <= i + wall_x <= 12:
            if self.is_not_wall_filled(i + wall_x, j) and self.is_not_pawn_filled(i + move_x, j):
                position = (i + move_x, j)
                if include_state:
                    copy_state = self.copy()
                    copy_state.move_pawn(position)
                    copy_state.player_one = not self.player_one
                    return copy_state, position
                else:
                    return position
            else:
                return None
        else:
            return None

    def get_west_pos(self, include_state=True):

        if self.player_one:
            i, j = self.player_one_pos
            move_y = -2
            wall_y = -1
        else:
            i, j = self.player_two_pos
            move_y = 2
            wall_y = 1

        if 0 <= j + move_y <= 12 and 0 <= j + wall_y <= 12:
            if self.is_not_pawn_filled(i, j + move_y) and self.is_not_wall_filled(i, j + wall_y):
                position = (i, j + move_y)
                if include_state:
                    copy_state = self.copy()
                    copy_state.move_pawn(position)
                    copy_state.player_one = not self.player_one
                    return copy_state, position
                else:
                    return position
            else:
                return None
        else:
            return None

    def get_east_pos(self, include_state=True):

        if self.player_one:
            i, j = self.player_one_pos
            move_y = 2
            wall_y = 1
        else:
            i, j = self.player_two_pos
            move_y = -2
            wall_y = -1

        if 0 <= j + move_y <= 12 and 0 <= j + wall_y <= 12:
            if self.is_not_pawn_filled(i, j + move_y) and self.is_not_wall_filled(i, j + wall_y):
                position = (i, j + move_y)
                if include_state:
                    copy_state = self.copy()
                    copy_state.move_pawn(position)
                    copy_state.player_one = not self.player_one
                    return copy_state, position
                else:
                    return position
            else:
                return None
        else:
            return None

    def get_jump_pos(self, include_state=True):

        if self.player_one:
            i, j = self.player_one_pos
            jump = -4
            move = -2
            wall1 = -1
            wall2 = -3
        else:
            i, j = self.player_two_pos
            jump = 4
            move = 2
            wall1 = 1
            wall2 = 3

        if 0 <= i + jump <= 12:
            if self.is_not_wall_filled(i + wall1, j) and self.is_pawn_filled(i + move, j) and \
                    self.is_not_wall_filled(i + wall2, j):
                position = (i + jump, j)
                if include_state:
                    copy_state = self.copy()
                    copy_state.move_pawn(position)
                    copy_state.player_one = not self.player_one
                    return copy_state, position
                else:
                    return position
            else:
                return None
        else:
            return None

    def get_northwest_pos(self, include_state=True):

        if self.player_one:
            i, j = self.player_one_pos
            move_x = -2
            move_y = -2
            wall_x = -1
            wall_y = -1
            occupied_x = -2
            FILLED_BY_WALL = -3
        else:
            i, j = self.player_two_pos
            move_x = 2
            move_y = 2
            wall_x = 1
            wall_y = 1
            occupied_x = 2
            FILLED_BY_WALL = 3

        if 0 <= i + move_x <= 12 and \
                0 <= j + move_y <= 12 and \
                0 <= i + wall_x <= 12 and \
                0 <= j + wall_y <= 12 and \
                0 <= i + occupied_x <= 12 and \
                0 <= i + FILLED_BY_WALL <= 12:
            if self.is_not_wall_filled(i + wall_x, j + wall_y) and \
                    self.is_pawn_filled(i + occupied_x, j) and \
                    self.is_wall_filled(i + FILLED_BY_WALL, j):
                position = (i + move_x, j + move_y)
                if include_state:
                    copy_state = self.copy()
                    copy_state.move_pawn(position)
                    copy_state.player_one = not self.player_one
                    return copy_state, position
                else:
                    return position
            else:
                return None
        else:
            return None

    def get_northeast_pos(self, include_state=True):

        if self.player_one:
            i, j = self.player_one_pos
            move_x = -2
            move_y = 2
            wall_x = -1
            wall_y = 1
            occupied_x = -2
            FILLED_BY_WALL = -3
        else:
            i, j = self.player_two_pos
            move_x = 2
            move_y = -2
            wall_x = 1
            wall_y = -1
            occupied_x = 2
            FILLED_BY_WALL = 3

        if 0 <= i + move_x <= 12 and \
                0 <= j + move_y <= 12 and \
                0 <= i + wall_x <= 12 and \
                0 <= j + wall_y <= 12 and \
                0 <= i + occupied_x <= 12 and \
                0 <= i + FILLED_BY_WALL <= 12:
            if self.is_not_wall_filled(i + wall_x, j + wall_y) and \
                    self.is_pawn_filled(i + occupied_x, j) and \
                    self.is_wall_filled(i + FILLED_BY_WALL, j):
                position = (i + move_x, j + move_y)
                if include_state:
                    copy_state = self.copy()
                    copy_state.move_pawn(position)
                    copy_state.player_one = not self.player_one
                    return copy_state, position
                else:
                    return position
            else:
                return None
        else:
            return None

    def get_available_moves(self, include_state=True):
        north = self.get_north_pos(include_state)
        south = self.get_south_pos(include_state)
        east = self.get_east_pos(include_state)
        west = self.get_west_pos(include_state)
        jump = self.get_jump_pos(include_state)
        north_east = self.get_northeast_pos(include_state)
        north_west = self.get_northwest_pos(include_state)

        array = []

        if south is not None:
            array.append(south)
        if east is not None:
            array.append(east)
        if west is not None:
            array.append(west)
        if jump is not None:
            array.append(jump)
        if north_east is not None:
            array.append(north_east)
        if north_west is not None:
            array.append(north_west)
        if north is not None:
            array.append(north)
        return array

    def check_wall_placement(self, starting_pos, direction):

        if self.player_one and self.player_one_walls_num == 0:
            return False, np.array([starting_pos[0], starting_pos[1], -1, -1, -1, -1])
        elif not self.player_one and self.player_two_walls_num == 0:
            return False, np.array([starting_pos[0], starting_pos[1], -1, -1, -1, -1])

        if starting_pos[0] % 2 == 1 and starting_pos[1] == 1:
            return False, np.array([starting_pos[0], starting_pos[1], -1, -1, -1, -1])

        if self.is_wall_filled(starting_pos[0], starting_pos[1]):
            return False, np.array([starting_pos[0], starting_pos[1], -1, -1, -1, -1])

        if direction == WallDirection.NORTH:
            if starting_pos[1] % 2 == 0:
                return False, np.array([starting_pos[0], starting_pos[1], -1, -1, -1, -1])
            else:
                second_piece_x = starting_pos[0] - 2
                second_piece_y = starting_pos[1]
                third_piece_x = starting_pos[0] - 1
                third_piece_y = starting_pos[1]
        elif direction == WallDirection.SOUTH:
            if starting_pos[1] % 2 == 0:
                return False, np.array([starting_pos[0], starting_pos[1], -1, -1, -1, -1])
            else:
                second_piece_x = starting_pos[0] + 2
                second_piece_y = starting_pos[1]
                third_piece_x = starting_pos[0] + 1
                third_piece_y = starting_pos[1]
        elif direction == WallDirection.EAST:
            if starting_pos[0] % 2 == 0:
                return False, np.array([starting_pos[0], starting_pos[1], -1, -1, -1, -1])
            else:
                second_piece_x = starting_pos[0]
                second_piece_y = starting_pos[1] + 2
                third_piece_x = starting_pos[0]
                third_piece_y = starting_pos[1] + 1

        else:  # WallDirection.WEST
            if starting_pos[0] % 2 == 0:
                return False, np.array([starting_pos[0], starting_pos[1], -1, -1, -1, -1])
            else:
                second_piece_x = starting_pos[0]
                second_piece_y = starting_pos[1] - 2
                third_piece_x = starting_pos[0]
                third_piece_y = starting_pos[1] - 1

        if not 0 <= starting_pos[0] <= 12 and not 0 <= starting_pos[1] <= 12 \
                and not 0 <= second_piece_x <= 12 and not 0 <= second_piece_y <= 12 \
                and not 0 <= third_piece_x <= 12 and not 0 <= third_piece_y <= 12:
            return False, np.array([starting_pos[0], starting_pos[1], -1, -1, -1, -1])

        if self.is_wall_filled(second_piece_x, second_piece_y):
            return False, np.array([starting_pos[0], starting_pos[1], -1, -1, -1, -1])
        if self.is_wall_filled(third_piece_x, third_piece_y):
            return False, np.array([starting_pos[0], starting_pos[1], -1, -1, -1, -1])

        # check whether this wall blocks the opponent's last remaining path
        positions = np.array(
            [starting_pos[0], starting_pos[1], second_piece_x, second_piece_y, third_piece_x, third_piece_y])

        copy_state = copy(self)

        if copy_state.is_wall_blocking(positions, not self.player_one):
            return False, np.array([starting_pos[0], starting_pos[1], -1, -1, -1, -1])

        return True, positions

    def is_wall_blocking(self, positions, player_one):
        self.place_wall(positions)
        self.player_one = player_one
        return not A_Star_Search.a_star(self, True)

    def get_available_wall_placements_for_player_one(self, include_state=True):
        wall_placements = []

        if self.player_one_walls_num == 0:
            return wall_placements

        start_row = max(self.player_two_pos[0] - 2, 0)
        end_row = min(self.player_two_pos[0] + 3, 12)
        start_col = max(self.player_one_pos[1] - 3, 0)
        end_col = min(self.player_one_pos[1] + 3, 12)

        # horizontal
        end = end_col - 3
        if end_col == 12:
            end = end_col + 1
        start_1 = start_col + 1
        if start_col == 0:
            start_1 = start_col
            end = end_col - 2
        for i in range(start_row + 1, end_row, 2):
            for j in range(start_1, end, 2):
                if self.is_wall_filled(i, j):
                    continue
                second_part_y = j + 2
                third_part_y = j + 1
                if not start_col <= second_part_y <= end_col:
                    continue
                if not start_col <= third_part_y <= end_col:
                    continue
                if self.is_wall_filled(i, second_part_y):
                    continue
                if self.is_wall_filled(i, third_part_y):
                    continue
                positions = (i, j, i, second_part_y, i, third_part_y)
                if include_state:
                    copy_state = self.copy()
                    if not copy_state.is_wall_blocking(positions, not self.player_one):
                        wall_placements.append((copy_state, positions))
                else:
                    wall_placements.append(positions)
        # vertical
        start_2 = start_col
        if start_2 == 0:
            start_2 = start_col + 1
        for i in range(start_row, end_row - 3, 2):
            for j in range(start_2, end_col + 1, 2):
                if self.is_wall_filled(i, j):
                    continue
                second_part_x = i + 2
                third_part_x = i + 1
                if not start_row <= second_part_x <= end_row:
                    continue
                if not start_row <= third_part_x <= end_row:
                    continue
                if self.is_wall_filled(second_part_x, j):
                    continue
                if self.is_wall_filled(third_part_x, j):
                    continue
                positions = (i, j, second_part_x, j, third_part_x, j)
                if include_state:
                    copy_state = self.copy()
                    if not copy_state.is_wall_blocking(positions, not self.player_one):
                        wall_placements.append((copy_state, positions))
                else:
                    wall_placements.append(positions)

        return wall_placements

    def get_available_wall_placements_for_player_two(self, include_state=True):
        wall_placements = []

        if self.player_two_walls_num == 0:
            return wall_placements


        start_row = max(self.player_one_pos[0] - 3, 0)
        end_row = min(self.player_one_pos[0] + 2, 12)
        start_col = max(self.player_one_pos[1] - 3, 0)
        end_col = min(self.player_one_pos[1] + 3, 12)
        # horizontal
        end = end_col - 3
        if end_col == 12:
            end = end_col + 1
        start_1 = start_col + 1
        if start_col == 0:
            start_1 = start_col
            end = end_col - 2
        for i in range(start_row, end_row, 2):
            for j in range(start_1, end, 2):
                if self.is_wall_filled(i, j):
                    continue
                second_part_y = j + 2
                third_part_y = j + 1
                if not start_col <= second_part_y <= end_col:
                    continue
                if not start_col <= third_part_y <= end_col:
                    continue
                if self.is_wall_filled(i, second_part_y):
                    continue
                if self.is_wall_filled(i, third_part_y):
                    continue
                positions = (i, j, i, second_part_y, i, third_part_y)
                if include_state:
                    copy_state = self.copy()
                    if not copy_state.is_wall_blocking(positions, not self.player_one):
                        wall_placements.append((copy_state, positions))
                else:
                    wall_placements.append(positions)

        # vertical
        start_2 = start_col
        if start_2 == 0 and start_row != 0:
            start_2 = start_col + 1
        if start_2 == 0 and start_row == 0:
            start_2 = start_col
        end_1 = end_col + 1
        if end_col == 12:
            end_1 = 11

        start_3 = start_row + 1
        if start_row == 0:
            start_3 = 0
        for i in range(start_3, end_row - 3, 2):
            for j in range(start_2, end_1, 2):
                if self.is_wall_filled(i, j):
                    continue
                second_part_x = i + 2
                third_part_x = i + 1
                if not start_row <= second_part_x <= end_row:
                    continue
                if not start_row <= third_part_x <= end_row:
                    continue
                if self.is_wall_filled(second_part_x, j):
                    continue
                if self.is_wall_filled(third_part_x, j):
                    continue
                positions = (i, j, second_part_x, j, third_part_x, j)
                if include_state:
                    copy_state = self.copy()
                    if not copy_state.is_wall_blocking(positions, not self.player_one):
                        wall_placements.append((copy_state, positions))
                else:
                    wall_placements.append(positions)
        return wall_placements

    def execute_action(self, action):
        if len(action) == 2:
            self.move_pawn(action)
        else:
            self.place_wall(action)
            print(action)

    def place_wall(self, positions):
        for i in range(0, 5, 2):
            self.board[positions[i] * self.cols + positions[i + 1]] = Status.FILLED_BY_WALL

        if self.player_one:
            self.player_one_walls_num -= 1
        else:
            self.player_two_walls_num -= 1

    def move_pawn(self, new_pos):
        new_i, new_j = new_pos

        if self.player_one:
            old_i, old_j = self.player_one_pos
            self.player_one_pos[0] = new_i
            self.player_one_pos[1] = new_j
            self.board[new_i * self.cols + new_j] = Status.FILLED_BY_PLAYER_1
        else:
            old_i, old_j = self.player_two_pos
            self.player_two_pos[0] = new_i
            self.player_two_pos[1] = new_j
            self.board[new_i * self.cols + new_j] = Status.FILLED_BY_PLAYER_2

        self.board[old_i * self.cols + old_j] = Status.FREE_PLAYER

    def is_end_state(self):
        return self.player_one_pos[0] == 0 or self.player_two_pos[0] == 12

    def game_result(self, player_one_maximizer=False):
        if player_one_maximizer:
            if self.player_one_pos[0] == 0:
                return 1
            else:
                return -1
        else:
            if self.player_two_pos[0] == 12:
                return 1
            else:
                return -1

    def get_winner(self):
        if self.player_one_pos[0] == 0:
            return "P1"
        else:
            return "P2"
