"""Trains the agent"""

from game.game import Game
from agent.agent import Agent
from utils.args_config import Config

GENERATIONS = 100000
# MAX_STEPS = 1500 # 1500 is the best for normal sized maps // Deprecated
FRAME_SKIP = 4  # How many frames does the agent hold a key


class Train:
    """Training class that controls how the Agent trains"""

    def __init__(self, config: Config):
        """Initializes the training process.

        Arguments:
            config: CLI Arguments
        """
        self.game = Game(config)
        self.agent = Agent()
        self.config = config
        self.done = False
        self.total_reward = 0
        self.state = self.game.get_state()

        self.generation = 0
        self.win_count = 0
        self.skip_counter = 0

        self.accumulated_reward = 0
        self.action_idx = 0

    def reset(self):
        """Resets the training.

        Reset all states, updates epsilon value and restarts the game
        """
        # Might seem like duplication, but we don't initially decay the epsilon
        self.done = False
        self.accumulated_reward = 0
        self.skip_counter = 0
        self.agent.decay_epsilon()
        self.game.restart_game()

    def make_one_step(self):
        """Makes one training step of the agent.

        Using FRAME_SKIP so agent can "hold" movement for more than one frames, apparently its good for reducing jitter
        The logic needs to match the visualisation, so the implementation is little bit akward on this side
        """

        # Picks new move every FRAME_SKIP frames
        if self.skip_counter == 0:
            self.state = self.game.get_state()
            self.action_idx = self.agent.choose_action(self.state)
            self.accumulated_reward = 0

        # Make a move
        next_state, reward, self.done = self.game.step(self.action_idx)
        self.total_reward += reward
        self.accumulated_reward += reward
        self.skip_counter += 1

        # Learn after FRAME_SKIP frames
        if self.skip_counter >= FRAME_SKIP or self.done:
            self.agent.learn(self.state, self.action_idx, self.accumulated_reward, next_state, self.done)
            self.skip_counter = 0

        if self.game.steps > self.config.max_steps or self.game.game_completed or self.game.game_over:
            if self.game.game_completed:
                self.win_count += 1
            self.done = True

        if self.done:
            self.reset()
            self.generation += 1
