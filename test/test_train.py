"""Unit tests for Train"""

import pytest
from agent.train import Train
from utils.args_config import Config


@pytest.fixture
def train():
    return Train(Config("test/maps/test_simple.txt", 2, 1500))


class TestTrain:

    def test_train_initializes(self, train):
        assert train.training_stats.generation == 0
        assert train.training_stats.win_count == 0
        assert train.training_state.done is False

    def test_reset_increments_generation(self, train):
        train.training_stats.generation = 5
        train.reset()
        # Generation should stay the same, reset is called after incrementing
        assert train.training_stats.generation == 5

    def test_reset_resets_flags(self, train):
        train.training_state.done = True
        train.training_state.accumulated_reward = 100
        train.training_state.skip_counter = 3

        train.reset()

        assert train.training_state.done is False
        assert train.training_state.accumulated_reward == 0
        assert train.training_state.skip_counter == 0

    def test_make_one_step_updates_skip_counter(self, train):
        initial_counter = train.training_state.skip_counter
        train.make_one_step()
        assert train.training_state.skip_counter == initial_counter + 1
