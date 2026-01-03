"""Trains the agent"""

from game.game import Game
from agent.agent import Agent

EPISODES = 100000
MAX_STEPS = 10000


class Train:
    def __init__(self):
        self.game = Game()
        self.agent = Agent()
        self.done = False
        self.total_reward = 0
        self.state = self.game.get_state()

        self.generation = 0
        self.win_count = 0

    def reset(self):
        # Might seem like duplication, but we don't initially decay the epsilon
        self.done = False
        self.total_reward = 0
        self.agent.decay_epsilon()
        self.game.restart_game()

    def make_step(self, step_size):
        """Trains the agent."""
        state = self.game.get_state()
        for i in range(step_size):
            action_idx = self.agent.choose_action(state)

            next_state, reward, self.done = self.game.step(action_idx)

            self.agent.learn(state, action_idx, reward, next_state, self.done)
            state = next_state
            self.total_reward += reward

            if self.game.steps > MAX_STEPS or self.game.game_completed or self.game.game_over:
                if self.game.game_completed:
                    self.win_count += 1
                self.done = True
                break

        if self.done:
            self.reset()
            self.generation += 1
