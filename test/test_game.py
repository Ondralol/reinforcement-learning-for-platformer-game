"""Unit tests for game logic"""

import pytest
import numpy as np
from game.game import Game, MovementDirection, TILE_SIZE, GRAVITY, JUMP_STRENGTH, MOVE_SPEED, MAX_FALLING_SPEED

from utils.args_config import Config


@pytest.fixture
def game_simple():
    """Creates a game with simple map."""
    return Game(Config("test/maps/test_simple.txt", 2, 1500))


@pytest.fixture
def game_coin():
    """Creates a game with coin map."""
    return Game(Config("test/maps/test_coin.txt", 2, 1500))


@pytest.fixture
def game_void():
    """Creates a game with void map."""
    return Game(Config("test/maps/test_void.txt", 2, 1500))


class TestGameInitialization:

    def test_initialize_game_with_config(self, game_simple):

        assert game_simple.persistant_states.config == Config("test/maps/test_simple.txt", 2, 1500)
        assert game_simple.game_state.progress.best_step_count == float("inf")
        assert game_simple.persistant_states.total_best_distance == float("inf")

        # Assert player initial position
        assert game_simple.map_state.start_x == 0
        assert game_simple.map_state.start_y == TILE_SIZE * 2
        assert game_simple.player_state.x == 0
        assert game_simple.player_state.y == TILE_SIZE * 2

    def test_load_map(self, game_simple):
        assert game_simple.map_state.height == 4
        assert game_simple.map_state.width == 8
        assert len(game_simple.map_state.map) == 4
        assert len(game_simple.map_state.map[0]) == 8

    def test_replace_start_with_air(self, game_simple):
        assert game_simple.map_state.map[2][0] == "."

    def test_find_end_position(self, game_simple):
        assert np.array_equal(game_simple.map_state.end_pos, np.array([6, 2]))


class TestMapQueries:

    def test_get_tile_returns_correct_tile(self, game_simple):
        assert game_simple.get_tile(6, 2) == "E"
        assert game_simple.get_tile(0, 3) == "#"
        assert game_simple.get_tile(1, 0) == "."

    def test_get_tile_out_of_bounds(self, game_simple):
        assert game_simple.get_tile(-1, 0) == "None"
        assert game_simple.get_tile(0, -1) == "None"
        assert game_simple.get_tile(100, 100) == "None"

    def test_detects_walls(self, game_simple):
        assert game_simple.is_wall(0, 3) is True
        assert game_simple.is_wall(1, 1) is False
        assert game_simple.is_wall(-1, 0) is True


class TestPhysics:

    def test_gravity(self, game_simple):
        game_simple.player_state.y = 0
        initial_vel_y = game_simple.player_state.vel_y
        game_simple.player_state.on_ground = False
        game_simple.update(MovementDirection.IDLE)
        assert game_simple.player_state.vel_y == initial_vel_y + GRAVITY

    def test_jump_sets_velocity(self, game_simple):
        game_simple.player_state.on_ground = True
        game_simple.update(MovementDirection.JUMP)

        assert game_simple.player_state.vel_y == JUMP_STRENGTH + GRAVITY
        assert game_simple.player_state.on_ground is False

    def test_cannot_jump_when_not_on_ground(self, game_simple):
        game_simple.player_state.on_ground = False
        game_simple.update(MovementDirection.JUMP)

        assert game_simple.player_state.vel_y != JUMP_STRENGTH

    def test_horizontal_movement_left(self, game_simple):
        game_simple.player_state.x = TILE_SIZE * 2
        game_simple.player_state.y = TILE_SIZE
        initial_x = game_simple.player_state.x
        game_simple.update(MovementDirection.LEFT)
        assert game_simple.player_state.x < initial_x

    def test_horizontal_movement_right(self, game_simple):
        game_simple.player_state.x = TILE_SIZE * 2
        game_simple.player_state.y = TILE_SIZE
        initial_x = game_simple.player_state.x
        game_simple.update(MovementDirection.RIGHT)
        assert game_simple.player_state.x > initial_x

    def test_max_falling_speed_limit(self, game_simple):
        game_simple.player_state.vel_y = MAX_FALLING_SPEED + 10
        game_simple.update(MovementDirection.IDLE)

        assert game_simple.player_state.vel_y <= MAX_FALLING_SPEED

    def test_velocity_sliding_effect(self, game_simple):
        game_simple.player_state.vel_x = 2.0
        game_simple.update(MovementDirection.IDLE)

        assert 0 <= game_simple.player_state.vel_x < 2.0


class TestCollisions:

    def test_floor_collision(self, game_simple):
        game_simple.player_state.y = -100
        game_simple.player_state.vel_y = 5.0
        game_simple.check_collisions(x_axis=False)

        assert game_simple.player_state.on_ground is True
        assert game_simple.player_state.vel_y == 0

    def test_wall_collision_stops_horizontal_movement(self, game_simple):
        game_simple.player_state.x = 100
        game_simple.player_state.vel_x = 5.0
        game_simple.check_collisions(x_axis=True)
        assert game_simple.player_state.vel_x == 0

    def test_coin_collection(self, game_coin):
        initial_coins = game_coin.game_state.coins_collected
        game_coin.update(MovementDirection.RIGHT)
        game_coin.update(MovementDirection.RIGHT)
        assert game_coin.game_state.coins_collected == initial_coins + 1
        assert game_coin.map_state.map[2][1] == "."

    def test_reaching_end_completes_game(self, game_simple):
        game_simple.player_state.x += 10
        for _ in range(100):
            game_simple.update(MovementDirection.RIGHT)
        assert game_simple.game_state.game_completed is True

    def test_void_tile_triggers_game_over(self, game_void):
        game_void.update(MovementDirection.RIGHT)
        game_void.update(MovementDirection.RIGHT)
        assert game_void.game_state.game_over is True


class TestGameState:

    def test_correct_shape(self, game_simple):
        state = game_simple.get_state(size=2)

        assert len(state) == 6
        assert len(state[0]) == 5

    def test_get_state_values(self, game_simple):
        game_simple.player_state.vel_x = MOVE_SPEED
        game_simple.player_state.vel_y = 3.0
        game_simple.player_state.on_ground = True

        state = game_simple.get_state(size=1)
        metadata = state[-1]

        assert len(metadata) == 4
        assert metadata[3] == 1

    def test_get_state_offset_calculation(self, game_simple):
        game_simple.player_state.x = TILE_SIZE * 2 + TILE_SIZE * 0.3
        state = game_simple.get_state(size=1)
        metadata = state[-1]
        assert metadata[0] == 0

        game_simple.player_state.x = TILE_SIZE * 2 + TILE_SIZE * 0.7
        state = game_simple.get_state(size=1)
        metadata = state[-1]
        assert metadata[0] == 1


class TestStepAndReward:

    def test_step_step(self, game_simple):
        initial_steps = game_simple.game_state.steps
        next_state, reward, done = game_simple.step(2)

        assert game_simple.game_state.steps == initial_steps + 1
        assert isinstance(next_state, list)
        assert isinstance(reward, (int, float))
        assert isinstance(done, bool)

    def test_coin_collection_reward(self, game_coin):
        game_coin.player_state.x = TILE_SIZE * 2
        game_coin.player_state.y = TILE_SIZE * 3
        _, reward, _ = game_coin.step(2)

        if game_coin.game_state.coins_collected > 0:
            assert reward > 0

    def test_game_over_gives_reward(self, game_void):
        for _ in range(10):
            _, reward, done = game_void.step(2)
            if done and game_void.game_state.game_over:
                assert reward == -100
                break

    def test_completion_reward(self, game_simple):
        for _ in range(100):
            _, reward, done = game_simple.step(2)
            if done and game_simple.game_state.game_completed:
                assert reward >= 500
                break

    def test_distance_progress(self, game_simple):
        initial_distance = game_simple.game_state.progress.best_distance
        for _ in range(10):
            game_simple.step(2)
            if game_simple.game_state.progress.best_distance < initial_distance:
                break

    def test_no_progress_penalty(self, game_simple):
        game_simple.game_state.progress.steps_since_progress = 174
        _, reward, done = game_simple.step(0)
        if done:
            assert reward < 0


class TestRestart:

    def test_restart_resets_position(self, game_simple):
        game_simple.player_state.x = TILE_SIZE * 5
        game_simple.player_state.y = TILE_SIZE * 1

        game_simple.restart_game()

        assert game_simple.player_state.x == game_simple.map_state.start_x
        assert game_simple.player_state.y == game_simple.map_state.start_y

    def test_restart_resets_velocities(self, game_simple):
        game_simple.player_state.vel_x = 5.0
        game_simple.player_state.vel_y = 3.0

        game_simple.restart_game()

        assert game_simple.player_state.vel_x == 0.0
        assert game_simple.player_state.vel_y == 0.0

    def test_restart_resets_game_state(self, game_simple):
        game_simple.game_state.game_completed = True
        game_simple.game_state.game_over = True
        game_simple.game_state.steps = 100
        game_simple.game_state.coins_collected = 5

        game_simple.restart_game()

        assert game_simple.game_state.game_completed is False
        assert game_simple.game_state.game_over is False
        assert game_simple.game_state.steps == 0
        assert game_simple.game_state.coins_collected == 0

    def test_restart_reloads_map(self, game_simple):
        game_simple.map_state.map[2][1] = "X"

        game_simple.restart_game()

        assert game_simple.map_state.map[2][1] == "."


class TestEdgeCases:

    def test_player_cannot_move_when_game_completed(self, game_simple):
        game_simple.game_state.game_completed = True
        initial_x = game_simple.player_state.x

        game_simple.update(MovementDirection.RIGHT)

        assert game_simple.player_state.x == initial_x

    def test_player_cannot_move_when_game_over(self, game_simple):
        game_simple.game_state.game_over = True
        initial_x = game_simple.player_state.x

        game_simple.update(MovementDirection.RIGHT)

        assert game_simple.player_state.x == initial_x
