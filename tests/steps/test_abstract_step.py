from hoshizukuri_game.models.activate import TargetActivate, ActivatePlaysetEnd
from hoshizukuri_game.models.game import Game
from hoshizukuri_game.steps.abstract_step import AbstractStep


class TestAbstractStep:
    def test_str(self):
        step = AbstractStep()
        assert str(step) == "0:abstract"

    def test_process(self):
        step = AbstractStep()
        game = Game()
        candidates = step.process(game)
        assert candidates == []

    def test_get_victory(self):
        step = AbstractStep()
        game = Game()
        result = step.get_victory(game)
        assert result == 0

    def test_get_victory_detail(self):
        step = AbstractStep()
        game = Game()
        result = step.get_victory_detail(game)
        assert result == ""

    def test_get_candidates1(self):
        step = AbstractStep()
        game = Game()
        result = step.get_candidates(game)
        assert result == []

    def test_get_candidates2(self):
        step = AbstractStep()
        step.candidates = ["0:actionplay:8"]
        game = Game()
        result = step.get_candidates(game)
        assert result == ["0:actionplay:8#0"]

    def test_can_play_trigger(self):
        game = Game()
        step = AbstractStep()
        target_activate = TargetActivate(ActivatePlaysetEnd(0), 0)
        assert step.can_play_trigger(game, target_activate)
