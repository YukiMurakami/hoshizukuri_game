from hoshizukuri_game.models.card import Card
from hoshizukuri_game.models.pile import Pile, PileName, PileType
from hoshizukuri_game.steps.common.draw_step import DrawStep
from hoshizukuri_game.models.player import Player
from hoshizukuri_game.models.game import Game
from hoshizukuri_game.steps.abstract_step import AbstractStep
from hoshizukuri_game.steps.common.trash_step import (
    trash_select_process,
    TrashStep
)
import pytest


class TestTrashStep():
    def test_str1(self):
        game = Game()
        game.set_players([Player(0)])
        game.players[0].pile[PileName.HAND] = Pile(
            PileType.LIST, card_list=[
                Card(1, 1), Card(1, 2), Card(1, 3), Card(4, 4)
            ]
        )
        step = TrashStep(0, 0, [1, 1], from_pilename=PileName.HAND)
        step.process(game)
        assert str(step) == "0:trash:hand:0:1-1,1-2"

    def test_str2(self):
        game = Game()
        game.set_players([Player(0)])
        game.players[0].pile[PileName.FIELD] = Pile(
            PileType.LISTLIST, card_list=[
                [Card(1, 1), Card(1, 2), Card(1, 3), Card(4, 4)],
                [Card(5, 1)]
            ]
        )
        step = TrashStep(0, 0, [1, 1], [1, 2], from_pilename=PileName.FIELD)
        step.process(game)
        assert str(step) == "0:trash:field:0:1-1,1-2"

    def test_str3(self):
        game = Game()
        game.set_players([Player(0)])
        game.players[0].pile[PileName.DECK] = Pile(
            PileType.LIST, card_list=[
                Card(1, 1), Card(1, 2), Card(1, 3), Card(4, 4)
            ]
        )
        step = TrashStep(0, 0, count=2, from_pilename=PileName.DECK)
        next_steps = step.process(game)
        assert str(step) == "0:pre-trashfromdeck:0:2"
        next_steps[0].process(game)
        assert str(next_steps[0]) == "0:trashfromdeck:0:1-1,1-2"

    def get_hand4_game(self):
        game = Game()
        game.set_players([Player(0), Player(1)])
        game.set_supply([])
        game.players[0].pile[PileName.HAND] = Pile(
            PileType.LIST, card_list=[
                Card(1, 1), Card(1, 2), Card(4, 3), Card(4, 4)
            ]
        )
        return game

    def test_process1(self):
        game = self.get_hand4_game()
        hand = game.players[0].pile[PileName.HAND]
        trash = game.trash
        step = TrashStep(0, 0, [1, 1])
        step.process(game)
        assert hand.count == 2
        assert hand.card_list[0].uniq_id == 3
        assert hand.card_list[1].uniq_id == 4
        assert trash.count == 2
        assert trash.card_list[0].uniq_id == 1
        assert trash.card_list[1].uniq_id == 2


class TestTrashSelectProcess():
    def game_and_step(self, card_list, from_pilename):
        game = Game()
        game.set_players([Player(0), Player(1)])
        game.set_supply([8, 9, 10])
        game.players[0].pile[from_pilename] = Pile(
            PileType.LIST, card_list=card_list
        )
        step = AbstractStep()
        step.player_id = 0
        return game, step

    def callback(self, card_ids, uniq_ids, game):
        return [DrawStep(0, 0, len(card_ids))]

    def test_trash_select_process_1(self):
        game, step = self.game_and_step(
            [Card(1, 1), Card(4, 2)], PileName.HAND)
        next_steps = trash_select_process(
            game, step, "trash", 2, can_less=True,
            next_step_callback=None
        )
        assert isinstance(next_steps[-1], AbstractStep)
        assert next_steps[-1].get_candidates(game) == [
            "0:trash:1#0",
            "0:trash:4#0",
            "0:trash:1,4#0",
            "0:trash:#0"
        ]

    def test_trash_select_process_2(self):
        game, step = self.game_and_step(
            [Card(1, 1), Card(4, 2)], PileName.HAND)
        game.choice = "0:trash:1,4"
        next_steps = trash_select_process(
            game, step, "trash", 2, can_less=True,
            next_step_callback=None
        )
        assert isinstance(next_steps[-1], TrashStep)

    def test_trash_select_process_error(self, get_step_classes):
        game, step = self.game_and_step(
            [Card(1, 1), Card(4, 2)], PileName.REVEAL)
        with pytest.raises(Exception):
            trash_select_process(
                game, step, "lurkertrash", 2, from_pilename=PileName.SUPPLY
            )
