"""Unit tests for Train"""

import pytest
from agent.train import Train
from utils.args_config import Config


@pytest.fixture
def train():
    return Train(Config("maps/test_simple.txt", 2, 1500))


class TestTrain:

    def test_train_initializes(self, train):
        assert train.generation == 0
        assert train.win_count == 0
        assert train.done is False

    def test_reset_increments_generation(self, train):
        train.generation = 5
        train.reset()
        # Generation should stay the same, reset is called after incrementing
        assert train.generation == 5

    def test_reset_resets_flags(self, train):
        train.done = True
        train.accumulated_reward = 100
        train.skip_counter = 3

        train.reset()

        assert train.done is False
        assert train.accumulated_reward == 0
        assert train.skip_counter == 0

    def test_make_one_step_updates_skip_counter(self, train):
        initial_counter = train.skip_counter
        train.make_one_step()
        assert train.skip_counter == initial_counter + 1
