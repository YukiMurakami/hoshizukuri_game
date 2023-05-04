"""
Steps for starflake.
"""
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...models.game import Game
from ..abstract_step import AbstractStep


class AddStarflakeStep(AbstractStep):
    """
    Add starflake with an treasure card.

    Args:
        player_id (int): player who has added starflake.
        depth (int): Expected log hierarchy.
        add_starflake (int): the number of added starflakes.

    Note:
        - minus starflake token.
    """
    def __init__(self, player_id: int, depth: int, add_starflake: int):
        super().__init__()
        self.player_id = player_id
        self.depth = depth
        self.add_starflake = add_starflake

    def __str__(self):
        return "%d:addstarflake:%d:%d" % (
            self.depth, self.player_id, self.add_starflake)

    def process(self, game: Game):
        # Only turn player can get starflake.
        if game.turn.player_id == self.player_id:
            game.starflake += self.add_starflake
        return []
