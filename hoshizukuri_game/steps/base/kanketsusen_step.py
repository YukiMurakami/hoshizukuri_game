"""
Kanketsusen card steps.
"""
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...models.game import Game
from ..abstract_step import AbstractStep
from ..common.draw_step import DrawStep


class KanketsusenStep(AbstractStep):
    """
    Kanketsusen card step.

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
        return "%d:kanketsusen:%d" % (self.depth, self.player_id)

    def process(self, game: Game):
        return [DrawStep(self.player_id, self.depth, 3)]
