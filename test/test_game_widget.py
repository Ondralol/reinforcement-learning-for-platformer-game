"""Tests for game widget"""

# Since its mostly UI, there is no point in testing the UI itself, I will be testing just the logic that needs testing


import pytest
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from gui.game_widget import MapWidget
from game.game import Game
from utils.args_config import Config


@pytest.fixture(scope="session", autouse=True)
def qapp():
    """Ensure a QApplication exists for the duration of the tests. (Apparently it's needed for Qt)"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


@pytest.fixture
def map_widget_agent():
    """Create GameWidget instance."""
    config = Config("test/maps/test_simple.txt", 2, 1500)
    return MapWidget(None, Game(config), config, agent=True)


@pytest.fixture
def map_widget_player():
    """Create GameWidget instance."""
    config = Config("test/maps/test_simple.txt", 2, 1500)
    return MapWidget(None, Game(config), config, agent=False)


class TestMapWidgetInitialization:

    def test_agent_playing_initialization(self, map_widget_agent):
        assert map_widget_agent.agent is True

    def test_player_playing_initialization(self, map_widget_player):
        assert map_widget_player.agent is False


class TestMapWidgetGameLoop:

    def test_game_loop_agent_playing_makes_progress(self, map_widget_agent):
        prev_agent_state = map_widget_agent.train.agent.q_table.copy()
        map_widget_agent.game_loop()
        assert prev_agent_state != map_widget_agent.train.agent.q_table

    def test_game_loop_player_playing_makes_progress(self, map_widget_player):
        # Makes a move to the right
        prev_x = map_widget_player.game.x
        map_widget_player.pressed_keys.add(Qt.Key_D)
        map_widget_player.game_loop()
        map_widget_player.game_loop()
        map_widget_player.game_loop()

        assert prev_x != map_widget_player.game.x
