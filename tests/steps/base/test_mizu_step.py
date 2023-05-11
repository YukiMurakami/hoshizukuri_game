from hoshizukuri_game.steps.base.mizu_step import (
    MizuStep
)
from hoshizukuri_game.models.game import Game
from hoshizukuri_game.models.player import Player
from hoshizukuri_game.models.pile import Pile, PileType, PileName
from hoshizukuri_game.models.card import Card
from hoshizukuri_game.steps.common.discard_step import DiscardStep


class TestMizuStep():
    def test_str(self):
        step = MizuStep(0, 0, 0)
        assert str(step) == "0:mizu:0"

    def get_game(self, card_list):
        game = Game()
        game.set_players([Player(0), Player(1)])
        game.players[0].pile[PileName.HAND] = Pile(
            PileType.LIST, card_list=card_list
        )
        return game

    def test_process_1(self, get_step_classes, is_equal_candidates):
        step = MizuStep(0, 0, 0)
        game = self.get_game([Card(1, 1), Card(2, 2), Card(7, 3)])
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [MizuStep]
        assert is_equal_candidates(
            step.get_candidates(game),
            [
                "0:mizudiscard:0#0",
                "0:mizudiscard:1#0",
                "0:mizudiscard:2#0",
                "0:mizudiscard:7#0"
            ]
        )

    def test_process_2(self, get_step_classes):
        step = MizuStep(0, 0, 0)
        game = self.get_game([Card(1, 1), Card(2, 2), Card(7, 3)])
        game.choice = "0:mizudiscard:1"
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [DiscardStep]
