from hoshizukuri_game.steps.base.suisho_step import (
    SuishoStep
)
from hoshizukuri_game.models.game import Game
from hoshizukuri_game.models.player import Player
from hoshizukuri_game.models.pile import Pile, PileType, PileName
from hoshizukuri_game.models.card import Card
from hoshizukuri_game.steps.common.play_step import PlayStep
from hoshizukuri_game.steps.common.reveal_step import RevealStep


class TestSuishoStep():
    def test_str(self):
        step = SuishoStep(0, 0, 0)
        assert str(step) == "0:suisho:0"

    def get_game(self, card_list):
        game = Game()
        game.set_players([Player(0), Player(1)])
        game.players[0].pile[PileName.DECK] = Pile(
            PileType.LIST, card_list=card_list
        )
        return game

    def test_process_1(self, get_step_classes):
        step = SuishoStep(0, 0, 0)
        game = self.get_game([Card(1, 1), Card(4, 2)])
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [RevealStep]
        next_steps = next_steps[0].process(game)
        next_steps = next_steps[0].process(game)
        assert get_step_classes(next_steps) == [PlayStep]

    def test_process_2(self, get_step_classes):
        step = SuishoStep(0, 0, 0)
        game = self.get_game([])
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [RevealStep]
        next_steps = next_steps[0].process(game)
        assert get_step_classes(next_steps) == []
