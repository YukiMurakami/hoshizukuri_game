from hoshizukuri_game.steps.common_card_steps import (
    StardustStep,
    RockStep,
    SatelliteStep,
    PlanetStep,
    StarStep
)
from hoshizukuri_game.models.game import Game
from hoshizukuri_game.models.player import Player
from hoshizukuri_game.steps.common.starflake_step import (
    AddStarflakeStep
)


class TestStardustStep():
    def test_str(self):
        step = StardustStep(0, 1, 0)
        assert str(step) == "1:stardust:0"

    def test_process(self):
        step = StardustStep(0, 1, 0)
        game = Game()
        game.set_players([Player(0)])
        next_steps = step.process(game)
        assert len(next_steps) == 1
        assert isinstance(next_steps[0], AddStarflakeStep)
        assert next_steps[0].add_starflake == 1


class TestRockStep():
    def test_str(self):
        step = RockStep(0, 1, 0)
        assert str(step) == "1:rock:0"

    def test_process(self):
        step = RockStep(0, 1, 0)
        game = Game()
        game.set_players([Player(0)])
        next_steps = step.process(game)
        assert len(next_steps) == 1
        assert isinstance(next_steps[0], AddStarflakeStep)
        assert next_steps[0].add_starflake == 2


class TestSatelliteStep():
    def test_str(self):
        step = SatelliteStep(0, 1, 0)
        assert str(step) == "1:satellite:0"

    def test_process(self):
        step = SatelliteStep(0, 1, 0)
        game = Game()
        game.set_players([Player(0)])
        next_steps = step.process(game)
        assert len(next_steps) == 1
        assert isinstance(next_steps[0], AddStarflakeStep)
        assert next_steps[0].add_starflake == 1
        assert step.get_victory(game) == 1


class TestPlanetStep():
    def test_str(self):
        step = PlanetStep(0, 1, 0)
        assert str(step) == "1:planet:0"

    def test_process(self):
        step = PlanetStep(0, 1, 0)
        game = Game()
        game.set_players([Player(0)])
        next_steps = step.process(game)
        assert len(next_steps) == 1
        assert isinstance(next_steps[0], AddStarflakeStep)
        assert next_steps[0].add_starflake == 1
        assert step.get_victory(game) == 4


class TestStarStep():
    def test_str(self):
        step = StarStep(0, 1, 0)
        assert str(step) == "1:star:0"

    def test_process(self):
        step = StarStep(0, 1, 0)
        game = Game()
        game.set_players([Player(0)])
        next_steps = step.process(game)
        assert len(next_steps) == 1
        assert isinstance(next_steps[0], AddStarflakeStep)
        assert next_steps[0].add_starflake == 1
        assert step.get_victory(game) == 8
