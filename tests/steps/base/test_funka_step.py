from hoshizukuri_game.steps.base.funka_step import (
    FunkaStep
)
from hoshizukuri_game.models.game import Game
from hoshizukuri_game.models.player import Player
from hoshizukuri_game.models.pile import Pile, PileType, PileName
from hoshizukuri_game.models.card import Card
from hoshizukuri_game.steps.common.discard_step import DiscardStep


class TestFunkaStep():
    def test_str(self):
        step = FunkaStep(0, 0, 0)
        assert str(step) == "0:funka:0"

    def get_game(self, card_list):
        game = Game()
        game.set_players([Player(0), Player(1)])
        game.players[0].pile[PileName.HAND] = Pile(
            PileType.LIST, card_list=card_list
        )
        return game

    def test_process_1(self, get_step_classes):
        step = FunkaStep(0, 0, 0)
        game = self.get_game([Card(1, 1), Card(2, 2), Card(7, 3)])
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [DiscardStep]

    def test_process_2(self, get_step_classes):
        step = FunkaStep(0, 0, 0)
        game = self.get_game([])
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == []
