"""
This module defines the utility functions about carddata.
"""
from __future__ import annotations
from typing import TYPE_CHECKING, List, Union, Dict
if TYPE_CHECKING:
    from ..models.card import Card
    from ..models.pile import Pile
    from ..models.game import Game
import os
import yaml
from ..models.cost import Cost
from ..models.card import CardType, CardColor


class CardData:
    singleton = None
    filename = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), '../carddata.yaml')
    cardinfo = {}
    name2iddic = {}

    def __new__(cls, *args, **kwargs):
        if cls.singleton is None:
            cls.singleton = super().__new__(cls)
            cls.cardinfo, cls.name2iddic = cls._load_carddata(
                cls.filename, cls._normalize_name
            )
        return cls.singleton

    def _normalize_name(name):
        """
        Normalize card name.
        This can remove spelling variants of cards.
        """
        name = name.lower()
        name = name.replace(" ", "").replace("'", "").replace("-", "")
        return name

    def _load_carddata(filename, normalize_name_func):
        cardinfo = {}
        name2iddic = {}
        with open(filename) as file:
            data = yaml.safe_load(file)
            for d in data:
                name = d["name"]
                jpn_name = d["japanese"]
                norm_name = normalize_name_func(name)
                cardinfo[d["id"]] = d
                cardinfo[d["id"]]["orgname"] = name
                cardinfo[d["id"]]["name"] = norm_name
                cardinfo[d["id"]]["japanese"] = jpn_name
                name2iddic[name] = d["id"]
                name2iddic[norm_name] = d["id"]
                name2iddic[jpn_name] = d["id"]
                cardinfo[d["id"]]["type"] = [
                    CardType(n) for n in d["type"].split("-")]
                cardinfo[d["id"]]["cost"] = Cost(d["cost"])
                cardinfo[d["id"]]["color"] = [
                    CardColor(n) for n in d["color"].split("-")]
        return cardinfo, name2iddic


def get_card_id(name: str):
    """
    Get card ID with card name.

    Args:
        name (str): card name.

    Returns:
        int: Card ID.
    """
    return CardData().name2iddic[name]


def get_original_name(card_id: int):
    """
    Get card origin name (without normalize) with card ID.

    Args:
        card_id (int): Card ID.

    Returns:
        str: Card original name.
    """
    return CardData().cardinfo[card_id]["orgname"]


def get_expansion(card_id: int):
    """
    Get expansion with card ID.

    Args:
        card_id (int): Card ID.

    Returns:
        str: Expansion name.
    """
    return CardData().cardinfo[card_id]["expansion"]


def get_vp(card_id: int):
    """
    Get vp with card ID.

    Args:
        card_id (int): Card ID.

    Returns:
        int: vp.
    """
    return CardData().cardinfo[card_id]["vp"]


def get_types(card_id: int, game: Game = None):
    """
    Get card types with card ID.

    Args:
        card_id (int): Card ID.
        game (Game, optional): Game. This is for checking game status.
            (Inheritance, .etc)

    Returns:
        List[CardType]: List of card types.
    """
    return CardData().cardinfo[card_id]["type"]


def get_colors(card_id: int, game: Game = None):
    """
    Get card colors with card ID.

    Args:
        card_id (int): Card ID.
        game (Game, optional): Game. This is for checking game status.
            (Inheritance, .etc)

    Returns:
        List[CardType]: List of card types.
    """
    return CardData().cardinfo[card_id]["color"]


def is_create(card_id: int):
    """
    Check if card_id is create.

    Args:
        card_id (int): Card ID.

    Returns:
        boolean: Create is True.
    """
    return CardData().cardinfo[card_id]["create"]


def id2uniq_id(pile: Pile, card_id: int, game: Game):
    """
    Get unique ID of the card which has card_id in pile.
    If there are many cards which has card_id,
    the first unique ID will be return.

    Args:
        pile (Pile): Only PileType.LIST.
        card_id (int): Target card ID.
        game (Game): now game.

    Returns:
        int: Unique card ID.
    """
    uniq_ids = ids2uniq_ids(pile, [card_id], game)
    return uniq_ids[0]


def ids2uniq_ids(pile: Pile, card_ids: List[int], game: Game):
    """
    Get unique IDs of the cards which have card_ids in pile.

    Args:
        pile (Pile): Only PileType.LIST.
        card_ids (List[int]): Target card IDs.
        game (Game): now game.

    Returns:
        List[int]: Unique card IDs.
    """
    result = []
    already_uniq_ids = []
    for card_id in card_ids:
        hit = False
        for card in pile.card_list:
            if card.id == card_id and card.uniq_id not in already_uniq_ids:
                result.append(card.uniq_id)
                already_uniq_ids.append(card.uniq_id)
                hit = True
                break
        if not hit:
            raise Exception("Not found card_id: %d" % card_id)
    return result


def ids2cards(pile: Pile, card_ids: List[int], game: Game) -> List[Card]:
    """
    Get Card list which have card_ids in pile.

    Args:
        pile (Pile): Only PileType.LIST.
        card_ids (List[int]): Target card IDs.
        game (Game): now game.

    Returns:
        List[Card]: Card list.
    """
    uniq_ids = ids2uniq_ids(pile, card_ids, game)
    result = []
    for uniq_id in uniq_ids:
        for card in pile.card_list:
            if card.uniq_id == uniq_id:
                result.append(card)
                break
    return result


def get_cost(card_id: int, game: Game) -> Cost:
    """
    Get cost of card ID.

    Args:
        card_id (int): Card ID.
        game (Game): now game.

    Returns:
        Cost: cost of the card.
    """
    cost: Cost = CardData().cardinfo[card_id]["cost"]
    return cost


def get_count(
        pile_or_piles: Union[Pile, List[Pile], Dict[int, Pile]],
        card_id: int):
    """
    Get the number of specific cards in pile.

    Args:
        pile_or_piles (Pile or List[Pile] or Dict[int, Pile]): Target pile.
        card_id (int): Card ID to count.

    Returns:
        int: the number of cards.
    """
    def sub_count(pile: Pile, card_id: int):
        count = 0
        if pile.type.value == "list":
            for card in pile.card_list:
                if card.id == card_id:
                    count += 1
        elif pile.type.value == "listlist":
            for card_list in pile.card_list:
                for card in card_list:
                    if card.id == card_id:
                        count += 1
        else:
            if pile.pile_card_id == card_id:
                count = pile.count
        return count

    if isinstance(pile_or_piles, list):
        count = 0
        for pile in pile_or_piles:
            count += sub_count(pile, card_id)
        return count
    if isinstance(pile_or_piles, dict):
        count = 0
        for pile in pile_or_piles.values():
            count += sub_count(pile, card_id)
        return count
    return sub_count(pile_or_piles, card_id)


def is_same_card_ids(a: List[int], b: List[int]):
    """
    Compare between two card IDs.

    Args:
        a (List[int]): card IDs.
        b (List[int]): card IDs.

    Returns:
        bool: True is same.
    """
    if len(a) != len(b):
        return False
    sort_a = sorted(a)
    sort_b = sorted(b)
    for i in range(len(sort_a)):
        if sort_a[i] != sort_b[i]:
            return False
    return True
