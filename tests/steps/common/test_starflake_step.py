from hoshizukuri_game.models.player import Player
from hoshizukuri_game.steps.common.starflake_step import (
    AddStarflakeStep
)
from hoshizukuri_game.models.game import Game


class TestAddStarflakeStep():
    def test_str(self):
        step = AddStarflakeStep(0, 0, 2)
        assert str(step) == "0:addstarflake:0:2"

    def test_process1(self):
        step = AddStarflakeStep(0, 0, 2)
        game = Game()
        game.set_players([Player(0), Player(1)])
        game.turn.player_id = 0
        game.starflake = 1
        next_steps = step.process(game)
        assert len(next_steps) == 0
        assert game.starflake == 3

    def test_process2(self):
        step = AddStarflakeStep(0, 0, 2)
        game = Game()
        game.set_players([Player(0), Player(1)])
        game.turn.player_id = 1
        game.starflake = 1
        next_steps = step.process(game)
        assert len(next_steps) == 0
        assert game.starflake == 1
