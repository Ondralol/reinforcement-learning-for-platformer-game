"""Implementation of the agent that plays the game"""

import random
import pickle
from dataclasses import dataclass, field


@dataclass
class Parameters:
    """Parameters for the agent"""

    action_space_size: int = 4  # Number of possible actions
    visibility_range: int = 2  # How many tiles in each direction can the agent see
    alpha: float = 0.1  # Learning rate
    gamma: float = 0.95  # Discount factor (How much is the future reward valued)
    epsilon: float = 1.0  # Exploration rate
    epsilon_decay: float = 0.9998  # Decay rate of epsilon
    min_epsilon: float = 0.001  # Minimal value of epsilon


@dataclass
class Transition:
    """Wrapper for passing arguments for learn method of Agent"""

    action: int
    reward: float
    done: bool
    state: list = field(default_factory=list)
    next_state: list = field(default_factory=list)

    def __iter__(self):
        """To enable unpacking"""
        yield self.state
        yield self.action
        yield self.reward
        yield self.next_state
        yield self.done


class Agent:
    """Agent class that handles learning how to play the game"""

    def __init__(self, params):
        """Initialize the agent and saves its arguments for the agents.

        Args:
            params: Parameters for the agent
        """
        # Store parameters
        self.parameters = params
        print(self.parameters.visibility_range)
        # Map that stores state and value for every movement at that state
        self.q_table = {}

    def get_state_key(self, state):
        """Returns tuple from the state.
        Args:
            state: Current game state
        """

        flattened = []
        for col in state:
            for cell in col:
                flattened.append(cell)
        return tuple(flattened)

    def choose_action(self, state):
        """Decides whch action to explore or exploit.

        Args:
            state: Current game state
        """

        state_key = self.get_state_key(state)

        # If we should make a random move
        if random.uniform(0, 1) < self.parameters.epsilon:
            return random.randint(0, self.parameters.action_space_size - 1)

        # If we haven't visited this state, set every movement value to zero
        if state_key not in self.q_table:
            self.q_table[state_key] = [0.0] * self.parameters.action_space_size

        # Use best known move at the current state, if there are more best moves, choose random
        q_vals = self.q_table[state_key]
        max_q = max(q_vals)
        options = []
        for i, val in enumerate(q_vals):
            if val == max_q:
                options.append(i)

        return random.choice(options)

    def learn(self, transition: Transition):
        """Update best values for a action at a specific state."""

        state, action, reward, next_state, done = transition

        state_key = self.get_state_key(state)
        next_state_key = self.get_state_key(next_state)

        # Make sure the state exist in the table
        if state_key not in self.q_table:
            self.q_table[state_key] = [0.0] * self.parameters.action_space_size
        if next_state_key not in self.q_table:
            self.q_table[next_state_key] = [0.0] * self.parameters.action_space_size

        # Get the current value of the action
        current_q = self.q_table[state_key][action]

        if done:
            target = reward
        else:
            # Find the maximal possible value of the next action
            max_future_q = max(self.q_table[next_state_key])
            target = reward + self.parameters.gamma * max_future_q

        # Calculate updated value of current action
        new_q = (1 - self.parameters.alpha) * current_q + self.parameters.alpha * target

        # Update the table
        self.q_table[state_key][action] = new_q

    def decay_epsilon(self):
        """Decays the epsilon value over time."""
        self.parameters.epsilon = max(
            self.parameters.min_epsilon, self.parameters.epsilon * self.parameters.epsilon_decay
        )

    def save_file(self, filename="agent_data.pkl"):
        """Saves the qtable to a file.

        Currently not used, in future it can be used to save the best moves
        """
        with open(filename, "wb") as f:
            pickle.dump(self.q_table, f)

    def load_file(self, filename="agent_data.pkl"):
        """Loads the qtable from a file.

        Currently not used, in future it can be used to load the best moves that agent has previously learned
        """
        try:
            with open(filename, "rb") as f:
                self.q_table = pickle.load(f)
                self.parameters.epsilon = self.parameters.min_epsilon
        except FileNotFoundError:
            print("File doesn't exists")
