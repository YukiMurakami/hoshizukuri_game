from hoshizukuri_game.models.game import Game
from hoshizukuri_game.models.player import Player
from hoshizukuri_game.models.pile import Pile, PileType, PileName
from hoshizukuri_game.models.log import InvalidLogException
from hoshizukuri_game.models.card import Card
from hoshizukuri_game.steps.abstract_step import AbstractStep
from hoshizukuri_game.steps.common.play_step import (
    PlayStep, PlayEndStep, play_add_select_process,
    _ProcessResolveLogStep
)
from hoshizukuri_game.steps.common_card_steps import (
    EiseiStep, HoshikuzuStep
)
import pytest


class TestPlayStep:
    def test_str(self):
        game = Game()
        game.set_players([Player(0)])
        game.players[0].pile[PileName.HAND] = Pile(
            PileType.LIST, card_list=[Card(1, 1)]
        )
        step = PlayStep(
            0, 0, [1], [1], from_pilename=PileName.HAND)
        step.process(game)
        assert str(step) == "0:play:hand:0:1-1:0"

    def test_process_1(self, get_step_classes):
        step = PlayStep(
            0, 0, [1], [1], from_pilename=PileName.HAND)
        game = Game()
        game.set_players([Player(0)])
        game.players[0].pile[PileName.HAND] = Pile(
            PileType.LIST, card_list=[Card(1, 1)]
        )
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [
            PlayEndStep, HoshikuzuStep, _ProcessResolveLogStep]

    def test_process_2(self, get_step_classes):
        step = PlayStep(
            0, 0, [], [], from_pilename=PileName.HAND)
        game = Game()
        game.created = False
        game.set_players([Player(0)])
        game.players[0].pile[PileName.HAND] = Pile(
            PileType.LIST, card_list=[Card(1, 1)]
        )
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == []

    def test_process_3(self, get_step_classes):
        step = PlayStep(
            0, 0, [], [], from_pilename=PileName.HAND)
        game = Game()
        game.created = False
        game.set_players([Player(0)])
        game.players[0].pile[PileName.HAND] = Pile(
            PileType.LIST, card_list=[Card(1, 1)]
        )
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == []

    def test_process_4(self, get_step_classes):
        step = PlayStep(
            0, 0, [3], [1], from_pilename=PileName.HAND, process_effect=False)
        game = Game()
        game.set_players([Player(0)])
        game.players[0].pile[PileName.HAND] = Pile(
            PileType.LIST, card_list=[Card(3, 1)]
        )
        next_steps = step.process(game)
        assert str(game.players[0].pile[PileName.HAND]) == "[]"
        assert str(game.players[0].pile[PileName.FIELD]) == "[[3-1]]"
        assert get_step_classes(next_steps) == []

    def test_process_5(self, get_step_classes):
        step = PlayStep(
            0, 0, [3], [1], from_pilename=PileName.FIELD)
        game = Game()
        game.created = False
        game.set_players([Player(0)])
        game.players[0].pile[PileName.FIELD] = Pile(
            PileType.LISTLIST, card_list=[[Card(3, 1)]]
        )
        next_steps = step.process(game)
        assert str(game.players[0].pile[PileName.FIELD]) == "[[3-1]]"
        assert get_step_classes(next_steps) == [
            PlayEndStep, EiseiStep, _ProcessResolveLogStep]

    def test_process_log_1(self, get_step_classes, make_log_manager):
        step = PlayStep(
            0, 0, [1], [1], from_pilename=PileName.HAND)
        game = Game()
        game.log_manager = make_log_manager(
            "A plays 星屑."
        )
        game.set_players([Player(0)])
        game.players[0].pile[PileName.HAND] = Pile(
            PileType.LIST, card_list=[Card(1, 1)]
        )
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [
            PlayEndStep, HoshikuzuStep, _ProcessResolveLogStep]

    def test_process_log_2(self, get_step_classes, make_log_manager):
        step = PlayStep(
            0, 0, [1], [1], from_pilename=PileName.HAND,
            process_effect=False, add=True)
        game = Game()
        game.log_manager = make_log_manager(
            "A adds 星屑 to the play from their hand."
        )
        game.set_players([Player(0)])
        game.players[0].pile[PileName.HAND] = Pile(
            PileType.LIST, card_list=[Card(1, 1)]
        )
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == []

    def test_process_log_3(self, get_step_classes, make_log_manager):
        step = PlayStep(
            0, 0, [1], [1], from_pilename=PileName.REVEAL,
            process_effect=False, add=True)
        game = Game()
        game.log_manager = make_log_manager(
            "A adds 星屑 to the play from their reveal."
        )
        game.set_players([Player(0)])
        game.players[0].pile[PileName.REVEAL] = Pile(
            PileType.LIST, card_list=[Card(1, 1)]
        )
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == []


class TestProcessResolveLogStep:
    def test_str(self):
        step = _ProcessResolveLogStep(0, 0, 1)
        assert str(step) == "0:processresolvelog:0:1"

    def test_process_log_1(self, get_step_classes, make_log_manager):
        step = _ProcessResolveLogStep(0, 0, 1)
        game = Game()
        game.log_manager = make_log_manager(
            "A resolves the effects of 星屑."
        )
        game.set_players([Player(0)])
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == []

    def test_process_log_2(self, get_step_classes, make_log_manager):
        step = _ProcessResolveLogStep(0, 0, 1)
        game = Game()
        game.log_manager = make_log_manager(
            "A draws 星屑."
        )
        game.set_players([Player(0)])
        with pytest.raises(InvalidLogException):
            step.process(game)


class TestPlayEndStep:
    def test_str(self):
        step = PlayEndStep(0, 0, 1, 1)
        assert str(step) == "0:playend:0:1-1"

    def test_process_1(self, get_step_classes):
        step = PlayEndStep(0, 0, 1, 1)
        game = Game()
        game.set_players([Player(0)])
        game.players[0].pile[PileName.FIELD] = Pile(
            PileType.LISTLIST, card_list=[[Card(1, 1)]]
        )
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == []


class TestPlayAddSelectProcess():
    def game_and_step(self, card_list):
        game = Game()
        game.set_players([Player(0), Player(1)])
        game.players[0].pile[PileName.HAND] = Pile(
            PileType.LIST, card_list=card_list
        )
        step = AbstractStep()
        step.player_id = 0
        return game, step

    def test_playadd_select_process_1(self):
        game, step = self.game_and_step(
            [Card(1, 1), Card(4, 2)])
        next_steps = play_add_select_process(
            game, step, "playadd", 2, can_less=True,
            next_step_callback=None
        )
        assert isinstance(next_steps[-1], AbstractStep)
        assert next_steps[-1].get_candidates(game) == [
            "0:playadd:1#0",
            "0:playadd:4#0",
            "0:playadd:1,4#0",
            "0:playadd:#0"
        ]

    def test_playadd_select_process_2(self):
        game, step = self.game_and_step(
            [Card(1, 1), Card(4, 2)])
        game.choice = "0:playadd:1"
        next_steps = play_add_select_process(
            game, step, "playadd", 2, can_less=True,
            next_step_callback=None
        )
        assert isinstance(next_steps[-1], PlayStep)
        assert next_steps[-1].card_ids == [1]

    def test_playadd_select_process_log_1(self, make_log_manager):
        game, step = self.game_and_step(
            [Card(1, 1), Card(4, 2)])
        game.log_manager = make_log_manager(
            "A adds 星屑 to the play from their hand."
        )
        next_steps = play_add_select_process(
            game, step, "playadd", 2, can_less=True,
            next_step_callback=None
        )
        assert isinstance(next_steps[-1], PlayStep)
        assert next_steps[-1].card_ids == [1]
