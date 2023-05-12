from hoshizukuri_game.steps.base.sougen_step import (
    SougenStep
)
from hoshizukuri_game.models.game import Game
from hoshizukuri_game.models.player import Player
from hoshizukuri_game.models.pile import Pile, PileType, PileName
from hoshizukuri_game.models.card import Card
from hoshizukuri_game.steps.common.gain_step import GainStep
from hoshizukuri_game.utils.card_util import get_card_id


class TestSougenStep():
    def test_str(self):
        step = SougenStep(0, 0, 0)
        assert str(step) == "0:sougen:0"

    def get_game(self, card_list):
        game = Game()
        game.set_players([Player(0), Player(1)])
        game.set_supply([get_card_id("sougen"), get_card_id("izumi")])
        game.players[0].pile[PileName.FIELD] = Pile(
            PileType.LISTLIST, card_list=card_list
        )
        return game

    def test_process_1(self, get_step_classes, is_equal_candidates):
        step = SougenStep(0, 0, 0)
        game = self.get_game([[Card(1, 1), Card(2, 2), Card(7, 3)]])
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [SougenStep]
        assert is_equal_candidates(
            step.get_candidates(game),
            [
                "0:sougengain:0#0",
                "0:sougengain:3#0",
                "0:sougengain:%d#0" % get_card_id("izumi")
            ]
        )

    def test_process_2(self, get_step_classes):
        step = SougenStep(0, 0, 0)
        game = self.get_game([[Card(1, 1), Card(2, 2), Card(7, 3)]])
        game.choice = "0:sougengain:3"
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [GainStep]
