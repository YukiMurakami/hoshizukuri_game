"""
Ikaduchi card steps.
"""
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...models.game import Game
from ...models.pile import PileName
from ..abstract_step import AbstractStep
from ..common.trash_step import trash_select_process
from ..common.gain_step import gain_select_process
from ...models.card_condition import (
    CardCondition,
)
from ...utils.card_util import (
    get_cost,
)
from ...models.cost import Cost


class IkaduchiStep(AbstractStep):
    """
    Ikaduchi card step.

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
        return "%d:ikaduchi:%d" % (self.depth, self.player_id)

    def _callback(self, trash_ids, uniq_ids, game):
        if len(trash_ids) <= 0:
            return []
        return [_IkaduchiGainStep(
            self.player_id, self.depth, trash_ids[0])]

    def process(self, game: Game):
        return trash_select_process(
            game, self, "ikaduchitrash", 1, can_less=True,
            next_step_callback=self._callback
        )


class _IkaduchiGainStep(AbstractStep):
    def __init__(self, player_id: int, depth: int, trash_id: int):
        super().__init__()
        self.player_id: int = player_id
        self.depth: int = depth
        self.trash_id: int = trash_id
        self.gain_cost: Cost = Cost(0)

    def __str__(self):
        return "%d:ikaduchigain:%d:%s" % (
            self.depth, self.player_id, str(self.gain_cost))

    def process(self, game):
        trash_cost = get_cost(self.trash_id, game)
        self.gain_cost = trash_cost + Cost(2)
        return gain_select_process(
            game, self, "ikaduchigain", CardCondition(
                le_cost=self.gain_cost
            ), to_pilename=PileName.HAND
        )
