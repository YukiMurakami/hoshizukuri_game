"""
Suisho card steps.
"""
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...models.game import Game
from ..abstract_step import AbstractStep
from ...models.pile import PileName
from ..common.reveal_step import RevealStep
from ...models.card import Card


class SuishoStep(AbstractStep):
    """
    Suisho card step.

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
        return "%d:suisho:%d" % (self.depth, self.player_id)

    def process(self, game: Game):
        return [RevealStep(
            self.player_id, self.depth, count=1,
            from_pilename=PileName.DECK, next_step_callback=self.callback
        )]

    def callback(self, card_ids, uniq_ids, game: Game):
        if len(uniq_ids) <= 0:
            return []
        assert len(uniq_ids) == 1
        index = game.players[self.player_id].pile[
            PileName.REVEAL].index(uniq_id=uniq_ids[0])
        card: Card = game.players[self.player_id].pile[
            PileName.REVEAL].card_list[index]
        card.create = False
        from ..common.play_step import PlayStep
        orbit_index = len(game.players[self.player_id].pile[
            PileName.FIELD].card_list) - 1
        return [
            PlayStep(
                self.player_id, self.depth,
                card_ids=card_ids,
                uniq_ids=uniq_ids,
                from_pilename=PileName.REVEAL,
                process_effect=False,
                add=True,
                orbit_index=orbit_index
            )
        ]
