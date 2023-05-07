from hoshizukuri_game.models.card_condition import (
    CardCondition,
    CardConditionOr,
    is_match_card,
    get_match_card_ids
)
from hoshizukuri_game.models.cost import Cost
from hoshizukuri_game.utils.card_util import get_card_id, CardType
from hoshizukuri_game.models.card import Card
from hoshizukuri_game.models.game import Game
from hoshizukuri_game.models.pile import Pile, PileType


class TestCardCondition:
    def test_card_condition_str1(self):
        cond = CardCondition()
        assert str(cond) == ""

    def test_card_condition_str2(self):
        cond = CardCondition(card_id=1, uniq_id=3)
        assert str(cond) == "id=1,uniq=3"

    def test_card_condition_str3(self):
        cond = CardCondition(type=CardType.INITIAL)
        assert str(cond) == "type=initial"

    def test_card_condition_str4(self):
        cond = CardCondition(le_cost=Cost(3))
        assert str(cond) == "cost<=3"

    def test_card_condition_str5(self):
        cond = CardCondition(eq_cost=Cost(3))
        assert str(cond) == "cost=3"

    def test_card_condition_str6(self):
        cond = CardConditionOr([
            CardCondition(eq_cost=Cost(2)),
            CardCondition(eq_cost=Cost(3))])
        assert str(cond) == "cost=2/cost=3"

    def test_card_condition_str7(self):
        cond = CardCondition(card_ids=[1, 2, 3])
        assert str(cond) == "ids=[1,2,3]"

    def test_card_condition_str8(self):
        cond = CardCondition(create=True)
        assert str(cond) == "create=True"

    def test_card_condition_1(self):
        game = Game()
        cond = CardCondition(card_id=1)
        card = Card(1, 100)
        assert is_match_card(card, cond, game=game) is True

    def test_card_condition_2(self):
        game = Game()
        cond = CardCondition(card_id=1)
        card = Card(2, 100)
        assert is_match_card(card, cond, game=game) is False

    def test_card_condition_3(self):
        game = Game()
        cond = CardCondition(uniq_id=1)
        card = Card(2, 100)
        assert is_match_card(card, cond, game=game) is False

    def test_card_condition_4(self):
        game = Game()
        cond = CardCondition(type=CardType.CELESTIAL)
        card = Card(get_card_id("funka"), 100)
        assert is_match_card(card, cond, game=game) is True

    def test_card_condition_5(self):
        game = Game()
        cond = CardCondition(type=CardType.CELESTIAL)
        card = Card(get_card_id("kousei"), 100)
        assert is_match_card(card, cond, game=game) is False

    def test_card_condition_6(self):
        game = Game()
        cond = CardCondition(le_cost=Cost(3))
        card = Card(get_card_id("funka"), 100)
        assert is_match_card(card, cond, game=game) is True

    def test_card_condition_7(self):
        game = Game()
        cond = CardCondition(le_cost=Cost(2))
        card = Card(get_card_id("funka"), 100)
        assert is_match_card(card, cond, game=game) is False

    def test_card_condition_8(self):
        game = Game()
        cond = CardCondition(eq_cost=Cost(3))
        card = Card(get_card_id("funka"), 100)
        assert is_match_card(card, cond, game=game) is True

    def test_card_condition_9(self):
        game = Game()
        cond = CardCondition(eq_cost=Cost(3))
        card = Card(get_card_id("shinrin"), 100)
        assert is_match_card(card, cond, game=game) is False

    def test_card_condition_10(self):
        game = Game()
        cond = CardConditionOr([
            CardCondition(eq_cost=Cost(2)),
            CardCondition(eq_cost=Cost(3))])
        card1 = Card(get_card_id("shinrin"), 100)
        card2 = Card(get_card_id("funka"), 100)
        card3 = Card(get_card_id("mizu"), 100)
        assert is_match_card(card1, cond, game) is False
        assert is_match_card(card2, cond, game) is True
        assert is_match_card(card3, cond, game) is True

    def test_card_condition_11(self):
        game = Game()
        cond = CardCondition(card_ids=[1, 2, 3])
        assert is_match_card(Card(1, 10), cond, game) is True
        assert is_match_card(Card(4, 5), cond, game) is False

    def test_card_condition_12(self):
        game = Game()
        cond = CardCondition(create=True)
        assert is_match_card(Card(
            get_card_id("wakusei"), 10), cond, game) is True
        assert is_match_card(Card(
            get_card_id("hoshikuzu"), 5), cond, game) is False

    def test_get_match_card_ids1(self):
        game = Game()
        cond = CardCondition(type=CardType.STAR)
        pile = Pile(PileType.LIST, card_list=[
            Card(1, 6),
            Card(2, 7),
            Card(3, 8),
            Card(4, 9),
            Card(4, 10)
        ])
        result = get_match_card_ids(pile, cond, game, uniq_flag=True)
        assert result == [3, 4]

    def test_get_match_card_ids2(self):
        game = Game()
        cond = CardCondition(type=CardType.CELESTIAL)
        pile1 = Pile(PileType.LIST, card_list=[
            Card(1, 1),
            Card(6, 2),
            Card(8, 3),
            Card(1, 4),
            Card(9, 5)
        ])
        pile2 = Pile(PileType.LIST, card_list=[
            Card(1, 1),
            Card(6, 2),
            Card(10, 3),
            Card(1, 4),
            Card(10, 5)
        ])
        result = get_match_card_ids([pile1, pile2], cond, game)
        assert result == [6, 6, 8, 9, 10, 10]

    def test_get_match_card_ids3(self):
        game = Game()
        cond = CardCondition(type=CardType.CELESTIAL)
        pile1 = Pile(PileType.LIST, card_list=[
            Card(1, 1),
            Card(6, 2),
            Card(8, 3),
            Card(1, 4),
            Card(9, 5)
        ])
        pile2 = Pile(PileType.LIST, card_list=[
            Card(1, 1),
            Card(6, 2),
            Card(10, 3),
            Card(1, 4),
            Card(10, 5)
        ])
        result = get_match_card_ids([pile1, pile2], cond, game, uniq_flag=True)
        assert result == [6, 8, 9, 10]

    def test_get_match_card_ids4(self):
        game = Game()
        cond = CardCondition(type=CardType.CELESTIAL)
        piles = [
            Pile(PileType.NUMBER, card_id_and_count=[
                get_card_id("hoshikuzu"), 7]),
            Pile(PileType.NUMBER, card_id_and_count=[
                get_card_id("kousei"), 10]),
            Pile(PileType.NUMBER, card_id_and_count=[
                get_card_id("shinrin"), 10])
        ]

        result = get_match_card_ids(piles, cond, game, uniq_flag=True)
        assert result == [10]

    def test_get_match_card_ids5(self):
        game = Game()
        cond = CardCondition(type=CardType.CELESTIAL)
        piles = {
            get_card_id("hoshikuzu"): Pile(PileType.NUMBER, card_id_and_count=[
                get_card_id("hoshikuzu"), 7]),
            get_card_id("kousei"): Pile(PileType.NUMBER, card_id_and_count=[
                get_card_id("kousei"), 10]),
            get_card_id("shinrin"): Pile(PileType.NUMBER, card_id_and_count=[
                get_card_id("shinrin"), 10])
        }

        result = get_match_card_ids(piles, cond, game, uniq_flag=True)
        assert result == [10]
