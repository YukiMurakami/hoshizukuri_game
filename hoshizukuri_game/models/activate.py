"""
This module defines the Activate model.
"""
from __future__ import annotations
from typing import TYPE_CHECKING, Type
if TYPE_CHECKING:
    from ..models.game import Game


class TargetActivate:
    """
    Object to compare with Activates.
    """
    def __init__(
            self,
            activate_class: Type[Activate],
            player_id: int = None,
            card_id: int = None,
            uniq_id: int = None,
            uniq_turn: int = None):
        self.player_id = player_id
        self.card_id = card_id
        self.uniq_id = uniq_id
        self.activate_class = activate_class
        self.uniq_turn = uniq_turn

    def __str__(self):
        strings = []
        if self.player_id is not None:
            strings.append("player_id=%d" % self.player_id)
        if self.card_id is not None:
            strings.append("card_id=%d" % self.card_id)
        if self.uniq_id is not None:
            strings.append("uniq_id=%d" % self.uniq_id)
        if self.uniq_turn is not None:
            strings.append("uniq_turn=%d" % self.uniq_turn)
        return "target_activate:%s:%s" % (
            self.activate_class.__name__,
            ",".join(strings)
        )


class Activate:
    """
    Activate model class.
    This is base class of Activates.
    """
    def __init__(self):
        pass

    def __str__(self):
        return "act"


class ActivatePlaysetEnd(Activate):
    """
    When a player ends their play set, this activates.

    Args:
        player_id (int, optional): Who ends. When this is None,
            target is every players.
    """
    def __init__(
            self, player_id: int = None):
        self.player_id = player_id

    def __str__(self):
        p_str = "*" if self.player_id is None else "%d" % self.player_id
        return "act:playsetend:%s" % (p_str)


def is_match_activate(
        target_activate: TargetActivate, activate: Activate, game: Game):
    """
    Check if target_activate satisfies activate.

    Args:
        target_activate (TargetActivate): Target activate.
        activate (Activate): Activate used for checking.
        game (Game): now game.

    Returns:
        boolean: True is for that target activate satisfies activate.
    """
    if not isinstance(activate, target_activate.activate_class):
        return False
    if isinstance(activate, ActivatePlaysetEnd):
        if activate.player_id is not None:
            if target_activate.player_id is None:
                return False
            if target_activate.player_id != activate.player_id:
                return False
        return True
    raise Exception("Not found activate:", activate.__class__)
