"""
Sougen card steps.
"""
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...models.game import Game
from ..abstract_step import AbstractStep
from ...models.card_condition import CardCondition
from ...models.pile import PileName
from ...models.cost import Cost
from ..common.gain_step import gain_select_process
from ...utils.card_util import get_card_id


class SougenStep(AbstractStep):
    """
    Sougen card step.

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
        return "%d:sougen:%d" % (self.depth, self.player_id)

    def process(self, game: Game):
        count = len(game.players[self.player_id].pile[
            PileName.FIELD].card_list[-1]) + 2
        return gain_select_process(
            game, self, "sougengain",
            CardCondition(
                le_cost=Cost(count),
                not_card_id=get_card_id("sougen")
            ),
            can_pass=True
        )
