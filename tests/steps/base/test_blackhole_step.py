from hoshizukuri_game.steps.base.blackhole_step import (
    BlackholeStep
)
from hoshizukuri_game.models.game import Game
from hoshizukuri_game.models.player import Player
from hoshizukuri_game.models.pile import Pile, PileType, PileName
from hoshizukuri_game.models.card import Card
from hoshizukuri_game.steps.common.play_step import PlayStep


class TestBlackholeStep():
    def test_str(self):
        step = BlackholeStep(0, 0, 0)
        assert str(step) == "0:blackhole:0"

    def get_game(self, card_list):
        game = Game()
        game.set_players([Player(0), Player(1)])
        game.players[0].pile[PileName.HAND] = Pile(
            PileType.LIST, card_list=card_list
        )
        return game

    def test_process_1(self, get_step_classes, is_equal_candidates):
        step = BlackholeStep(0, 0, 0)
        game = self.get_game([Card(3, 1), Card(4, 2), Card(7, 3)])
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [BlackholeStep]
        assert is_equal_candidates(
            step.get_candidates(game),
            [
                "0:blackholeaddplay:#0",
                "0:blackholeaddplay:3#0",
                "0:blackholeaddplay:4#0",
                "0:blackholeaddplay:3,4#0",
            ]
        )

    def test_process_2(self, get_step_classes):
        step = BlackholeStep(0, 0, 0)
        game = self.get_game([Card(3, 1), Card(4, 2), Card(7, 3)])
        game.choice = "0:blackholeaddplay:4"
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [PlayStep]

    def test_process_3(self, get_step_classes):
        step = BlackholeStep(0, 0, 0)
        game = self.get_game([Card(7, 3)])
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == []
