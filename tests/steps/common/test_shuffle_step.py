import random
from hoshizukuri_game.models.card import Card
from hoshizukuri_game.models.pile import Pile, PileName, PileType
from hoshizukuri_game.models.player import Player
from hoshizukuri_game.steps.common.shuffle_step import (
    ReshuffleStep,
)
from hoshizukuri_game.models.game import Game


class TestReshuffleStep():
    def test_str1(self):
        step = ReshuffleStep(0, 1)
        assert str(step) == "1:reshuffle:0:"

    def test_process_1(self):
        random.seed(0)
        step = ReshuffleStep(0, 0)
        game = Game()
        game.set_players([Player(0)])
        game.players[0].pile[PileName.DISCARD] = Pile(
            PileType.LIST, card_list=[
                Card(1, 1), Card(1, 2), Card(4, 3)
            ]
        )
        step.process(game)
        assert game.players[0].pile[PileName.DECK].count == 3
        assert game.players[0].pile[PileName.DISCARD].count == 0
        assert str(game.players[0].pile[PileName.DECK].card_list[0]) == "1-1"
        assert str(game.players[0].pile[PileName.DECK].card_list[1]) == "4-3"
        assert str(game.players[0].pile[PileName.DECK].card_list[2]) == "1-2"

    def test_process_2(self):
        random.seed(0)
        step = ReshuffleStep(0, 0)
        game = Game()
        game.set_players([Player(0)])
        game.players[0].pile[PileName.DISCARD] = Pile(
            PileType.LIST, card_list=[]
        )
        step.process(game)
        assert str(step) == "0:reshuffle:0:"
        assert game.players[0].pile[PileName.DECK].count == 0
        assert game.players[0].pile[PileName.DISCARD].count == 0
