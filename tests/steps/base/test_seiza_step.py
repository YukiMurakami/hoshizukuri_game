from hoshizukuri_game.steps.base.seiza_step import (
    SeizaStep
)
from hoshizukuri_game.models.game import Game
from hoshizukuri_game.models.player import Player
from hoshizukuri_game.models.pile import Pile, PileType, PileName
from hoshizukuri_game.models.card import Card
from hoshizukuri_game.utils.card_util import get_card_id


class TestSeizaStep():
    def test_str(self):
        step = SeizaStep(0, 0, 0)
        assert str(step) == "0:seiza:0"

    def get_game(self, card_list):
        game = Game()
        game.set_players([Player(0), Player(1)])
        game.players[0].pile[PileName.HAND] = Pile(
            PileType.LIST, card_list=card_list
        )
        return game

    def test_process_1(self, get_step_classes):
        step = SeizaStep(0, 0, 0)
        game = self.get_game([Card(1, 1), Card(2, 2), Card(7, 3)])
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == []

    def test_get_victory(self):
        step = SeizaStep(0, 0, 0)
        game = self.get_game([
            Card(1, 1), Card(2, 2),
            Card(get_card_id("honow"), 3),
            Card(get_card_id("arashi"), 4),
            Card(get_card_id("shinrin"), 5),
            Card(get_card_id("kori"), 6),
            Card(get_card_id("sougen"), 7),
            Card(get_card_id("honow"), 8),
            Card(get_card_id("honow"), 9)
        ])
        assert step.get_victory(game) == 6

    def test_get_victory_defatil(self):
        step = SeizaStep(0, 0, 0)
        game = self.get_game([
            Card(1, 1), Card(2, 2),
            Card(get_card_id("honow"), 3),
            Card(get_card_id("arashi"), 4),
            Card(get_card_id("shinrin"), 5),
            Card(get_card_id("kori"), 6),
            Card(get_card_id("sougen"), 7),
            Card(get_card_id("honow"), 8),
            Card(get_card_id("honow"), 9)
        ])
        assert step.get_victory_detail(game) == (
            "19:Seiza: 3 red, 2 green, 2 blue"
        )
