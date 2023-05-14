from hoshizukuri_game.steps.base.kori_step import (
    KoriStep
)
from hoshizukuri_game.models.game import Game
from hoshizukuri_game.models.player import Player
from hoshizukuri_game.models.pile import Pile, PileType, PileName
from hoshizukuri_game.models.card import Card
from hoshizukuri_game.utils.card_util import get_card_id


class TestKoriStep():
    def test_str(self):
        step = KoriStep(0, 0, 0)
        assert str(step) == "0:kori:0"

    def test_process_1(self, get_step_classes, is_equal_candidates):
        game = Game()
        game.set_players([Player(0), Player(1)])
        game.set_supply([])
        card = Card(get_card_id("kori"), 5)
        game.players[0].pile[PileName.FIELD] = Pile(
            PileType.LISTLIST, card_list=[
                [Card(1, 1), card]
            ]
        )
        step = KoriStep(0, 0, 5)
        assert not card.stop_orbit
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == []
        assert card.stop_orbit
