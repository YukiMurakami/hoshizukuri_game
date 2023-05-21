from hoshizukuri_game.models.card import Card
from hoshizukuri_game.models.pile import Pile, PileName, PileType
from hoshizukuri_game.models.player import Player
from hoshizukuri_game.models.game import Game
from hoshizukuri_game.steps.common.putin_step import (
    PutinHandStep
)


class TestPutinHandStep():
    def test_str1(self):
        game = Game()
        game.set_players([Player(0)])
        game.players[0].pile[PileName.REVEAL] = Pile(
            PileType.LIST, card_list=[
                Card(1, 1), Card(1, 2), Card(1, 3), Card(4, 4)
            ]
        )
        step = PutinHandStep(0, 0, [1, 1], from_pilename=PileName.REVEAL)
        step.process(game)
        assert str(step) == "0:putinhand:reveal:0:1-1,1-2"

    def get_game(self):
        game = Game()
        game.set_players([Player(0), Player(1)])
        game.set_supply([])
        game.players[0].pile[PileName.REVEAL] = Pile(
            PileType.LIST, card_list=[
                Card(1, 1), Card(1, 2), Card(4, 3), Card(4, 4)
            ]
        )
        return game

    def test_process1(self):
        game = self.get_game()
        reveal = game.players[0].pile[PileName.REVEAL]
        hand = game.players[0].pile[PileName.HAND]
        step = PutinHandStep(0, 0, [1, 1], from_pilename=PileName.REVEAL)
        step.process(game)
        assert hand.count == 2
        assert hand.card_list[0].uniq_id == 1
        assert hand.card_list[1].uniq_id == 2
        assert reveal.count == 2
        assert reveal.card_list[0].uniq_id == 3
        assert reveal.card_list[1].uniq_id == 4
