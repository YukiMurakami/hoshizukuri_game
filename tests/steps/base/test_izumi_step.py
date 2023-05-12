from hoshizukuri_game.steps.base.izumi_step import (
    IzumiStep,
    _IzumiSelectStep,
)
from hoshizukuri_game.models.game import Game
from hoshizukuri_game.models.player import Player
from hoshizukuri_game.models.pile import Pile, PileType, PileName
from hoshizukuri_game.models.card import Card
from hoshizukuri_game.steps.common.discard_step import DiscardStep
from hoshizukuri_game.steps.common.look_step import LookStep
from hoshizukuri_game.steps.common.putin_step import PutinHandStep


class TestIzumiStep():
    def test_str(self):
        step = IzumiStep(0, 0, 0)
        assert str(step) == "0:izumi:0"

    def get_game(self, card_list):
        game = Game()
        game.set_players([Player(0), Player(1)])
        game.players[0].pile[PileName.DECK] = Pile(
            PileType.LIST, card_list=card_list
        )
        return game

    def test_process_1(self, get_step_classes, is_equal_candidates):
        step = IzumiStep(0, 0, 0)
        game = self.get_game([Card(1, 1), Card(4, 2)])
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [LookStep]
        next_steps = next_steps[0].process(game)
        next_steps = next_steps[0].process(game)
        assert get_step_classes(next_steps) == [_IzumiSelectStep]

    def test_process_2(self, get_step_classes, is_equal_candidates):
        step = IzumiStep(0, 0, 0)
        game = self.get_game([])
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [LookStep]
        next_steps = next_steps[0].process(game)
        assert get_step_classes(next_steps) == []


class TestIzumiSelectStep():
    def test_str(self):
        step = _IzumiSelectStep(0, 0, 0)
        assert str(step) == "0:izumiselect:0"

    def get_game(self, card_list):
        game = Game()
        game.set_players([Player(0), Player(1)])
        game.players[0].pile[PileName.LOOK] = Pile(
            PileType.LIST, card_list=card_list
        )
        return game

    def test_process_1(self, get_step_classes, is_equal_candidates):
        step = _IzumiSelectStep(0, 0, 0)
        game = self.get_game([Card(1, 1)])
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [_IzumiSelectStep]
        assert is_equal_candidates(
            next_steps[0].get_candidates(game),
            [
                "0:izumi:hand#0",
                "0:izumi:discard#0"
            ]
        )

    def test_process_2(self, get_step_classes):
        step = _IzumiSelectStep(0, 0, 0)
        game = self.get_game([Card(1, 1)])
        game.choice = "0:izumi:hand"
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [PutinHandStep]

    def test_process_3(self, get_step_classes):
        step = _IzumiSelectStep(0, 0, 0)
        game = self.get_game([Card(1, 1)])
        game.choice = "0:izumi:discard"
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [DiscardStep]
