from time import time, sleep
import math
from Agent import Agent
from Environment import Environment, Mappings
from Color import Color
from wall_direction import WallDirection

class Interface:
    def __init__(self):

        self.player_simulation_algorithms = ["minimax", "minimax"]
        self.game_state = Environment()
        self.algorithms = ["minimax", "minimax-alpha-beta-pruning"]

        self.initialize()

    def print_commands(self):
        Interface.print_colored_output("Notice:", Color.RED)
        print("1. Moving Pawn => m: x, y (x=row_name, y=col_name)")
        print("2. Placing Wall => p: x, y, d (x=row_name, y=col_name, d=direction(n, s, e, w)")
        print("3. Exit => exit")

    def initialize(self):
        Interface.print_colored_output("QUORIDOR", Color.GREEN)
        print()

        self.print_commands()
        print("{0:-<100}".format(""))

        Interface.print_colored_output("Main Menu", Color.BLUE)
        print("1. USER vs. AI")
        print("2. AI vs. AI")
        print()

        flag = False
        while True:
            key = input('Choose an option: ')
            print()
            if key == '1':
                self.game_state.is_simulation = False

                Interface.print_colored_output("Algorithm Menu", Color.BLUE)
                print("1. Minimax")
                print("2. Minimax with alpha beta pruning")
                print()
                while True:
                    x = input("Choose an option: ")
                    if not x.isdigit() and x != "exit":
                        Interface.print_colored_output("Enter again !!!!", Color.RED)
                    elif x == "exit":
                        exit(0)
                    else:
                        if 0 <= int(x) - 1 < len(self.algorithms):
                            self.player_simulation_algorithms[1] = self.algorithms[int(x) - 1]
                            flag = True
                            break
                        else:
                            Interface.print_colored_output("Enter again !!!!", Color.RED)
                if flag:
                    break

            elif key == '2':
                self.game_state.is_simulation = True
                Interface.print_colored_output("Algorithm Menu", Color.BLUE)
                print("1. Minimax")
                print("2. Minimax with alpha beta pruning")
                print()
                while True:
                    x = input("Choose an option: ")
                    if not len(x.split(",")) == 2 and x != "exit":
                        Interface.print_colored_output("Enter again !!!!", Color.RED)
                    elif x == "exit":
                        exit(0)
                    else:
                        one, two = x.split(",")
                        if 0 <= int(one) - 1 < len(self.algorithms) and 0 <= int(two) - 1 < len(self.algorithms):
                            self.player_simulation_algorithms[0] = self.algorithms[int(one) - 1]
                            self.player_simulation_algorithms[1] = self.algorithms[int(two) - 1]
                            flag = True
                            break
                        else:
                            Interface.print_colored_output("Enter again !!!!", Color.RED)
                if flag:
                    break
            else:
                Interface.print_colored_output("Enter again !!!!", Color.RED)

    def player_one_user(self):
        while True:
            value = input("Enter action: ")
            if value == "exit":
                exit(0)
            elif value.lower() == "help":
                print()
                self.print_commands()
                print()
            else:
                if value.upper().startswith("M"):
                    x_string, y_string = value[1:].split(",")
                    x_string = x_string[-1]
                    y_string = y_string.strip()
                    if x_string.upper() not in Mappings.INPUT_MAPPINGS.keys() or y_string.upper() not in Mappings.INPUT_MAPPINGS.keys():
                        Interface.print_colored_output("Enter again !!!!", Color.RED)
                    else:
                        x_int = Mappings.INPUT_MAPPINGS[x_string.upper()]
                        y_int = Mappings.INPUT_MAPPINGS[y_string.upper()]
                        available_moves = self.game_state.get_available_moves(False)
                        move = (x_int, y_int)
                        if move not in available_moves:
                            Interface.print_colored_output("Enter again !!!!", Color.RED)
                        else:
                            self.game_state.move_pawn(move)
                            break

                elif value.upper().startswith("W"):
                    x_string, y_string, dir_string = value[1:].split(",")
                    x_string = x_string[-1]
                    y_string = y_string.strip()
                    dir_string = dir_string.strip()
                    if x_string.upper() not in Mappings.INPUT_MAPPINGS.keys() or y_string.upper() not in Mappings.INPUT_MAPPINGS.keys():
                        Interface.print_colored_output("Enter again !!!!", Color.RED)
                    else:
                        if dir_string.upper() in ["N", "S", "E", "W"]:

                            if dir_string.upper() == "S":
                                direction = WallDirection.SOUTH
                            elif dir_string.upper() == "E":
                                direction = WallDirection.EAST
                            elif dir_string.upper() == "W":
                                direction = WallDirection.WEST
                            else:
                                direction = WallDirection.NORTH

                            x_int = Mappings.INPUT_MAPPINGS[x_string.upper()]
                            y_int = Mappings.INPUT_MAPPINGS[y_string.upper()]
                            is_placement_valid, coords = self.game_state.check_wall_placement((x_int, y_int),
                                                                                              direction)
                            if not is_placement_valid:
                                Interface.print_colored_output("Enter again !!!!", Color.RED)
                            else:
                                self.game_state.place_wall(coords)
                                break

                else:
                    Interface.print_colored_output("Enter again !!!!", Color.RED)

    def player_simulation(self, player_number):
        if player_number == 1:
            index = 0
            maximizer = True
        else:
            index = 1
            maximizer = False

        action = (0, 0)
        agent = Agent(self.player_simulation_algorithms[index])
        action = agent.get_action(maximizer, self.game_state)
        self.game_state.execute_action(action)

        if action is not None:
            if len(action) == 2:
                self.print_colored_output("Player {0:1} has moved his pawn.".format(player_number), Color.CYAN)
            else:
                self.print_colored_output("Player {0:1} has placed a wall.".format(player_number), Color.CYAN)
            return True
        else:
            self.print_colored_output("Player {0:1} has no moves left.".format(player_number), Color.CYAN)
            return False

    def check_end_state(self):
        if self.game_state.is_end_state():
            winner = self.game_state.get_winner()
            if not self.game_state.is_simulation:
                if winner == "P1":
                    self.print_colored_output("You won!", Color.GREEN)
                else:
                    self.print_colored_output("You lost!", Color.RED)
            else:
                self.print_colored_output("The winner is " + winner + ".", Color.CYAN)
            return True
        else:
            return False

    def play(self):
        while True:
            print()
            self.game_state.print_game_stats()
            print("\n")
            self.game_state.print_board()
            print()

            if self.check_end_state():
                break

            if self.game_state.player_one:
                if not self.game_state.is_simulation:
                    self.player_one_user()
                else:
                    res = self.player_simulation(1)
                    sleep(1.5)
                    if not res:
                        break
            else:
                res = self.player_simulation(2)
                if not res:
                    break

            self.game_state.player_one = not self.game_state.player_one

    @staticmethod
    def print_colored_output(text, color):
        print(color + text + Color.RESET)