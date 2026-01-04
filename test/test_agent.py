"""Unit tests for Agent"""

import pytest
from agent.agent import Agent, Transition, Parameters


@pytest.fixture
def agent():
    """Create a basic agent instance."""
    return Agent(
        Parameters(action_space_size=4, alpha=0.2, epsilon=1.0, gamma=0.999, epsilon_decay=0.99, min_epsilon=0.001)
    )


@pytest.fixture
def simple_state():
    """Return a simple game state."""
    return [[0, 0, 1], [0, 0, 0], [1, 1, 1], [0, 1, 0, 1]]


class TestAgent:

    def test_agent_initializes(self, agent):
        assert agent.parameters.action_space_size == 4
        assert agent.parameters.epsilon == 1.0
        assert agent.q_table == {}

    def test_custom_parameters(self):
        agent = Agent(
            Parameters(action_space_size=3, alpha=0.2, epsilon=0.5, gamma=0.999, epsilon_decay=4, min_epsilon=200)
        )
        assert agent.parameters.action_space_size == 3
        assert agent.parameters.alpha == 0.2
        assert agent.parameters.epsilon == 0.5
        assert agent.parameters.gamma == 0.999
        assert agent.parameters.epsilon_decay == 4
        assert agent.parameters.min_epsilon == 200

    def test_get_get_state_key(self, agent, simple_state):
        key1 = agent.get_state_key(simple_state)
        key2 = agent.get_state_key(simple_state)
        assert isinstance(key1, tuple)
        assert key1 == key2

    def test_different_states_give_different_keys(self, agent):
        state1 = [[0, 1], [1, 0]]
        state2 = [[1, 0], [0, 1]]

        key1 = agent.get_state_key(state1)
        key2 = agent.get_state_key(state2)
        assert key1 != key2

    def test_choose_action_returns_valid_number(self, agent, simple_state):
        action = agent.choose_action(simple_state)
        assert 0 <= action < 4  # This will fail if we add more actions

    def test_zero_epsilon_chooses_best_action(self, agent, simple_state):
        agent.parameters.epsilon = 0.0
        state_key = agent.get_state_key(simple_state)
        agent.q_table[state_key] = [1.0, 5.0, 2.0, 3.0]

        action = agent.choose_action(simple_state)
        assert action == 1  # Index with highest value


class TestLearn:

    def test_learn_creates_q_table_entry(self, agent, simple_state):
        next_state = [[1, 1], [0, 0], [1, 1], [1, 0, 0, 0]]

        agent.learn(Transition(action=2, state=simple_state, reward=10, next_state=next_state, done=False))

        state_key = agent.get_state_key(simple_state)
        assert state_key in agent.q_table

    def test_learn_updates_q_value(self, agent, simple_state):
        next_state = [[0, 0], [0, 0], [0, 0], [0]]

        agent.learn(Transition(action=1, state=simple_state, reward=10, next_state=next_state, done=False))

        state_key = agent.get_state_key(simple_state)
        assert agent.q_table[state_key][1] > 0


class TestEpsilonDecay:

    def test_decay_reduces_epsilon(self, agent):
        initial = agent.parameters.epsilon
        agent.decay_epsilon()
        assert agent.parameters.epsilon < initial

    def test_decay_respects_minimum(self, agent):
        agent.parameters.epsilon = agent.parameters.min_epsilon
        agent.decay_epsilon()
        assert agent.parameters.epsilon == agent.parameters.min_epsilon


class TestSaveLoad:

    def test_save_and_load(self, agent, simple_state, tmp_path):
        filename = tmp_path / "test.pkl"

        state_key = agent.get_state_key(simple_state)
        agent.q_table[state_key] = [1.0, 2.0, 3.0, 4.0]
        agent.save_file(str(filename))

        new_agent = Agent(
            Parameters(action_space_size=3, alpha=0.2, epsilon=0.5, gamma=0.999, epsilon_decay=4, min_epsilon=200)
        )
        new_agent.load_file(str(filename))

        assert new_agent.q_table[state_key] == [1.0, 2.0, 3.0, 4.0]

    def test_load_missing_file_doesnt_crash(self, agent):
        agent.load_file("nonexistent.pkl")
        # Should just print message, not crash
