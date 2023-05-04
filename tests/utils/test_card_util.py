from hoshizukuri_game.utils.card_util import (
    get_card_id,
    get_expansion,
    get_original_name,
    get_types,
    ids2cards,
    is_same_card_ids,
    id2uniq_id,
    ids2uniq_ids,
    get_cost,
    get_count,
    is_create,
    get_colors,
    get_vp,
)
from hoshizukuri_game.models.game import Game
from hoshizukuri_game.models.card import CardType, Card, CardColor
from hoshizukuri_game.models.pile import Pile, PileType
from hoshizukuri_game.models.cost import Cost
import pytest


class TestCardUtil:
    def test_get_card_id_1(self):
        result = get_card_id("stardust")
        assert result == 1

    def test_get_card_id_2(self):
        result = get_card_id("Rock")
        assert result == 2

    def test_get_card_id_3(self):
        result = get_card_id("衛星")
        assert result == 3

    def test_get_expansion(self):
        result = get_expansion(10)
        assert result == "Base"

    def test_get_vp(self):
        assert get_vp(12) == 3
        assert get_vp(5) == 8

    def test_get_types(self):
        game = Game()
        result = get_types(get_card_id("satellite"), game)
        assert result == [CardType.STAR, CardType.INITIAL]

    def test_get_colors(self):
        game = Game()
        result = get_colors(get_card_id("flame"), game)
        assert result == [CardColor.RED]

    def test_id2uniqid_1(self):
        card_id = 8
        pile = Pile(PileType.LIST, card_list=[
            Card(4, 0), Card(4, 1), Card(1, 2),
            Card(8, 3), Card(8, 4)
        ])
        game = Game()
        uniq_id = id2uniq_id(pile, card_id, game)
        assert uniq_id == 3

    def test_id2uniqid_2(self):
        card_id = 9
        pile = Pile(PileType.LIST, card_list=[
            Card(4, 0), Card(4, 1), Card(1, 2),
            Card(8, 3), Card(8, 4)
        ])
        game = Game()
        with pytest.raises(Exception):
            id2uniq_id(pile, card_id, game)

    def test_ids2uniqids_1(self):
        card_ids = [4, 4]
        pile = Pile(PileType.LIST, card_list=[
            Card(4, 0), Card(4, 1), Card(1, 2),
            Card(8, 3), Card(8, 4)
        ])
        game = Game()
        uniq_ids = ids2uniq_ids(pile, card_ids, game)
        assert uniq_ids == [0, 1]

    def test_ids2uniqids_2(self):
        card_ids = [4, 7]
        pile = Pile(PileType.LIST, card_list=[
            Card(4, 0), Card(4, 1), Card(1, 2),
            Card(8, 3), Card(8, 4)
        ])
        game = Game()
        with pytest.raises(Exception):
            ids2uniq_ids(pile, card_ids, game)

    def test_get_cost_1(self):
        game = Game()
        cost = get_cost(get_card_id("star"), game)
        assert cost == Cost(10)

    def test_ids2cards(self):
        pile = Pile(PileType.LIST, card_list=[
            Card(1, 1), Card(1, 2), Card(2, 3), Card(1, 4)
        ])
        game = Game()
        cards = ids2cards(pile, card_ids=[1, 2], game=game)
        assert len(cards) == 2
        assert cards[0].id == 1
        assert cards[0].uniq_id == 1
        assert cards[1].id == 2
        assert cards[1].uniq_id == 3

    def test_get_count_1(self):
        pile = Pile(
            PileType.LIST, card_list=[
                Card(1, 1), Card(1, 2), Card(2, 3), Card(1, 4)
            ]
        )
        assert get_count(pile, 1) == 3

    def test_get_count_2(self):
        pile = Pile(
            PileType.NUMBER, card_id_and_count=[1, 8]
        )
        assert get_count(pile, 1) == 8

    def test_get_count_3(self):
        piles = [
            Pile(PileType.NUMBER, card_id_and_count=[1, 3]),
            Pile(PileType.NUMBER, card_id_and_count=[2, 4]),
            Pile(PileType.NUMBER, card_id_and_count=[3, 5])
        ]
        assert get_count(piles, 2) == 4

    def test_get_count_4(self):
        piles = {
            1: Pile(PileType.NUMBER, card_id_and_count=[1, 3]),
            2: Pile(PileType.NUMBER, card_id_and_count=[2, 4]),
            3: Pile(PileType.NUMBER, card_id_and_count=[3, 5])
        }
        assert get_count(piles, 2) == 4

    def test_get_count_5(self):
        card_list = [
            [
                Card(card_id=2, uniq_id=1),
            ],
            [
                Card(card_id=2, uniq_id=2),
                Card(card_id=2, uniq_id=3),
                Card(card_id=3, uniq_id=4),
            ]
        ]
        pile = Pile(PileType.LISTLIST, card_list=card_list)
        assert get_count(pile, 2) == 3

    def test_is_same_card_ids_1(self):
        assert is_same_card_ids([1, 2], [2, 1])

    def test_is_same_card_ids_2(self):
        assert is_same_card_ids([1, 2], [2]) is False

    def test_is_same_card_ids_3(self):
        assert is_same_card_ids([1, 2], [2, 2]) is False

    def test_get_original_name(self):
        assert get_original_name(1) == "Stardust"

    def test_is_create_1(self):
        assert is_create(1) is False

    def test_is_create_2(self):
        assert is_create(3)
