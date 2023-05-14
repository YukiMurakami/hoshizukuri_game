from hoshizukuri_game.steps.base.inseki_step import (
    InsekiStep,
    _InsekiAttackStep
)
from hoshizukuri_game.models.game import Game
from hoshizukuri_game.models.player import Player
from hoshizukuri_game.models.pile import Pile, PileType, PileName
from hoshizukuri_game.models.card import Card
from hoshizukuri_game.steps.common.discard_step import DiscardStep
from hoshizukuri_game.steps.common.draw_step import DrawStep
from hoshizukuri_game.steps.common.reveal_step import RevealAllHandStep
from hoshizukuri_game.utils.card_util import get_card_id


class TestInsekiStep():
    def test_str(self):
        step = InsekiStep(0, 0, 0)
        assert str(step) == "0:inseki:0"

    def get_game(self, card_list):
        game = Game()
        game.set_players([Player(0), Player(1), Player(2)])
        game.players[0].pile[PileName.HAND] = Pile(
            PileType.LIST, card_list=card_list
        )
        return game

    def test_process_1(self, get_step_classes):
        step = InsekiStep(0, 0, 0)
        game = self.get_game([Card(1, 1), Card(4, 2)])
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [
            _InsekiAttackStep, _InsekiAttackStep]
        assert next_steps[0].player_id == 2
        assert next_steps[1].player_id == 1


class TestInsekiAttackStep():
    def test_str(self):
        step = _InsekiAttackStep(0, 0, 2, 0)
        assert str(step) == "0:insekiattack:0"

    def get_game(self, card_list, attacker_list):
        game = Game()
        game.set_players([Player(0), Player(1), Player(2)])
        game.players[0].pile[PileName.HAND] = Pile(
            PileType.LIST, card_list=card_list
        )
        game.players[2].pile[PileName.FIELD] = Pile(
            PileType.LISTLIST, card_list=[attacker_list]
        )
        return game

    def test_process_1(self, get_step_classes, is_equal_candidates):
        step = _InsekiAttackStep(0, 0, 2, 0)
        game = self.get_game(
            [
                Card(get_card_id("honow"), 1),
                Card(get_card_id("mizu"), 2),
                Card(get_card_id("shinrin"), 3)
            ],
            [
                Card(get_card_id("kori"), 4),
                Card(get_card_id("ikaduchi"), 5),
                Card(get_card_id("inseki"), 0)
            ]
        )
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [_InsekiAttackStep]
        assert is_equal_candidates(
            next_steps[0].get_candidates(game),
            [
                "0:insekidiscard:%d#0" % get_card_id("mizu"),
                "0:insekidiscard:%d#0" % get_card_id("honow")
            ]
        )

    def test_process_2(self, get_step_classes):
        step = _InsekiAttackStep(0, 0, 2, 0)
        game = self.get_game(
            [
                Card(get_card_id("honow"), 1),
                Card(get_card_id("mizu"), 2),
                Card(get_card_id("shinrin"), 3)
            ],
            [
                Card(get_card_id("inseki"), 0)
            ]
        )
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == []

    def test_process_3(self, get_step_classes):
        step = _InsekiAttackStep(0, 0, 2, 0)
        game = self.get_game(
            [
                Card(get_card_id("honow"), 1),
                Card(get_card_id("mizu"), 2),
                Card(get_card_id("shinrin"), 3)
            ],
            [
                Card(get_card_id("kori"), 4),
                Card(get_card_id("ikaduchi"), 5),
                Card(get_card_id("inseki"), 0)
            ]
        )
        game.choice = "0:insekidiscard:%d" % get_card_id("mizu")
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [DrawStep, DiscardStep]

    def test_process_4(self, get_step_classes, is_equal_candidates):
        step = _InsekiAttackStep(0, 0, 2, 0)
        game = self.get_game(
            [
                Card(get_card_id("hoshikuzu"), 1),
                Card(get_card_id("hoshikuzu"), 2),
                Card(get_card_id("shinrin"), 3)
            ],
            [
                Card(get_card_id("kori"), 4),
                Card(get_card_id("ikaduchi"), 5),
                Card(get_card_id("inseki"), 0)
            ]
        )
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [RevealAllHandStep]

    def test_process_5(self, get_step_classes, is_equal_candidates):
        step = _InsekiAttackStep(0, 0, 2, 0)
        game = self.get_game(
            [
            ],
            [
                Card(get_card_id("kori"), 4),
                Card(get_card_id("ikaduchi"), 5),
                Card(get_card_id("inseki"), 0)
            ]
        )
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == []
