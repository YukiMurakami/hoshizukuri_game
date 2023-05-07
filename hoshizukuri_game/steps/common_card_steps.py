"""
Common card steps.
"""
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..models.game import Game
from .abstract_step import AbstractStep
from .common.starflake_step import (
    AddStarflakeStep
)


class HoshikuzuStep(AbstractStep):
    """
    Hoshikuzu card step.

    Args:
        player_id (int): player ID.
        depth (int): Expected log hierarchy.
        uniq_id (int): unique ID.
    """
    def __init__(self, player_id: int, depth: int, uniq_id: int):
        super().__init__()
        self.player_id = player_id
        self.depth = depth
        self.uniq_id = uniq_id

    def __str__(self):
        return "%d:hoshikuzu:%d" % (self.depth, self.player_id)

    def process(self, game: Game):
        return [AddStarflakeStep(self.player_id, self.depth, 1)]


class GansekiStep(AbstractStep):
    """
    Ganseki card step.

    Args:
        player_id (int): player ID.
        depth (int): Expected log hierarchy.
        uniq_id (int): unique ID.
    """
    def __init__(self, player_id: int, depth: int, uniq_id: int):
        super().__init__()
        self.player_id = player_id
        self.depth = depth
        self.uniq_id = uniq_id

    def __str__(self):
        return "%d:ganseki:%d" % (self.depth, self.player_id)

    def process(self, game: Game):
        return [AddStarflakeStep(self.player_id, self.depth, 2)]


class EiseiStep(AbstractStep):
    """
    Eisei card step.

    Args:
        player_id (int): player ID.
        depth (int): Expected log hierarchy.
        uniq_id (int): unique ID.
    """
    def __init__(self, player_id: int, depth: int, uniq_id: int):
        super().__init__()
        self.player_id = player_id
        self.depth = depth
        self.uniq_id = uniq_id

    def __str__(self):
        return "%d:eisei:%d" % (self.depth, self.player_id)

    def process(self, game: Game):
        return [AddStarflakeStep(self.player_id, self.depth, 1)]

    def get_victory(self, game: Game):
        return 1


class WakuseiStep(AbstractStep):
    """
    Wakusei card step.

    Args:
        player_id (int): player ID.
        depth (int): Expected log hierarchy.
        uniq_id (int): unique ID.
    """
    def __init__(self, player_id: int, depth: int, uniq_id: int):
        super().__init__()
        self.player_id = player_id
        self.depth = depth
        self.uniq_id = uniq_id

    def __str__(self):
        return "%d:wakusei:%d" % (self.depth, self.player_id)

    def process(self, game: Game):
        return [AddStarflakeStep(self.player_id, self.depth, 1)]

    def get_victory(self, game: Game):
        return 4


class KouseiStep(AbstractStep):
    """
    Star card step.

    Args:
        player_id (int): player ID.
        depth (int): Expected log hierarchy.
        uniq_id (int): unique ID.
    """
    def __init__(self, player_id: int, depth: int, uniq_id: int):
        super().__init__()
        self.player_id = player_id
        self.depth = depth
        self.uniq_id = uniq_id

    def __str__(self):
        return "%d:star:%d" % (self.depth, self.player_id)

    def process(self, game: Game):
        return [AddStarflakeStep(self.player_id, self.depth, 1)]

    def get_victory(self, game: Game):
        return 8
