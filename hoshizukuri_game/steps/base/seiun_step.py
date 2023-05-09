"""
Seiun card steps.
"""
from __future__ import annotations
from ..abstract_step import AbstractStep


class SeiunStep(AbstractStep):
    """
    Seiun card step.

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
        return "%d:seiun:%d" % (self.depth, self.player_id)
