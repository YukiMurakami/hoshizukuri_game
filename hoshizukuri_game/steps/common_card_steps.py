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


class StardustStep(AbstractStep):
    """
    Stardust card step.

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
        return "%d:stardust:%d" % (self.depth, self.player_id)

    def process(self, game: Game):
        return [AddStarflakeStep(self.player_id, self.depth, 1)]


class RockStep(AbstractStep):
    """
    Rock card step.

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
        return "%d:rock:%d" % (self.depth, self.player_id)

    def process(self, game: Game):
        return [AddStarflakeStep(self.player_id, self.depth, 2)]


class SatelliteStep(AbstractStep):
    """
    Satellite card step.

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
        return "%d:satellite:%d" % (self.depth, self.player_id)

    def process(self, game: Game):
        return [AddStarflakeStep(self.player_id, self.depth, 1)]

    def get_victory(self, game: Game):
        return 1


class PlanetStep(AbstractStep):
    """
    Planet card step.

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
        return "%d:planet:%d" % (self.depth, self.player_id)

    def process(self, game: Game):
        return [AddStarflakeStep(self.player_id, self.depth, 1)]

    def get_victory(self, game: Game):
        return 4


class StarStep(AbstractStep):
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
