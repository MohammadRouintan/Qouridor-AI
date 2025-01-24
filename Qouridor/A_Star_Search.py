from queue import PriorityQueue
from dataclasses import dataclass, field
from typing import Any
import copy

@dataclass(order=True)
class PriorityQueueItem:
    priority: int
    item: Any = field(compare=False)

def h(game_state):
    if game_state.player_one:
        return 100 * abs(game_state.player_one_pos[0])
    else:
        return 100 * (abs(game_state.player_two_pos[0] - 12))


def g(path):
    actions = []
    current_cost = 0
    for state in path:
        current_cost += state[1][2]
    current_cost += len(actions)
    current_cost += h(path[-1][0])
    return current_cost


def a_star(game_state, check_blockage):
    visited = set()

    queue = PriorityQueue()
    if game_state.player_one:
        pos = game_state.player_one_pos
    else:
        pos = game_state.player_two_pos

    queue.put(PriorityQueueItem(0, [(game_state, ((pos[0], pos[1]), (0, 0), 0))]))

    while not queue.empty():
        item = queue.get()
        path = item.item
        current_state = path[-1][0]
        current_simplified_state = path[-1][1]
        if current_state.is_goal_state():
            if check_blockage:
                return True
            final_path = []
            for state in path:
                final_path.append(state[1][1])
            return len(final_path[1:])
        if current_simplified_state not in visited:
            visited.add(current_simplified_state)
            for successor in current_state.get_child_states_with_moves():
                if successor[1] not in visited:
                    successor_path = copy.copy(path)
                    successor_path.append(successor)
                    queue.put(PriorityQueueItem(g(successor_path), successor_path))
    if check_blockage:
        return False
    return 0

