from hoshizukuri_game.steps.common_card_steps import (
    HoshikuzuStep,
    GansekiStep,
    EiseiStep,
    WakuseiStep,
    KouseiStep
)
from hoshizukuri_game.models.game import Game
from hoshizukuri_game.models.player import Player
from hoshizukuri_game.steps.common.starflake_step import (
    AddStarflakeStep
)


class TestHoshikuzuStep():
    def test_str(self):
        step = HoshikuzuStep(0, 1, 0)
        assert str(step) == "1:hoshikuzu:0"

    def test_process(self):
        step = HoshikuzuStep(0, 1, 0)
        game = Game()
        game.set_players([Player(0)])
        next_steps = step.process(game)
        assert len(next_steps) == 1
        assert isinstance(next_steps[0], AddStarflakeStep)
        assert next_steps[0].add_starflake == 1


class TestGansekiStep():
    def test_str(self):
        step = GansekiStep(0, 1, 0)
        assert str(step) == "1:ganseki:0"

    def test_process(self):
        step = GansekiStep(0, 1, 0)
        game = Game()
        game.set_players([Player(0)])
        next_steps = step.process(game)
        assert len(next_steps) == 1
        assert isinstance(next_steps[0], AddStarflakeStep)
        assert next_steps[0].add_starflake == 2


class TestEiseiStep():
    def test_str(self):
        step = EiseiStep(0, 1, 0)
        assert str(step) == "1:eisei:0"

    def test_process(self):
        step = EiseiStep(0, 1, 0)
        game = Game()
        game.set_players([Player(0)])
        next_steps = step.process(game)
        assert len(next_steps) == 1
        assert isinstance(next_steps[0], AddStarflakeStep)
        assert next_steps[0].add_starflake == 1
        assert step.get_victory(game) == 1


class TestWakuseiStep():
    def test_str(self):
        step = WakuseiStep(0, 1, 0)
        assert str(step) == "1:wakusei:0"

    def test_process(self):
        step = WakuseiStep(0, 1, 0)
        game = Game()
        game.set_players([Player(0)])
        next_steps = step.process(game)
        assert len(next_steps) == 1
        assert isinstance(next_steps[0], AddStarflakeStep)
        assert next_steps[0].add_starflake == 1
        assert step.get_victory(game) == 4


class TestKouseiStep():
    def test_str(self):
        step = KouseiStep(0, 1, 0)
        assert str(step) == "1:star:0"

    def test_process(self):
        step = KouseiStep(0, 1, 0)
        game = Game()
        game.set_players([Player(0)])
        next_steps = step.process(game)
        assert len(next_steps) == 1
        assert isinstance(next_steps[0], AddStarflakeStep)
        assert next_steps[0].add_starflake == 1
        assert step.get_victory(game) == 8
