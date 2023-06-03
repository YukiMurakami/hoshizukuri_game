from hoshizukuri_game.steps.base.kakuyugo_step import (
    KakuyugoStep
)
from hoshizukuri_game.models.game import Game
from hoshizukuri_game.models.player import Player
from hoshizukuri_game.models.pile import Pile, PileType, PileName
from hoshizukuri_game.models.card import Card
from hoshizukuri_game.steps.common.trash_step import TrashStep
from hoshizukuri_game.utils.card_util import get_card_id


class TestKakuyugoStep():
    def test_str(self):
        step = KakuyugoStep(0, 0, 0)
        assert str(step) == "0:kakuyugo:0"

    def get_game(self, card_list, field_list):
        game = Game()
        game.set_players([Player(0), Player(1)])
        game.players[0].pile[PileName.HAND] = Pile(
            PileType.LIST, card_list=card_list
        )
        game.players[0].pile[PileName.FIELD] = Pile(
            PileType.LISTLIST, card_list=field_list
        )
        return game

    def test_process_1(self, get_step_classes, is_equal_candidates):
        step = KakuyugoStep(0, 0, 5)
        game = self.get_game([
            Card(1, 1), Card(2, 2),
            Card(7, 3),
            Card(10, 4)
        ], [[Card(get_card_id("kakuyugo"), 5)]])
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [KakuyugoStep]
        assert is_equal_candidates(
            step.get_candidates(game),
            [
                "0:kakuyugotrash:#0",
                "0:kakuyugotrash:1#0",
                "0:kakuyugotrash:2#0",
                "0:kakuyugotrash:7#0",
                "0:kakuyugotrash:10#0",
                "0:kakuyugotrash:1,7#0",
                "0:kakuyugotrash:2,7#0",
                "0:kakuyugotrash:1,10#0",
                "0:kakuyugotrash:2,10#0",
                "0:kakuyugotrash:7,10#0",
                "0:kakuyugotrash:1,7,10#0",
                "0:kakuyugotrash:2,7,10#0"
            ]
        )

    def test_process_2(self, get_step_classes):
        step = KakuyugoStep(0, 0, 5)
        game = self.get_game([], [[Card(get_card_id("kakuyugo"), 5)]])
        next_steps = step.process(game)
        card = game.players[0].pile[PileName.FIELD].get_card(5)
        assert card.starflake == 1
        assert get_step_classes(next_steps) == []

    def test_process_3(self, get_step_classes):
        step = KakuyugoStep(0, 0, 5)
        game = self.get_game([
            Card(1, 1), Card(2, 2),
            Card(7, 3),
            Card(10, 4)
        ], [[Card(get_card_id("kakuyugo"), 5)]])
        game.choice = "0:kakuyugotrash:1,7,10"
        next_steps = step.process(game)
        card = game.players[0].pile[PileName.FIELD].get_card(5)
        assert card.starflake == 7
        assert get_step_classes(next_steps) == [TrashStep]

    def test_process_4(self, get_step_classes):
        step = KakuyugoStep(0, 0, 5)
        game = self.get_game([
            Card(1, 1), Card(2, 2),
            Card(7, 3),
            Card(10, 4)
        ], [[Card(get_card_id("kakuyugo"), 5)]])
        game.choice = "0:kakuyugotrash:"
        next_steps = step.process(game)
        card = game.players[0].pile[PileName.FIELD].get_card(5)
        assert card.starflake == 1
        assert get_step_classes(next_steps) == []

    def test_process_log_1(self, get_step_classes, make_log_manager):
        step = KakuyugoStep(0, 0, 5)
        game = self.get_game([
            Card(1, 1), Card(2, 2),
            Card(7, 3),
            Card(10, 4)
        ], [[Card(get_card_id("kakuyugo"), 5)]])
        game.log_manager = make_log_manager(
            "A trashes 星屑, 原始星, 森林 from their hand."
        )
        game.choice = "0:kakuyugotrash:1,7,10"
        next_steps = step.process(game)
        card = game.players[0].pile[PileName.FIELD].get_card(5)
        assert card.starflake == 7
        assert get_step_classes(next_steps) == [TrashStep]

    def test_process_log_2(
            self, get_step_classes, make_log_manager, is_equal_candidates):
        step = KakuyugoStep(0, 0, 5)
        game = self.get_game([
            Card(1, 1), Card(2, 2),
            Card(7, 3),
            Card(10, 4)
        ], [[Card(get_card_id("kakuyugo"), 5)]])
        game.log_manager = make_log_manager(
            ""
        )
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [KakuyugoStep]
        assert is_equal_candidates(
            step.get_candidates(game),
            [
                "0:kakuyugotrash:#0",
                "0:kakuyugotrash:1#0",
                "0:kakuyugotrash:2#0",
                "0:kakuyugotrash:7#0",
                "0:kakuyugotrash:10#0",
                "0:kakuyugotrash:1,7#0",
                "0:kakuyugotrash:2,7#0",
                "0:kakuyugotrash:1,10#0",
                "0:kakuyugotrash:2,10#0",
                "0:kakuyugotrash:7,10#0",
                "0:kakuyugotrash:1,7,10#0",
                "0:kakuyugotrash:2,7,10#0"
            ]
        )

    def test_process_log_3(self, get_step_classes, make_log_manager):
        step = KakuyugoStep(0, 0, 5)
        game = self.get_game([
            Card(1, 1), Card(2, 2),
            Card(7, 3),
            Card(10, 4)
        ], [[Card(get_card_id("kakuyugo"), 5)]])
        game.log_manager = make_log_manager(
            "A draws 星屑."
        )
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == []
