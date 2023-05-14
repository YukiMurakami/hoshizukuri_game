from hoshizukuri_game.steps.base.daichi_step import (
    DaichiStep, _DaichiTriggerStep
)
from hoshizukuri_game.models.game import Game
from hoshizukuri_game.models.player import Player
from hoshizukuri_game.models.pile import Pile, PileType, PileName
from hoshizukuri_game.models.card import Card
from hoshizukuri_game.steps.common.gain_step import GainStep
from hoshizukuri_game.steps.common.trash_step import TrashStep
from hoshizukuri_game.utils.card_util import get_card_id


class TestDaichiStep():
    def test_str(self):
        step = DaichiStep(0, 0, 0)
        assert str(step) == "0:daichi:0"

    def get_game(self, card_list):
        game = Game()
        game.set_players([Player(0), Player(1)])
        game.players[0].pile[PileName.FIELD] = Pile(
            PileType.LISTLIST, card_list=card_list
        )
        return game

    def test_process_1(self, get_step_classes):
        step = DaichiStep(0, 0, 0)
        game = self.get_game([[
            Card(3, 1), Card(4, 2), Card(7, 3),
            Card(get_card_id("daichi"), 0)
        ]])
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [GainStep]
        next_steps[0].card_ids == [get_card_id("wakusei")]

    def test_process_2(self, get_step_classes):
        step = DaichiStep(0, 0, 0)
        game = self.get_game([[
            Card(3, 1), Card(4, 2), Card(7, 3), Card(7, 4),
            Card(get_card_id("daichi"), 0)
        ]])
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [GainStep]
        next_steps[0].card_ids == [get_card_id("kousei")]


class TestDaichiTriggerStep():
    def test_str(self):
        step = _DaichiTriggerStep(0, 0, 0)
        assert str(step) == "0:daichitrigger:0:%d-0" % get_card_id("daichi")

    def get_game(self, card_list):
        game = Game()
        game.set_players([Player(0), Player(1)])
        game.players[0].pile[PileName.FIELD] = Pile(
            PileType.LISTLIST, card_list=card_list
        )
        return game

    def test_get_trigger_name(self):
        step = _DaichiTriggerStep(0, 0, 0)
        assert step.get_trigger_name() == "daichi:%d-0" % get_card_id("daichi")

    def test_process_1(self, get_step_classes):
        game = self.get_game([[Card(get_card_id("daichi"), 0)]])
        step = _DaichiTriggerStep(0, 0, 0)
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [TrashStep]

    def test_process_2(self, get_step_classes):
        game = self.get_game([[Card(get_card_id("daichi"), 1)]])
        step = _DaichiTriggerStep(0, 0, 0)
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == []
