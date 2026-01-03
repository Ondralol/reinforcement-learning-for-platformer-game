"""Implementation of the agent that plays the game"""

import random
import pickle


class Agent:
    def __init__(
        self,
        action_space_size=4,
        visibility_range=5,
        alpha=0.1,
        gamma=0.95,
        epsilon=1.0,
        epsilon_decay=0.9995,
        min_epsilon=0.05,
    ):
        """Initialize the agent and saves its arguments for the agents.

        Args:
            action_space_size: Number of possible actions
            visibility_range: How many tiles in each direction can the agent see
            alpha: Learning rate
            gamma: Discount factor (How much is the future reward valued)
            epsilon: Exploration rate
            epsilon_decay: Decay rate of epsilon
            min_epsilon: Minimal value of epsilon
        """

        self.action_space_size = action_space_size
        self.visibility_range = visibility_range
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.min_epsilon = min_epsilon

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
        if random.uniform(0, 1) < self.epsilon:
            return random.randint(0, self.action_space_size - 1)

        # If we haven't visited this state, set every movement value to zero
        if state_key not in self.q_table:
            self.q_table[state_key] = [0.0] * self.action_space_size

        # Use best known move at the current state, if there are more best moves, choose random
        q_vals = self.q_table[state_key]
        max_q = max(q_vals)
        options = []
        for i, val in enumerate(q_vals):
            if val == max_q:
                options.append(i)

        return random.choice(options)

    def learn(self, state, action, reward, next_state, done):

        state_key = self.get_state_key(state)
        next_state_key = self.get_state_key(next_state)

        # Make sure the state exist in the table
        if state_key not in self.q_table:
            self.q_table[state_key] = [0.0] * self.action_space_size
        if next_state_key not in self.q_table:
            self.q_table[next_state_key] = [0.0] * self.action_space_size

        # Get the current value of the action
        current_q = self.q_table[state_key][action]

        if done:
            target = reward
        else:
            # Find the maximal possible value of the next action
            max_future_q = max(self.q_table[next_state_key])
            target = reward + self.gamma * max_future_q

        # Calculate updated value of current action
        new_q = (1 - self.alpha) * current_q + self.alpha * target

        # Update the table
        self.q_table[state_key][action] = new_q

    def decay_epsilon(self):
        """Decays the epsilon value over time."""
        self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)

    def save_file(self, filename="agent_data.pkl"):
        """Saves the qtable to a file."""
        with open(filename, "wb") as f:
            pickle.dump(self.q_table, f)

    def load_file(self, filename="agent_data.pkl"):
        """Loads the qtable from a file."""
        try:
            with open(filename, "rb") as f:
                self.q_table = pickle.load(f)
                self.epsilon = self.min_epsilon
        except FileNotFoundError:
            print("File doesn't exists")
