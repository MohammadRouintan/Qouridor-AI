from time import sleep
from Agent import Agent
from Environment import Environment, Mappings
from wall_direction import WallDirection
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import print as rprint

class Interface:
    def __init__(self):
        self.player_simulation_algorithms = ["minimax-alpha-beta-pruning", "minimax-alpha-beta-pruning"]
        self.game_state = Environment()
        self.console = Console()
        self.initialize()

    def print_commands(self):
        commands_table = Table(title="Commands", show_header=False, box=None)
        commands_table.add_row("1. Move Pawn", "m: x, y (x=row_name, y=col_name)")
        commands_table.add_row("2. Place Wall", "p: x, y, d (x=row_name, y=col_name, d=direction(n, s, e, w))")
        commands_table.add_row("3. Exit", "exit")
        self.console.print(Panel(commands_table, title="[bold red]Notice[/bold red]", border_style="red"))

    def initialize(self):
        self.console.print(Panel("[bold green]=== QUORIDOR ===", title="Welcome", border_style="green"))
        self.print_commands()
        self.console.print(Panel("[bold blue]Main Menu[/bold blue]", border_style="blue"))
        self.console.print("1. USER vs. AI")
        self.console.print("2. AI vs. AI")

        while True:
            key = self.console.input('Choose an option (1 or 2): ')
            if key == '1':
                self.game_state.is_simulation = False
                break
            elif key == '2':
                self.game_state.is_simulation = True
                break
            else:
                self.console.print("[bold red]Invalid option! Please try again.[/bold red]")

        self.play()

    def player_one_user(self):
        while True:
            value = self.console.input("Enter action (m: x, y or p: x, y, d): ")
            if value == "exit":
                exit(0)
            elif value.lower() == "help":
                self.print_commands()
            else:
                if value.upper().startswith("M"):
                    try:
                        x_string, y_string = value[1:].split(",")
                        x_string = x_string.strip().upper()
                        y_string = y_string.strip().upper()
                        x_string = x_string[-1]
                        y_string = y_string.strip()
                        print(x_string, y_string)
                        if x_string not in Mappings.INPUT_MAPPINGS.keys() or y_string not in Mappings.INPUT_MAPPINGS.keys():
                            self.console.print("[bold red]Invalid input! Please try again.[/bold red]")
                        else:
                            x_int = Mappings.INPUT_MAPPINGS[x_string]
                            y_int = Mappings.INPUT_MAPPINGS[y_string]
                            available_moves = self.game_state.get_available_moves(False)
                            move = (x_int, y_int)
                            if move not in available_moves:
                                self.console.print("[bold red]Invalid move! Please try again.[/bold red]")
                            else:
                                self.game_state.move_pawn(move)
                                break
                    except:
                        self.console.print("[bold red]Invalid format! Please try again.[/bold red]")

                elif value.upper().startswith("P"):
                    try:
                        print(value)
                        x_string, y_string, dir_string = value[1:].split(",")
                        print(x_string, y_string, dir_string)
                        x_string = x_string[-1]
                        y_string = y_string.strip()
                        dir_string = dir_string.stirp()

                        print(x_string, y_string, dir_string)
                        if x_string not in Mappings.INPUT_MAPPINGS.keys() or y_string not in Mappings.INPUT_MAPPINGS.keys():
                            self.console.print("[bold red]Invalid input! Please try again.[/bold red]")
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

                                x_int = Mappings.INPUT_MAPPINGS[x_string]
                                y_int = Mappings.INPUT_MAPPINGS[y_string]
                                is_placement_valid, coords = self.game_state.check_wall_placement((x_int, y_int), direction)
                                if not is_placement_valid:
                                    self.console.print("[bold red]Invalid wall placement! Please try again.[/bold red]")
                                else:
                                    self.game_state.place_wall(coords)
                                    break
                            else:
                                self.console.print("[bold red]Invalid direction! Please try again.[/bold red]")
                    except:
                        self.console.print("[bold red]Invalid format! Please try again.[/bold red]")

                else:
                    self.console.print("[bold red]Invalid action! Please try again.[/bold red]")

    def player_simulation(self, player_number):
        if player_number == 1:
            index = 0
            maximizer = True
        else:
            index = 1
            maximizer = False

        agent = Agent(self.player_simulation_algorithms[index])
        action = agent.get_action(maximizer, self.game_state)
        self.game_state.execute_action(action)

        if action is not None:
            if len(action) == 2:
                self.console.print(f"[bold cyan]Player {player_number} has moved his pawn.[/bold cyan]")
            else:
                self.console.print(f"[bold cyan]Player {player_number} has placed a wall.[/bold cyan]")
            return True
        else:
            self.console.print(f"[bold cyan]Player {player_number} has no moves left.[/bold cyan]")
            return False

    def check_end_state(self):
        if self.game_state.is_end_state():
            winner = self.game_state.get_winner()
            if not self.game_state.is_simulation:
                if winner == "P1":
                    self.console.print("[bold green]You won![/bold green]")
                else:
                    self.console.print("[bold red]You lost![/bold red]")
            else:
                self.console.print(f"[bold cyan]The winner is {winner}.[/bold cyan]")
            return True
        else:
            return False

    def play(self):
        while True:
            self.console.print()
            self.game_state.print_game_stats()
            self.console.print("\n")
            self.game_state.print_board()
            self.console.print()

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
        rprint(f"[{color}]{text}[/{color}]")