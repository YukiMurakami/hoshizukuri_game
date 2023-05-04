from hoshizukuri_game.models.pile import PileName
from hoshizukuri_game.steps.phase_steps import (
    TurnStartStep,
    PrepareFirstDeckStep
)
from hoshizukuri_game.models.turn import Turn, TurnType
from hoshizukuri_game.models.game import Game
from hoshizukuri_game.models.player import Player


class TestTurnStartStep:
    def test_str(self):
        step = TurnStartStep(0, Turn(0, 0, 0, TurnType.NORMAL))
        assert str(step) == "0:turnstart:0:0:normal:0"

    def test_process(self, get_step_classes):
        step = TurnStartStep(0, Turn(1, 0, 0, TurnType.NORMAL))
        game = Game()
        game.set_players([Player(0), Player(1)])
        game.set_supply([])
        game.turn = Turn(0, -1, 1, TurnType.NORMAL)
        next_steps = step.process(game)
        assert game.turn.turn == 1
        assert game.turn.player_id == 0
        assert game.turn.turn_type == TurnType.NORMAL
        assert get_step_classes(next_steps) == []


class TestPrepareFirstDeckStep:
    def test_str(self):
        step = PrepareFirstDeckStep(0)
        assert str(step) == "0:preparefirstdeck:0"

    def get_base_game(self):
        game = Game()
        game.set_players([Player(0)])
        game.set_supply([n for n in range(6, 14)])
        game.turn = Turn(1, 0, 0, TurnType.NORMAL)
        return game

    def test_process(self):
        step = PrepareFirstDeckStep(0)
        game = self.get_base_game()
        step.process(game)
        assert game.players[0].pile[PileName.DISCARD].count == 7
