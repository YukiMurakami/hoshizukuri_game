from hoshizukuri_game.models.pile import Pile, PileName, PileType
from hoshizukuri_game.models.player import Player
from hoshizukuri_game.models.game import Game
from hoshizukuri_game.models.card import Card
from hoshizukuri_game.steps.common.gain_step import (
    GainStep,
    gain_select_process,
)
from hoshizukuri_game.models.card_condition import CardCondition
from hoshizukuri_game.steps.abstract_step import AbstractStep
from hoshizukuri_game.models.cost import Cost
from hoshizukuri_game.utils.card_util import CardType


class TestGainStep():
    def test_str_1(self):
        step = GainStep(0, 1, 2)
        assert str(step) == "1:gain:supply:0:2:discard"

    def test_str_2(self):
        step = GainStep(0, 1, 2, uniq_id=10, from_pilename=PileName.TRASH)
        assert str(step) == "1:gain:trash:0:2-10:discard"

    def get_game(self):
        game = Game()
        game.set_players([Player(0), Player(1)])
        game.set_supply([])
        return game

    def test_process_gain(self, get_step_classes):
        game = self.get_game()
        step = GainStep(0, 0, 3)
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == []
        assert game.supply[3].count == 11
        assert str(game.players[0].pile[PileName.DISCARD]) == "[3-1]"

    def test_process_gain_nocard(self, get_step_classes):
        game = self.get_game()
        step = GainStep(0, 0, 10)
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == []
        assert str(game.players[0].pile[PileName.DISCARD]) == "[]"

    def test_process_gain_trash(self, get_step_classes):
        game = self.get_game()
        game.trash = Pile(
            PileType.LIST, card_list=[Card(5, 2)]
        )
        step = GainStep(0, 0, 5, from_pilename=PileName.TRASH)
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == []
        assert str(game.trash) == "[]"
        assert str(game.players[0].pile[PileName.DISCARD]) == "[5-2]"


class TestGainSelectProcess():
    def get_game(self):
        game = Game()
        game.set_players([Player(0)])
        game.set_supply([])
        return game

    def test_gain_select_process_1(self, get_step_classes):
        game = self.get_game()
        step = AbstractStep()
        step.player_id = 0
        game.choice = "0:gain:3"
        next_steps = gain_select_process(
            game, step, "gain", None,
            can_pass=False
        )
        assert get_step_classes(next_steps) == [GainStep]
        assert game.choice == ""

    def test_gain_select_process_2(self, get_step_classes):
        game = self.get_game()
        game.trash = Pile(
            PileType.LIST, card_list=[Card(9, 10), Card(10, 11)]
        )
        step = AbstractStep()
        step.player_id = 0
        game.choice = "0:gain:9"
        steps = gain_select_process(
            game, step, "gain",
            CardCondition(type=CardType.CELESTIAL),
            can_pass=False, from_pilename=PileName.TRASH
        )
        assert get_step_classes(steps) == [GainStep]
        assert game.choice == ""

    def test_gain_select_process_no_choice(self):
        game = self.get_game()
        step = AbstractStep()
        step.player_id = 0
        game.choice = ""
        steps = gain_select_process(
            game, step, "gain",
            None,
            can_pass=False
        )
        assert len(steps) == 1
        assert steps[0] is step
        assert game.choice == ""

    def test_gain_select_process_no_candidates(self):
        game = self.get_game()
        step = AbstractStep()
        step.player_id = 0
        game.choice = "0:gain:1"
        steps = gain_select_process(
            game, step, "gain",
            CardCondition(le_cost=Cost(0), type=CardType.STAR),
            can_pass=False
        )
        assert len(steps) == 0
        assert game.choice == "0:gain:1"

    def test_gain_select_process_can_pass(self, is_equal_candidates):
        game = self.get_game()
        step = AbstractStep()
        step.player_id = 0
        steps = gain_select_process(
            game, step, "gain",
            None,
            can_pass=True
        )
        assert len(steps) == 1
        assert steps[0] is step
        assert is_equal_candidates(
            steps[0].get_candidates(game),
            [
                "0:gain:3#0",
                "0:gain:4#0",
                "0:gain:5#0",
                "0:gain:0#0",
            ]
        )
