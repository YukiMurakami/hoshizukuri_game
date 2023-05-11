"""
Seiza card steps.
"""
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...models.game import Game
from ..abstract_step import AbstractStep
from ...utils.card_util import get_card_id, get_colors, CardColor


class SeizaStep(AbstractStep):
    """
    Seiza card step.

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
        return "%d:seiza:%d" % (self.depth, self.player_id)

    def get_victory(self, game: Game):
        card_ids = game.players[self.player_id].get_own_card_ids()
        color_count = [0, 0, 0]
        for card_id in card_ids:
            if CardColor.RED in get_colors(card_id, game):
                color_count[0] += 1
            if CardColor.GREEN in get_colors(card_id, game):
                color_count[1] += 1
            if CardColor.BLUE in get_colors(card_id, game):
                color_count[2] += 1
        return min(color_count) * 3

    def get_victory_detail(self, game: Game):
        card_ids = game.players[self.player_id].get_own_card_ids()
        color_count = [0, 0, 0]
        for card_id in card_ids:
            if CardColor.RED in get_colors(card_id, game):
                color_count[0] += 1
            if CardColor.GREEN in get_colors(card_id, game):
                color_count[1] += 1
            if CardColor.BLUE in get_colors(card_id, game):
                color_count[2] += 1
        return "%d:Seiza: %d red, %d green, %d blue" % (
            get_card_id("seiza"), color_count[0],
            color_count[1], color_count[2])
