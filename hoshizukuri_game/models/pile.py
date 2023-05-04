"""
This module defines the Pile model.
"""
from __future__ import annotations
from enum import Enum
from typing import TYPE_CHECKING, Union
if TYPE_CHECKING:
    from .card import Card
from typing import List


class PileName(Enum):
    DECK = "deck"
    """Player's deck."""
    HAND = "hand"
    """Player's hand."""
    FIELD = "field"
    """Player's field (play area)."""
    DISCARD = "discard"
    """Player's discard."""
    LOOK = "look"
    """Checked cards from deck."""
    REVEAL = "reveal"
    """Revealed cards from deck."""
    SUPPLY = "supply"
    TRASH = "trash"


class PileType(Enum):
    LIST = "list"
    """Need to distinguish between cards. (player's deck)"""
    LISTLIST = "listlist"
    """Need to divide card groups. (player's field)"""
    NUMBER = "number"
    """The cards are all the same. (supply pile)"""


class Pile:
    """Pile model class.

    This controls the list of Cards.
    There are two types depending on the application for capacity reduction
        and speed up.

    Args:
        pile_type (PileType): The type of pile.
        card_id_and_count (list[int], optional): Card ID and
            the number of cards. Required when PileType.NUMBER.
        card_list (list[Card] or list[list[Card]], optional):
            The list of Cards or the list of Cards.
            Required when PileTyle.LIST or PileType.LISTLIST.

    Attributes:
        type (PileType): The type of pile.
        pile_card_id (int): Card ID of pile.
            This is for empty supply.
            This is set automatically.
        count (int): The number of cards.
        card_list (list[Card] or list[list[Card]]):
            The list of Cards (Only LIST Type or LISTLIST Type).
    """
    def __init__(
            self, pile_type: PileType,
            card_id_and_count: List[int] = None,
            card_list: Union[List[Card], List[List[Card]]] = None
            ):
        self.type = pile_type
        self.pile_card_id = None
        self.count = 0
        self.card_list = []
        if pile_type == PileType.NUMBER:
            self.pile_card_id = card_id_and_count[0]
            self.count = card_id_and_count[1]
        elif pile_type == PileType.LIST:
            self.card_list = list(card_list)
            if len(card_list) > 0:
                self.pile_card_id = card_list[0].id
                self.count = len(card_list)
        elif pile_type == PileType.LISTLIST:
            self.card_list = list(card_list)
            if len(card_list) > 0:
                self.pile_card_id = card_list[0][0].id
                self.count = 0
                for pile in card_list:
                    self.count += len(pile)

    def __str__(self):
        if self.type == PileType.NUMBER:
            return "{%d:%d}" % (self.pile_card_id, self.count)
        if self.type == PileType.LIST:
            return "[%s]" % (
                ",".join(["%s" % n for n in self.card_list])
            )
        return "[%s]" % (
            ",".join(["[%s]" % ",".join([
                "%s" % n for n in card_list]) for card_list in self.card_list])
        )

    def index(self, card_id: int = None, uniq_id: int = None):
        """
        Get index of cardlist with card_id or uniq_id.
        This is for PileType.LIST.
        PileType.NUMBER returns -1.
        uniq_id is higher priority than card_id.
        This needs either card_id or uniq_id.

        Args:
            card_id (int, Optional): card ID.
            uniq_id (int, Optional): unique ID.

        Returns:
            int: index. When PileType.NUMBER or not found, -1.
        """
        if self.type == PileType.NUMBER:
            return -1
        elif self.type == PileType.LIST:
            if uniq_id is not None:
                for i, card in enumerate(self.card_list):
                    if card.uniq_id == uniq_id:
                        return i
                return -1
            for i, card in enumerate(self.card_list):
                if card.id == card_id:
                    return i
            return -1
        if uniq_id is not None:
            for i, card_list in enumerate(self.card_list):
                for card in card_list:
                    if card.uniq_id == uniq_id:
                        return i
            return -1
        for i, card_list in enumerate(self.card_list):
            for card in card_list:
                if card.id == card_id:
                    return i
        return -1

    def push(self, card: Card):
        """
        Add a card at the last position of pile.

        Args:
            card (Card): a card will be pushed into.
        """
        if self.type == PileType.LISTLIST:
            self.insert(card, len(self.card_list), 0)
        else:
            self.insert(card, self.count)

    def insert(self, card: Card, index: int, sub_index: int = None):
        """
        Add a card at the index position of pile.

        Args:
            card (Card): a card will be pushed into.
            index (int): position. -1 is the last.
            sub_index (int): sub index for PileType.LISTLIST. -1 is the last.
        """
        if self.type != PileType.NUMBER:
            if index == -1:
                index = len(self.card_list)
            if self.type == PileType.LISTLIST:
                assert sub_index is not None
                if sub_index == -1:
                    if index == len(self.card_list):
                        sub_index = 0
                    else:
                        sub_index = len(self.card_list[index])
            assert index >= 0 and index <= len(self.card_list)
        if self.type == PileType.LIST:
            self.card_list.insert(index, card)
            self.count = len(self.card_list)
        if self.type == PileType.NUMBER:
            assert self.pile_card_id == card.id
            self.count += 1
        if self.type == PileType.LISTLIST:
            assert sub_index is not None
            if index == len(self.card_list):
                self.card_list.append([])
            assert sub_index >= 0 and sub_index <= len(self.card_list[index])
            self.card_list[index].insert(sub_index, card)
            self.count += 1

    def remove_at(self, index: int, sub_index: int = None):
        """
        Remove a card at index.

        Args:
            index (int): index.
            sub_index (int): sub index for PileType.LISTLIST
        """
        if self.type != PileType.NUMBER:
            assert index >= 0 and index < len(self.card_list)
        if self.type == PileType.LIST:
            del self.card_list[index]
            self.count = len(self.card_list)
        elif self.type == PileType.NUMBER:
            self.count -= 1
        else:
            assert self.type == PileType.LISTLIST
            assert sub_index is not None
            assert sub_index >= 0 and sub_index < len(self.card_list[index])
            self.count -= 1
            del self.card_list[index][sub_index]
            if len(self.card_list[index]) == 0:
                del self.card_list[index]
