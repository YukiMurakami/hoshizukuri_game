"""
Funka card steps.
"""
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...models.game import Game
from ...models.pile import PileName
from ..abstract_step import AbstractStep
from ..common.discard_step import DiscardStep


class FunkaStep(AbstractStep):
    """
    Funka card step.

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
        return "%d:funka:%d" % (self.depth, self.player_id)

    def process(self, game: Game):
        card_ids = [n.id for n in game.players[
            self.player_id].pile[PileName.HAND].card_list]
        uniq_ids = [n.uniq_id for n in game.players[
            self.player_id].pile[PileName.HAND].card_list]
        if len(card_ids) <= 0:
            return []
        return [DiscardStep(
            self.player_id, self.depth,
            card_ids, uniq_ids
        )]
