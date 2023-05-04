import random
from hoshizukuri_game.models.card import Card
from hoshizukuri_game.models.pile import Pile, PileName, PileType
from hoshizukuri_game.models.player import Player
from hoshizukuri_game.steps.common.draw_step import (
    DrawStep,
    _ActualDrawStep
)
from hoshizukuri_game.steps.common.shuffle_step import ReshuffleStep
from hoshizukuri_game.models.game import Game


class TestDrawStep():
    def test_str(self):
        step = DrawStep(0, 0, 2)
        assert str(step) == "0:pre-draw:0:2"

    def test_process1(self):
        step = DrawStep(0, 0, 2)
        game = Game()
        game.set_players([Player(0)])
        game.players[0].pile[PileName.DECK] = Pile(
            PileType.LIST, card_list=[Card(1, 1), Card(1, 2), Card(4, 3)]
        )
        next_steps = step.process(game)
        assert len(next_steps) == 1
        assert isinstance(next_steps[0], _ActualDrawStep)
        assert next_steps[0].player_id == 0
        assert next_steps[0].count == 2

    def test_process2(self):
        random.seed(0)
        step = DrawStep(0, 0, 2)
        game = Game()
        game.set_players([Player(0)])
        game.players[0].pile[PileName.DISCARD] = Pile(
            PileType.LIST, card_list=[Card(1, 1), Card(1, 2), Card(4, 3)]
        )
        next_steps = step.process(game)
        assert len(next_steps) == 2
        assert isinstance(next_steps[1], ReshuffleStep)
        assert next_steps[1].player_id == 0
        assert isinstance(next_steps[0], _ActualDrawStep)
        assert next_steps[0].count == 2

    def test_process3(self):
        random.seed(0)
        step = DrawStep(0, 0, 5)
        game = Game()
        game.set_players([Player(0)])
        next_steps = step.process(game)
        assert len(next_steps) == 0


class TestActualDrawStep():
    def test_str(self):
        step = _ActualDrawStep(0, 1, 2)
        game = Game()
        game.set_players([Player(0)])
        game.players[0].pile[PileName.DECK] = Pile(
            PileType.LIST, card_list=[
                Card(1, 1), Card(1, 2), Card(4, 3)
            ]
        )
        step.process(game)
        assert str(step) == "1:draw:0:1-1,1-2"

    def test_process(self):
        step = _ActualDrawStep(0, 0, 2)
        game = Game()
        game.set_players([Player(0)])
        game.players[0].pile[PileName.DECK] = Pile(
            PileType.LIST, card_list=[
                Card(1, 1), Card(1, 2), Card(4, 3)
            ]
        )
        deck = game.players[0].pile[PileName.DECK]
        hand = game.players[0].pile[PileName.HAND]
        next_steps = step.process(game)
        assert deck.count == 1
        assert hand.count == 2
        assert deck.card_list[0].uniq_id == 3
        assert hand.card_list[1].uniq_id == 2
        assert next_steps == []
