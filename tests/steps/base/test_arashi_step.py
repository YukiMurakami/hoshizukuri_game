from hoshizukuri_game.steps.base.arashi_step import (
    ArashiStep
)
from hoshizukuri_game.models.game import Game
from hoshizukuri_game.models.player import Player
from hoshizukuri_game.models.pile import Pile, PileType, PileName
from hoshizukuri_game.models.card import Card
from hoshizukuri_game.steps.common.discard_step import DiscardStep


class TestArashiStep():
    def test_str(self):
        step = ArashiStep(0, 0, 0)
        assert str(step) == "0:arashi:0"

    def get_game(self, card_list):
        game = Game()
        game.set_players([Player(0), Player(1)])
        game.players[0].pile[PileName.FIELD] = Pile(
            PileType.LISTLIST, card_list=card_list
        )
        return game

    def test_process_1(self, get_step_classes, is_equal_candidates):
        step = ArashiStep(0, 0, 0)
        game = self.get_game(
            [
                [Card(1, 1), Card(2, 2), Card(3, 3)],
                [Card(1, 4)],
                [Card(2, 5)],
                [Card(1, 6), Card(2, 7)],
                [Card(9, 10)]
            ]
        )
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [ArashiStep]
        assert is_equal_candidates(
            step.get_candidates(game),
            [
                "0:arashiindex:#0",
                "0:arashiindex:1#0",
                "0:arashiindex:2#0"
            ]
        )

    def test_process_2(self, get_step_classes):
        step = ArashiStep(0, 0, 0)
        game = self.get_game(
            [
                [Card(1, 1), Card(2, 2), Card(3, 3)],
                [Card(1, 4)],
                [Card(2, 5)],
                [Card(1, 6), Card(2, 7)],
                [Card(9, 10)]
            ]
        )
        game.choice = "0:arashiindex:1"
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [DiscardStep]
        assert next_steps[0].orbit_index == 1

    def test_process_3(self, get_step_classes):
        step = ArashiStep(0, 0, 0)
        game = self.get_game(
            [
                [Card(1, 1), Card(2, 2), Card(3, 3)],
                [Card(1, 4)],
                [Card(2, 5)],
                [Card(1, 6), Card(2, 7)],
                [Card(9, 10)]
            ]
        )
        game.choice = "0:arashiindex:"
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == []

    def test_process_4(self, get_step_classes):
        step = ArashiStep(0, 0, 0)
        game = self.get_game(
            [
                [Card(9, 10)]
            ]
        )
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == []

    def test_process_log_1(self, get_step_classes, make_log_manager):
        step = ArashiStep(0, 0, 0)
        game = self.get_game(
            [
                [Card(1, 1), Card(2, 2), Card(3, 3)],
                [Card(1, 4)],
                [Card(2, 5)],
                [Card(1, 6), Card(2, 7)],
                [Card(9, 10)]
            ]
        )
        game.log_manager = make_log_manager(
            "A discards 星屑 from their playarea."
        )
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [DiscardStep]
        assert next_steps[0].orbit_index == 1

    def test_process_log_2(
            self, get_step_classes, is_equal_candidates, make_log_manager):
        step = ArashiStep(0, 0, 0)
        game = self.get_game(
            [
                [Card(1, 1), Card(2, 2), Card(3, 3)],
                [Card(1, 4)],
                [Card(2, 5)],
                [Card(1, 6), Card(2, 7)],
                [Card(9, 10)]
            ]
        )
        game.log_manager = make_log_manager("")
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [ArashiStep]
        assert is_equal_candidates(
            step.get_candidates(game),
            [
                "0:arashiindex:#0",
                "0:arashiindex:1#0",
                "0:arashiindex:2#0"
            ]
        )

    def test_process_log_3(self, get_step_classes, make_log_manager):
        step = ArashiStep(0, 0, 0)
        game = self.get_game(
            [
                [Card(1, 1), Card(2, 2), Card(3, 3)],
                [Card(1, 4)],
                [Card(2, 5)],
                [Card(1, 6), Card(2, 7)],
                [Card(9, 10)]
            ]
        )
        game.log_manager = make_log_manager(
            "A draws 星屑."
        )
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == []
