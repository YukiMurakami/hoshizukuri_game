from hoshizukuri_game.steps.base.kudamononoki_step import (
    KudamononokiStep
)
from hoshizukuri_game.models.game import Game
from hoshizukuri_game.models.player import Player


class TestKudamononokiStep():
    def test_str(self):
        step = KudamononokiStep(0, 0, 0)
        assert str(step) == "0:kudamononoki:0"

    def test_process(self):
        step = KudamononokiStep(0, 1, 0)
        game = Game()
        game.set_players([Player(0)])
        next_steps = step.process(game)
        assert len(next_steps) == 0
        assert step.get_victory(game) == 3
