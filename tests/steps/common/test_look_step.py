from hoshizukuri_game.models.card import Card
from hoshizukuri_game.models.pile import Pile, PileName, PileType
from hoshizukuri_game.models.player import Player
from hoshizukuri_game.models.game import Game
from hoshizukuri_game.steps.common.look_step import (
    LookStep
)


class TestLookStep():
    def test_str1(self):
        game = Game()
        game.set_players([Player(0)])
        game.players[0].pile[PileName.HAND] = Pile(
            PileType.LIST, card_list=[
                Card(1, 1), Card(1, 2), Card(1, 3), Card(4, 4)
            ]
        )
        step = LookStep(0, 0, [1, 1], from_pilename=PileName.HAND)
        step.process(game)
        assert str(step) == "0:look:hand:0:1-1,1-2"

    def test_str2(self):
        game = Game()
        game.set_players([Player(0)])
        game.players[0].pile[PileName.DECK] = Pile(
            PileType.LIST, card_list=[
                Card(1, 1), Card(1, 2), Card(1, 3), Card(4, 4)
            ]
        )
        step = LookStep(0, 0, count=2, from_pilename=PileName.DECK)
        next_steps = step.process(game)
        assert str(step) == "0:pre-lookfromdeck:0:2"
        next_steps[0].process(game)
        assert str(next_steps[0]) == "0:lookfromdeck:0:1-1,1-2"

    def test_process_1(self):
        game = Game()
        game.set_players([Player(0)])
        game.players[0].pile[PileName.DECK] = Pile(
            PileType.LIST, card_list=[
                Card(1, 1), Card(1, 2), Card(1, 3), Card(4, 4)
            ]
        )
        deck = game.players[0].pile[PileName.DECK]
        look = game.players[0].pile[PileName.LOOK]
        step = LookStep(0, 0, count=2, from_pilename=PileName.DECK)
        next_steps = step.process(game)
        next_steps = next_steps[0].process(game)
        assert str(deck) == "[1-3,4-4]"
        assert str(look) == "[1-1,1-2]"
