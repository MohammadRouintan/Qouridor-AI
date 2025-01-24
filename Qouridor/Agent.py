import math
from Environment import Environment
import A_Star_Search

class Agent:
    def __init__(self, strategy='minimax'):
        self.env = None
        self.strategy = strategy

    def get_action(self, maximizer, env):
        agent_action = None
        self.env = env

        if self.strategy == 'minimax':
            agent_action = self.agent(maximizer, is_alpha_beta=False)
        elif self.strategy == 'minimax-alpha-beta-pruning':
            agent_action = self.agent(maximizer, is_alpha_beta=True)

        return agent_action

    def agent(self, player, is_alpha_beta):
        d = {}
        for child in self.env.get_all_child_states(player):
            if not is_alpha_beta:
                value = self.minimax(child[0], 5, is_max_player=False, player=player)
            else:
                value = self.minimax_alpha_beta_pruning(child[0], 5, -math.inf, math.inf, is_max_player=False, player=player)

            d[value] = child

        if len(d.keys()) == 0:
            return None

        maximum = max(d)
        best = d[maximum]
        action = best[1]

        return action
    
    def minimax(self, game_state: Environment, depth, is_max_player, player):
        if depth == 0:
            return self.eval_func(game_state, player)
        if is_max_player:
            max_eval = -math.inf
            for child in game_state.get_all_child_states(player):
                ev = self.minimax(child[0], depth - 1, False, player)
                max_eval = max(max_eval, ev)
            game_state.value = max_eval
            return max_eval
        else:
            min_eval = math.inf
            for child in game_state.get_all_child_states(player):
                ev = self.minimax(child[0], depth - 1, True, player)
                min_eval = min(min_eval, ev)
            game_state.value = min_eval
            return min_eval

    def minimax_alpha_beta_pruning(self, game_state: Environment, depth, alpha, beta, is_max_player, player):
        if depth == 0:
            return self.eval_func(game_state, player)
        if is_max_player:
            max_eval = -math.inf
            for child in game_state.get_all_child_states(player):
                ev = self.minimax_alpha_beta_pruning(child[0], depth - 1, alpha, beta, False, player)
                max_eval = max(max_eval, ev)
                alpha = max(alpha, ev)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = math.inf
            for child in game_state.get_all_child_states(player):
                ev = self.minimax_alpha_beta_pruning(child[0], depth - 1, alpha, beta, True, player)
                min_eval = min(min_eval, ev)
                beta = min(beta, ev)
                if beta <= alpha:
                    break
            return min_eval

    def eval_func(self, game_state: Environment, is_player_one_maximizer):
        player_one_distance_to_goal = game_state.player_one_pos[0] // 2
        player_two_distance_to_goal = (12 - game_state.player_two_pos[0]) // 2
        score = 0

        if is_player_one_maximizer:
            opponent_path_to_goal_len, player_path_to_goal_len = player_two_distance_to_goal, player_one_distance_to_goal
            if game_state.player_one_walls_num != 10 and game_state.player_two_walls_num != 10:
                previous = game_state.player_one
                game_state.player_one = True
                player_path_to_goal_len = A_Star_Search.a_star(game_state, False)
                game_state.player_one = previous

            score += 10 * opponent_path_to_goal_len
            score -= player_one_distance_to_goal

            divisor = 100
            if player_path_to_goal_len != 0:
                divisor = player_path_to_goal_len
            score += round(100 / divisor, 2)

            divisor = 50
            if player_two_distance_to_goal != 0:
                divisor = player_two_distance_to_goal
            score -= round(50 / divisor, 2)

            score += (game_state.player_one_walls_num - game_state.player_two_walls_num)
            if game_state.player_one_pos[0] == 0:
                score += 100
            if player_path_to_goal_len == 0 and game_state.player_one_pos[0] != 0:
                score -= 500

            return score
        else:
            opponent_path_to_goal_len, player_path_to_goal_len = player_one_distance_to_goal, player_two_distance_to_goal
            if game_state.player_one_walls_num != 10 and game_state.player_two_walls_num != 10:
                previous = game_state.player_one
                game_state.player_one = False
                player_path_to_goal_len = A_Star_Search.a_star(game_state, False)
                game_state.player_one = previous

            score += 10 * opponent_path_to_goal_len
            score -= player_two_distance_to_goal

            divisor = 100
            if player_path_to_goal_len != 0:
                divisor = player_path_to_goal_len
            score += round(100 / divisor, 2)

            divisor = 50
            if player_one_distance_to_goal != 0:
                divisor = player_one_distance_to_goal
            score -= round(50 / divisor, 2)

            score += (game_state.player_two_walls_num - game_state.player_one_walls_num)
            if game_state.player_two_pos[0] == 12:
                score += 100
            if player_path_to_goal_len == 0 and game_state.player_two_pos[0] != 12:
                score -= 500

            return score

