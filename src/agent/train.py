"""Trains the agent"""

from dataclasses import dataclass, field

from game.game import Game
from agent.agent import Agent, Transition, Parameters
from utils.args_config import Config

GENERATIONS = 100000
# MAX_STEPS = 1500 # 1500 is the best for normal sized maps // Deprecated
FRAME_SKIP = 4  # How many frames does the agent hold a key


@dataclass
class TrainStats:
    """Training statistics."""

    generation: int = 0
    win_count: int = 0


@dataclass
class TrainState:
    """Training state."""

    done: bool = False
    total_reward: float = 0.0
    state: list = field(default_factory=list)
    skip_counter: int = 0
    accumulated_reward: int = 0
    action_idx: int = 0


class Train:
    """Training class that controls how the Agent trains"""

    def __init__(self, config: Config):
        """Initializes the training process.

        Arguments:
            config: CLI Arguments
        """
        self.game = Game(config)
        self.agent = Agent(Parameters())
        self.config = config
        self.training_stats = TrainStats()

        self.training_state = TrainState(state=self.game.get_state(self.config.visibility))

    def reset(self):
        """Resets the training.

        Reset all states, updates epsilon value and restarts the game
        """
        # Reset necessary states
        self.training_state.done = False
        self.training_state.accumulated_reward = 0
        self.training_state.skip_counter = 0
        self.agent.decay_epsilon()
        self.game.restart_game()

    def make_one_step(self):
        """Makes one training step of the agent.

        Using FRAME_SKIP so agent can "hold" movement for more than one frames, apparently its good for reducing jitter
        The logic needs to match the visualisation, so the implementation is little bit akward on this side
        """

        # Picks new move every FRAME_SKIP frames
        if self.training_state.skip_counter == 0:
            self.training_state.state = self.game.get_state(self.config.visibility)
            self.training_state.action_idx = self.agent.choose_action(self.training_state.state)
            self.training_state.accumulated_reward = 0

        # Make a move
        next_state, reward, self.training_state.done = self.game.step(self.training_state.action_idx)
        self.training_state.total_reward += reward
        self.training_state.accumulated_reward += reward
        self.training_state.skip_counter += 1

        # Learn after FRAME_SKIP frames
        if self.training_state.skip_counter >= FRAME_SKIP or self.training_state.done:
            self.agent.learn(
                Transition(
                    state=self.training_state.state,
                    action=self.training_state.action_idx,
                    reward=self.training_state.accumulated_reward,
                    next_state=next_state,
                    done=self.training_state.done,
                )
            )
            self.training_state.skip_counter = 0

        if (
            self.game.game_state.steps > self.config.max_steps
            or self.game.game_state.game_completed
            or self.game.game_state.game_over
        ):
            if self.game.game_state.game_completed:
                self.training_stats.win_count += 1
            self.training_state.done = True

        if self.training_state.done:
            self.reset()
            self.training_stats.generation += 1
