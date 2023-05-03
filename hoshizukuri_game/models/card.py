"""
This module defines the Card model.
"""
from __future__ import annotations
from enum import Enum


class CardType(Enum):
    STAR = "star"
    INITIAL = "initial"
    CELESTIAL = "celestial"


class Card:
    """Card model class.

    Args:
        card_id (int): Card ID by name.
        uniq_id (int): Unique ID for individual identification.

    Attributes:
        id (int): Card ID by name.
        uniq_id (int): Unique ID for individual identification.
    """
    def __init__(self, card_id: int, uniq_id: int):
        self.id = card_id
        self.uniq_id = uniq_id

    def __str__(self):
        return "%d-%d" % (self.id, self.uniq_id)
