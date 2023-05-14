"""
This module defines the Limit model.

Limit defines the lifetime of variables
    and triggers during each turn routine.
"""
from __future__ import annotations
from typing import Type


class TargetLimit:
    """
    Object to compare with Limits.
    """
    def __init__(
            self,
            limit_class: Type[Limit],
            player_id: int = None,
            trigger_id: str = None,
            card_id: int = None,
            uniq_id: int = None,
            uniq_turn: int = None):
        self.player_id = player_id
        self.limit_class = limit_class
        self.trigger_id = trigger_id
        self.card_id = card_id
        self.uniq_id = uniq_id
        self.uniq_turn = uniq_turn


class Limit:
    """
    Limit model class.
    This is base class of Limits.
    """
    def __init__(self):
        pass

    def __str__(self):
        return "limit"


class LimitOr(Limit):
    """
    Limit which has OR conditions.

    Args:
        limits (List[Limit]): Limit list.
    """
    def __init__(self, limits):
        self.limits = list(limits)

    def __str__(self):
        return "limit:or:[%s]" % (
            ",".join(str(n) for n in self.limits))


class LimitTriggerActivate(Limit):
    """
    Lifetime is until the trigger will be activated.

    Args:
        trigger_id (str): Trigger unique ID.

    Note:
        - When trigger_id is None, this will be set during added in trigger.
    """
    def __init__(self, trigger_id: str):
        super().__init__()
        self.trigger_id = trigger_id

    def __str__(self):
        trigger_id = "None"
        if self.trigger_id is not None:
            trigger_id = self.trigger_id
        return "limit:trigger_activate:%s" % trigger_id


class LimitForever(Limit):
    """
    Lifetime is forever.
    """
    def __init__(self):
        pass

    def __str__(self):
        return "limit:forever"


def is_match_limit(target_limit: TargetLimit, limit: Limit):
    """
    Check if target_limit satisfies limit.

    Args:
        target_limit (TargetLimit): Target limit.
        limit (Limit): Limit used for checking.

    Returns:
        boolean: True is for that target limit satisfies limit.
    """
    if isinstance(limit, LimitOr):
        for c_limit in limit.limits:
            if is_match_limit(target_limit, c_limit):
                return True
        return False
    if not isinstance(limit, target_limit.limit_class):
        return False
    if isinstance(limit, LimitTriggerActivate):
        return target_limit.trigger_id == limit.trigger_id
    raise Exception("Not found limit:", limit.__class__)
