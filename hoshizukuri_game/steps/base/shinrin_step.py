"""
Shinrin card steps.
"""
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...models.game import Game
from ..abstract_step import AbstractStep
from ...models.card_condition import CardCondition
from ...utils.card_util import CardColor


class ShinrinStep(AbstractStep):
    """
    Shinrin card step.

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
        return "%d:shinrin:%d" % (self.depth, self.player_id)

    def process(self, game: Game):
        from ..common.play_step import play_add_select_process
        return play_add_select_process(
            game, self, "shinrinaddplay", 1, can_less=True,
            card_condition=CardCondition(
                create=False, color=CardColor.NEUTRAL
            )
        )
