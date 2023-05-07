"""
This module defines the Card model.
"""
from __future__ import annotations
from ..utils.card_util import get_starflake, is_create


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
        self.starflake = get_starflake(card_id)
        self.create = is_create(card_id)

    def __str__(self):
        return "%d-%d" % (self.id, self.uniq_id)
