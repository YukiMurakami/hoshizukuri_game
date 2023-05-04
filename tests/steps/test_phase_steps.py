from hoshizukuri_game.models.card import Card
from hoshizukuri_game.models.pile import Pile, PileName, PileType
from hoshizukuri_game.steps.common.draw_step import DrawStep
from hoshizukuri_game.steps.common.play_step import PlayStep
from hoshizukuri_game.steps.phase_steps import (
    PlayContinueStep,
    TurnStartStep,
    PrepareFirstDeckStep,
    PlaySelectStep,
)
from hoshizukuri_game.models.turn import Turn, TurnType
from hoshizukuri_game.models.game import Game
from hoshizukuri_game.models.player import Player
from hoshizukuri_game.utils.card_util import get_card_id


class TestTurnStartStep:
    def test_str(self):
        step = TurnStartStep(0, Turn(0, 0, 0, TurnType.NORMAL))
        assert str(step) == "0:turnstart:0:0:normal:0"

    def test_process(self, get_step_classes):
        step = TurnStartStep(0, Turn(1, 0, 0, TurnType.NORMAL))
        game = Game()
        game.set_players([Player(0), Player(1)])
        game.set_supply([])
        game.turn = Turn(0, -1, 1, TurnType.NORMAL)
        next_steps = step.process(game)
        assert game.turn.turn == 1
        assert game.turn.player_id == 0
        assert game.turn.turn_type == TurnType.NORMAL
        assert get_step_classes(next_steps) == [PlaySelectStep]


class TestPrepareFirstDeckStep:
    def test_str(self):
        step = PrepareFirstDeckStep(0)
        assert str(step) == "0:preparefirstdeck:0"

    def get_base_game(self):
        game = Game()
        game.set_players([Player(0)])
        game.set_supply([n for n in range(6, 14)])
        game.turn = Turn(1, 0, 0, TurnType.NORMAL)
        return game

    def test_process(self):
        step = PrepareFirstDeckStep(0)
        game = self.get_base_game()
        step.process(game)
        assert game.players[0].pile[PileName.DISCARD].count == 7


class TestPlaySelectStep:
    def test_str(self):
        step = PlaySelectStep(0)
        assert str(step) == "0:playselect:0"

    def get_game(self, hand_list):
        game = Game()
        game.set_players([Player(0), Player(1)])
        game.set_supply([n for n in range(8, 17)])
        game.turn = Turn(1, 0, 0, TurnType.NORMAL)
        game.players[0].pile[PileName.HAND] = Pile(
            PileType.LIST, card_list=hand_list)
        return game

    def test_process_normal(self, get_step_classes, is_equal_candidates):
        step = PlaySelectStep(0)
        game = self.get_game([
            Card(get_card_id("flame"), 0),
            Card(get_card_id("eruption"), 1),
            Card(get_card_id("stardust"), 2),
        ])
        game.choice = ""
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [
            PlaySelectStep
        ]
        assert is_equal_candidates(
            step.get_candidates(game),
            [
                "0:play:1#0",
                "0:play:9#0",
                "0:play:10#0",
                "0:play:9,10#0",
                "0:play:10,9#0",
            ]
        )

    def test_process_3_colors(self, get_step_classes, is_equal_candidates):
        step = PlaySelectStep(0)
        game = self.get_game([
            Card(get_card_id("flame"), 0),
            Card(get_card_id("eruption"), 1),
            Card(get_card_id("forest"), 2),
            Card(get_card_id("ice"), 3),
        ])
        game.choice = ""
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [
            PlaySelectStep
        ]
        assert is_equal_candidates(
            step.get_candidates(game),
            [
                "0:play:9#0",
                "0:play:10#0",
                "0:play:11#0",
                "0:play:16#0",
                "0:play:9,10#0",
                "0:play:10,9#0",
                "0:play:9,11,16#0",
                "0:play:9,16,11#0",
                "0:play:11,9,16#0",
                "0:play:11,16,9#0",
                "0:play:16,9,11#0",
                "0:play:16,11,9#0",
                "0:play:10,11,16#0",
                "0:play:10,16,11#0",
                "0:play:11,10,16#0",
                "0:play:11,16,10#0",
                "0:play:16,10,11#0",
                "0:play:16,11,10#0",
            ]
        )

    def test_process_play(self, get_step_classes):
        step = PlaySelectStep(0)
        game = self.get_game([
            Card(get_card_id("flame"), 0),
            Card(get_card_id("eruption"), 1),
            Card(get_card_id("stardust"), 2),
        ])
        game.choice = "0:play:9"
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [
            PlayContinueStep,
            PlayStep
        ]

    def test_process_no_hand(self, get_step_classes):
        step = PlaySelectStep(0)
        game = self.get_game([])
        game.choice = ""
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == []

    def test_process_over_orbit(self, get_step_classes):
        step = PlaySelectStep(0)
        game = self.get_game([
            Card(get_card_id("flame"), 0),
            Card(get_card_id("eruption"), 1),
            Card(get_card_id("stardust"), 2),
        ])
        game.players[0].orbit = 35
        game.choice = "0:play:9"
        game.players[0].tmp_orbit = 35
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == []

    def test_process_created(self, get_step_classes):
        step = PlaySelectStep(0)
        game = self.get_game([
            Card(get_card_id("flame"), 0),
            Card(get_card_id("eruption"), 1),
            Card(get_card_id("stardust"), 2),
        ])
        game.created = True
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == []


class TestPlayContinueStep:
    def test_str(self):
        step = PlayContinueStep(0)
        assert str(step) == "0:playcontinue:0"

    def test_process_1(self, get_step_classes):
        step = PlayContinueStep(0)
        game = Game()
        game.set_players([Player(0)])
        game.set_supply([])
        game.players[0].pile[PileName.HAND] = Pile(
            PileType.LIST, card_list=[
                Card(1, 1), Card(1, 2)
            ]
        )
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [
            PlaySelectStep, DrawStep
        ]
        assert next_steps[1].count == 2

    def test_process_2(self, get_step_classes):
        step = PlayContinueStep(0)
        game = Game()
        game.set_players([Player(0)])
        game.set_supply([])
        game.players[0].pile[PileName.HAND] = Pile(
            PileType.LIST, card_list=[
                Card(1, 1), Card(1, 2), Card(1, 3), Card(2, 4)
            ]
        )
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [
            PlaySelectStep
        ]
