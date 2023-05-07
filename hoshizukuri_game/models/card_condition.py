"""
This module defines the CardCondition model.
"""
from __future__ import annotations
from typing import TYPE_CHECKING, Dict, List, Union
if TYPE_CHECKING:
    from ..models.game import Game
from .card import Card
from ..utils.card_util import CardType
from .cost import Cost
from .pile import Pile, PileType
from ..utils.card_util import (
    get_types, get_cost, is_create,
)


class CardCondition:
    """
    CardCondition model class.

    Args:
        card_id (int): Must be this card ID.
        uniq_id (int): Must be this unique card ID.
        card_ids (List[int]): Must be included in this card ID list.
        le_cost (Cost): Must be less equal than this cost.
        eq_cost (Cost): Must be equal this cost.
        type (CardType): Must be this card type.
        create (bool): this have to have "create".

    TODO:
        Cost, etc.
    """
    def __init__(
            self, card_id: int = None,
            uniq_id: int = None,
            card_ids: List[int] = None,
            le_cost: Cost = None,
            eq_cost: Cost = None,
            type: CardType = None,
            create: bool = None):
        self.card_id = card_id
        self.uniq_id = uniq_id
        self.card_ids = card_ids
        self.le_cost = le_cost
        self.eq_cost = eq_cost
        self.type = type
        self.create = create

    def __str__(self):
        strings = []
        if self.card_id is not None:
            strings.append("id=%d" % self.card_id)
        if self.uniq_id is not None:
            strings.append("uniq=%d" % self.uniq_id)
        if self.card_ids is not None:
            strings.append("ids=[%s]" % ",".join(
                [str(n) for n in self.card_ids]))
        if self.le_cost is not None:
            strings.append("cost<=%s" % str(self.le_cost))
        if self.eq_cost is not None:
            strings.append("cost=%s" % str(self.eq_cost))
        if self.type is not None:
            strings.append("type=%s" % self.type.value)
        if self.create is not None:
            strings.append("create=%s" % self.create)
        return ",".join(strings)


class CardConditionOr(CardCondition):
    """
    CardConditionOr model class.

    Args:
        conditions (List[CardCondition]): card conditions.
    """
    def __init__(self, conditions: List[CardCondition]):
        self.conditions = conditions

    def __str__(self):
        return "/".join([str(n) for n in self.conditions])


def get_match_card_ids(
        pile_or_piles: Union[Pile, List[Pile], Dict[int, Pile]],
        condition: CardCondition,
        game: Game, uniq_flag: bool = False):
    """
    Get list of card ids satisfied condition.

    Args:
        pile_or_piles (Pile or List[Pile] or Dict[int, Pile]): Target pile.
        condition (CardCondition): Condition.
        game (Game): Now game.
        uniq_flag (bool): True is for unique list.

    Returns:
        list[int]: List of card ids satisfied condition.
    """
    if isinstance(pile_or_piles, list):
        result = []
        for pile in pile_or_piles:
            result += get_match_card_ids(
                pile, condition, game, uniq_flag=uniq_flag)
        if uniq_flag:
            result = list(set(result))
        result = sorted(result)
        return result
    if isinstance(pile_or_piles, dict):
        result = []
        for pile in pile_or_piles.values():
            result += get_match_card_ids(
                pile, condition, game, uniq_flag=uniq_flag)
        if uniq_flag:
            result = list(set(result))
        result = sorted(result)
        return result
    assert isinstance(pile_or_piles, Pile)
    pile = pile_or_piles
    result = []
    if pile.type == PileType.LIST:
        for card in pile.card_list:
            if is_match_card(card, condition, game):
                result.append(card.id)
    else:
        for _ in range(pile.count):
            if is_match_card(Card(pile.pile_card_id, -1), condition, game):
                result.append(pile.pile_card_id)
    if uniq_flag:
        result = list(set(result))
    result = sorted(result)
    return result


def is_match_card(
        card: Card, condition: CardCondition, game: Game):
    """
    Check if card satisfies condition.

    Args:
        card (Card): Target card.
        condition (CardCondition): Condition.
        game (Game): Now game.

    Returns:
        boolean: If target card satisfies condition, True.
    """
    if isinstance(condition, CardConditionOr):
        for cond in condition.conditions:
            if is_match_card(card, cond, game):
                return True
        return False
    if condition.card_id is not None:
        if condition.card_id != card.id:
            return False
    if condition.uniq_id is not None:
        if condition.uniq_id != card.uniq_id:
            return False
    if condition.card_ids is not None:
        if card.id not in condition.card_ids:
            return False
    if condition.type is not None:
        types = get_types(card.id, game=game)
        if condition.type not in types:
            return False
    if condition.le_cost is not None:
        if (get_cost(card.id, game) <= condition.le_cost) is False:
            return False
    if condition.eq_cost is not None:
        if (get_cost(card.id, game) == condition.eq_cost) is False:
            return False
    if condition.create is not None:
        if condition.create != is_create(card.id):
            return False
    return True
