from hoshizukuri_game.steps.base.ikaduchi_step import (
    IkaduchiStep,
    _IkaduchiGainStep
)
from hoshizukuri_game.models.game import Game
from hoshizukuri_game.models.player import Player
from hoshizukuri_game.models.pile import Pile, PileType, PileName
from hoshizukuri_game.models.card import Card
from hoshizukuri_game.steps.common.trash_step import TrashStep
from hoshizukuri_game.steps.common.gain_step import GainStep


class TestIkaduchiStep():
    def test_str(self):
        step = IkaduchiStep(0, 0, 0)
        assert str(step) == "0:ikaduchi:0"

    def get_game(self, card_list):
        game = Game()
        game.set_players([Player(0), Player(1)])
        game.players[0].pile[PileName.HAND] = Pile(
            PileType.LIST, card_list=card_list
        )
        return game

    def test_process(self, get_step_classes):
        step = IkaduchiStep(0, 0, 0)
        game = self.get_game([Card(1, 1), Card(4, 2)])
        game.choice = "0:ikaduchitrash:4"
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [_IkaduchiGainStep, TrashStep]
        assert next_steps[0].trash_id == 4

    def test_process_no_hand(self, get_step_classes):
        step = IkaduchiStep(0, 0, 0)
        game = self.get_game([])
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == []

    def test_process_no_trash(self, get_step_classes):
        step = IkaduchiStep(0, 0, 0)
        game = self.get_game([Card(1, 1), Card(4, 2)])
        game.choice = "0:ikaduchitrash:0"
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == []


class TestIkaduchiGainStep():
    def test_str(self):
        step = _IkaduchiGainStep(0, 0, 2)
        game = Game()
        step.process(game)
        assert str(step) == "0:ikaduchigain:0:4"

    def test_process(self):
        step = _IkaduchiGainStep(0, 0, 3)
        game = Game()
        game.choice = "0:ikaduchigain:3"
        game.set_players([Player(0)])
        game.set_supply([])
        next_steps = step.process(game)
        assert len(next_steps) == 1
        assert isinstance(next_steps[0], GainStep)
        assert next_steps[0].card_ids == [3]
