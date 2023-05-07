from typing import List
from hoshizukuri_game.models.card import Card
from hoshizukuri_game.utils.card_util import CardType
from hoshizukuri_game.models.card_condition import CardCondition
from hoshizukuri_game.steps.common.play_step import PlayStep
from hoshizukuri_game.models.player import Player
from hoshizukuri_game.models.game import Game
from hoshizukuri_game.models.pile import Pile, PileType, PileName
from hoshizukuri_game.steps.abstract_step import AbstractStep
from hoshizukuri_game.steps.common.card_move_step import (
    CardMoveStep,
    _ActualCardMoveFromDeckStep,
    select_process,
    get_pile
)
from hoshizukuri_game.steps.common.shuffle_step import ReshuffleStep
import pytest


def get_game(deck_list, discard_list, hand_list, field_list):
    game = Game()
    game.set_players([Player(0)])
    game.set_supply([])
    game.players[0].pile[PileName.DECK] = Pile(
        PileType.LIST, card_list=deck_list
    )
    game.players[0].pile[PileName.DISCARD] = Pile(
        PileType.LIST, card_list=discard_list
    )
    game.players[0].pile[PileName.HAND] = Pile(
        PileType.LIST, card_list=hand_list
    )
    game.players[0].pile[PileName.FIELD] = Pile(
        PileType.LISTLIST, card_list=field_list
    )
    return game


class TestGetPile:
    def test_get_pile_1(self):
        game = Game()
        game.set_players([Player(0)])
        game.set_supply([])
        pile = get_pile(PileName.SUPPLY, game, 0)
        assert pile is game.supply

    def test_get_pile_2(self):
        game = Game()
        game.set_players([Player(0)])
        game.set_supply([])
        pile = get_pile(PileName.TRASH, game, 0)
        assert pile is game.trash

    def test_get_pile_3(self):
        game = Game()
        game.set_players([Player(0)])
        game.set_supply([])
        pile = get_pile(PileName.HAND, game, 0)
        assert pile is game.players[0].pile[PileName.HAND]


class TestCardMoveStep:
    def callback(self, card_ids, uniq_ids, game):
        step = AbstractStep()
        return [step]

    def test_constractor_1(self):
        with pytest.raises(Exception):
            CardMoveStep(
                player_id=0, depth=0,
                from_pilename=PileName.HAND,
                to_pilename=PileName.HAND
            )

    def test_constractor_2(self):
        with pytest.raises(Exception):
            CardMoveStep(
                player_id=0, depth=0,
                from_pilename=PileName.HAND,
                to_pilename=PileName.DISCARD,
                count=2
            )

    def test_constractor_3(self):
        with pytest.raises(Exception):
            CardMoveStep(
                player_id=0, depth=0,
                from_pilename=PileName.DECK,
                to_pilename=PileName.DISCARD,
                card_ids=[1, 2, 3]
            )

    def test_constractor_4(self):
        with pytest.raises(Exception):
            CardMoveStep(
                player_id=0, depth=0,
                from_pilename=PileName.HAND,
                to_pilename=PileName.DISCARD,
                next_step_callback=self.callback
            )

    def test_constractor_5(self):
        with pytest.raises(Exception):
            CardMoveStep(
                player_id=0, depth=0, card_ids=[1, 2],
                from_pilename=PileName.HAND,
                to_pilename=PileName.DISCARD,
                next_step_callback=self.callback
            )

    def test_str(self):
        step = CardMoveStep(
            player_id=0, depth=0,
            from_pilename=PileName.HAND,
            to_pilename=PileName.DISCARD,
            card_ids=[1, 1, 4],
            uniq_ids=[1, 2, 3]
        )
        assert str(step) == "card_move_step"

    def test_process_1(self, get_step_classes):
        # pile to pile
        game = get_game(
            [], [], [Card(1, 1), Card(1, 2), Card(4, 3), Card(4, 4)], []
        )
        step = CardMoveStep(
            player_id=0, depth=0,
            from_pilename=PileName.HAND,
            to_pilename=PileName.DISCARD,
            card_ids=[1, 1, 4]
        )
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == []
        assert str(game.players[0].pile[PileName.DISCARD]) == "[1-1,1-2,4-3]"
        assert str(game.players[0].pile[PileName.HAND]) == "[4-4]"

    def test_process_2(self, get_step_classes):
        # deck to reveal
        game = get_game(
            [Card(1, 1), Card(1, 2), Card(4, 3), Card(4, 4)], [], [], [])
        step = CardMoveStep(
            player_id=0, depth=0,
            from_pilename=PileName.DECK,
            to_pilename=PileName.REVEAL,
            count=2
        )
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [_ActualCardMoveFromDeckStep]
        assert next_steps[0].count == 2
        assert str(next_steps[0]) == "from_deck_step"
        next_steps = next_steps[0].process(game)
        assert get_step_classes(next_steps) == []

    def test_process_3(self, get_step_classes):
        # deck to reveal
        game = get_game(
            [Card(1, 1), Card(1, 2), Card(4, 3)], [Card(4, 4)], [], [])
        step = CardMoveStep(
            player_id=0, depth=0,
            from_pilename=PileName.DECK,
            to_pilename=PileName.REVEAL,
            count=10
        )
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [
            _ActualCardMoveFromDeckStep, ReshuffleStep]
        assert next_steps[0].count == 4

    def test_process_4(self, get_step_classes):
        # deck to reveal
        game = get_game(
            [], [], [], [])
        step = CardMoveStep(
            player_id=0, depth=0,
            from_pilename=PileName.DECK,
            to_pilename=PileName.REVEAL,
            count=10
        )
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == []

    def test_process_5(self, get_step_classes):
        # hand to field
        game = get_game(
            [], [], [Card(1, 1), Card(2, 2), Card(4, 3)], [])
        step = CardMoveStep(
            player_id=0, depth=0,
            from_pilename=PileName.HAND,
            to_pilename=PileName.FIELD,
            card_ids=[1, 2]
        )
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == []
        assert str(game.players[0].pile[PileName.HAND]) == "[4-3]"
        assert str(game.players[0].pile[PileName.FIELD]) == "[[1-1,2-2]]"

    def test_process_6(self, get_step_classes):
        # supply to hand
        game = get_game(
            [], [], [], [])
        step = CardMoveStep(
            player_id=0, depth=0,
            from_pilename=PileName.SUPPLY,
            to_pilename=PileName.HAND,
            card_ids=[3]
        )
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == []
        assert str(game.players[0].pile[PileName.HAND]) == "[3-1]"
        assert game.supply[3].count == 11

    def test_process_7(self, get_step_classes):
        # empty supply to hand
        game = get_game(
            [], [], [], [])
        game.supply[3] = Pile(
            PileType.NUMBER, card_id_and_count=[3, 0]
        )
        step = CardMoveStep(
            player_id=0, depth=0,
            from_pilename=PileName.SUPPLY,
            to_pilename=PileName.HAND,
            card_ids=[3]
        )
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == []
        assert str(game.players[0].pile[PileName.HAND]) == "[]"
        assert game.supply[3].count == 0


class TestActualCardMoveFromDeckStep:
    def get_from_deck_step_string(self, step):
        return ""

    def after_process_callback(self, card_ids, uniq_ids, game):
        pass

    def callback(self, card_ids, uniq_ids, game):
        step = AbstractStep()
        return [step]

    def test_process_1(self, get_step_classes):
        step = _ActualCardMoveFromDeckStep(
            player_id=0, depth=0, count=2,
            to_pilename=PileName.REVEAL,
            next_step_callback=self.callback,
            get_from_deck_step_string=self.get_from_deck_step_string,
            after_process_callback=self.after_process_callback
        )
        game = get_game(
            [Card(1, 1), Card(1, 2), Card(4, 3)], [Card(4, 4)],
            [], []
        )
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [AbstractStep]
        assert str(game.players[0].pile[PileName.DECK]) == "[4-3]"
        assert str(game.players[0].pile[PileName.REVEAL]) == "[1-1,1-2]"


class TestSelectProcess():
    def create_step(
            self, player_id: int, depth: int,
            from_pilename: PileName, to_pilename: PileName,
            card_ids: List[int], uniq_ids: List[int]):
        return PlayStep(
            player_id, depth, card_ids, uniq_ids,
            from_pilename
        )

    def check(
            self, get_step_classes,
            player_id, card_list, choice="", log="", can_less=False,
            condition=None, count=1,
            next_step_callback=None, previous_step_callback=None,
            expected_next_steps=None, expected_candidates=None,
            expected_card_ids=None, can_pass=None,
            from_pilename=PileName.HAND, to_pilename=PileName.DISCARD):
        game = Game()
        game.set_players([Player(0), Player(1)])
        game.set_supply([])
        game.players[player_id].pile[from_pilename] = Pile(
            PileType.LIST, card_list=card_list
        )
        if can_pass is None:
            can_pass = can_less
        game.choice = choice
        source_step = AbstractStep()
        source_step.player_id = player_id
        next_steps = select_process(
            self.create_step, game, source_step,
            "play", count, from_pilename=from_pilename,
            to_pilename=to_pilename,
            can_less=can_less, can_pass=can_pass, card_condition=condition,
            next_step_callback=next_step_callback,
            previous_step_callback=previous_step_callback
        )
        if expected_next_steps is not None:
            assert get_step_classes(next_steps) == expected_next_steps
        if expected_candidates is not None:
            assert expected_candidates == next_steps[0].get_candidates(game)
        if expected_card_ids is not None:
            assert expected_card_ids == next_steps[0].card_ids
        assert game.choice == ""

    def test_select_process_1(self, get_step_classes):
        self.check(
            get_step_classes, 0, [Card(1, 1), Card(4, 2)],
            expected_next_steps=[AbstractStep],
            expected_candidates=["0:play:1#0", "0:play:4#0"])

    def test_select_process_2(self, get_step_classes):
        self.check(
            get_step_classes, 0, [Card(1, 1), Card(4, 2)],
            choice="0:play:4",
            expected_next_steps=[PlayStep],
            expected_card_ids=[4])

    def test_select_process_3(self, get_step_classes):
        self.check(
            get_step_classes, 0, [Card(1, 1), Card(4, 2)],
            choice="0:play:0",
            expected_next_steps=[])

    def test_select_process_4(self, get_step_classes):
        self.check(
            get_step_classes, 0, [Card(1, 1), Card(4, 2)],
            condition=CardCondition(type=CardType.STAR),
            expected_next_steps=[PlayStep],
            expected_card_ids=[4])

    def test_select_process_5(self, get_step_classes):
        self.check(
            get_step_classes, 0, [Card(1, 1)],
            condition=CardCondition(type=CardType.STAR),
            can_less=True,
            expected_next_steps=[])

    def test_select_process_6(self, get_step_classes):
        self.check(
            get_step_classes, 0, [Card(1, 1), Card(4, 2)],
            can_less=True,
            expected_next_steps=[AbstractStep],
            expected_candidates=[
                "0:play:1#0", "0:play:4#0", "0:play:0#0"])

    def test_select_process_7(self, get_step_classes):
        self.check(
            get_step_classes, 0, [Card(1, 1), Card(4, 2)],
            can_less=True,
            condition=CardCondition(type=CardType.STAR),
            expected_next_steps=[AbstractStep],
            expected_candidates=[
                "0:play:4#0", "0:play:0#0"])

    def test_select_process_8(self, get_step_classes):
        with pytest.raises(Exception):
            self.check(
                get_step_classes, 0, [Card(1, 1), Card(4, 2)],
                from_pilename=PileName.SUPPLY, count=2
            )

    def test_select_process_9(self, get_step_classes):
        self.check(
            get_step_classes, 0, [],
            choice="",
            from_pilename=PileName.SUPPLY, count=1,
            expected_candidates=[
                "0:play:3#0", "0:play:4#0", "0:play:5#0"
            ],
            expected_next_steps=[AbstractStep]
        )

    def test_select_process_10(self, get_step_classes):
        self.check(
            get_step_classes, 0, [],
            choice="",
            from_pilename=PileName.SUPPLY, count=0,
            expected_next_steps=[]
        )

    def test_select_process_11(self, get_step_classes):
        self.check(
            get_step_classes, 0, [],
            choice="",
            from_pilename=PileName.HAND,
            to_pilename=PileName.DISCARD, count=1,
            expected_next_steps=[], can_less=False
        )

    def test_select_process_29(
            self, get_step_classes):
        self.check(
            get_step_classes, 0,
            [Card(1, 1), Card(4, 2)],
            to_pilename=PileName.DECK,
            expected_next_steps=[AbstractStep], count=2,
            expected_candidates=["0:play:1,4#0", "0:play:4,1#0"])

    def test_select_process_30(
            self, get_step_classes):
        with pytest.raises(Exception):
            self.check(
                get_step_classes, 0,
                [Card(1, 1), Card(4, 2)],
                from_pilename=PileName.DECK,
                to_pilename=PileName.DISCARD,
                expected_next_steps=[AbstractStep], count=2,
                expected_candidates=["0:play:1,4#0", "0:play:4,1#0"])

    def test_select_process_31(
            self, get_step_classes):
        self.check(
            get_step_classes, 0,
            [Card(1, 1), Card(4, 2)],
            expected_next_steps=[AbstractStep], count=2,
            can_pass=True,
            expected_candidates=["0:play:1,4#0", "0:play:#0"])
