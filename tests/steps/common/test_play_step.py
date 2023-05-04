from hoshizukuri_game.models.game import Game
from hoshizukuri_game.models.player import Player
from hoshizukuri_game.models.pile import Pile, PileType, PileName
from hoshizukuri_game.models.card import Card
from hoshizukuri_game.steps.common.play_step import (
    PlayStep
)
from hoshizukuri_game.steps.common_card_steps import (
    SatelliteStep, StardustStep
)


class TestPlayStep:
    def test_str(self):
        step = PlayStep(
            0, 0, [1], [1], from_pilename=PileName.HAND)
        assert str(step) == "0:play:hand:0:1-1"

    def test_process_1(self, get_step_classes):
        step = PlayStep(
            0, 0, [1], [1], from_pilename=PileName.HAND)
        game = Game()
        game.set_players([Player(0)])
        game.players[0].pile[PileName.HAND] = Pile(
            PileType.LIST, card_list=[Card(1, 1)]
        )
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [StardustStep]

    def test_process_2(self, get_step_classes):
        step = PlayStep(
            0, 0, [], [], from_pilename=PileName.HAND, create=True)
        game = Game()
        game.created = False
        game.set_players([Player(0)])
        game.players[0].pile[PileName.HAND] = Pile(
            PileType.LIST, card_list=[Card(1, 1)]
        )
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == []
        assert game.created is True

    def test_process_3(self, get_step_classes):
        step = PlayStep(
            0, 0, [], [], from_pilename=PileName.HAND, create=False)
        game = Game()
        game.created = False
        game.set_players([Player(0)])
        game.players[0].pile[PileName.HAND] = Pile(
            PileType.LIST, card_list=[Card(1, 1)]
        )
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == []
        assert game.created is False

    def test_process_4(self, get_step_classes):
        step = PlayStep(
            0, 0, [3], [1], from_pilename=PileName.HAND)
        game = Game()
        game.created = False
        game.set_players([Player(0)])
        game.players[0].pile[PileName.HAND] = Pile(
            PileType.LIST, card_list=[Card(3, 1)]
        )
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [SatelliteStep]
        assert game.created is True
