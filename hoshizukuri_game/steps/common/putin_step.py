"""
Steps for put in hand cards.
"""
from __future__ import annotations
from typing import List
from ...models.pile import PileName
from .card_move_step import CardMoveStep


class PutinHandStep(CardMoveStep):
    """
    PutinHand some cards step.

    Args:
        player_id (int): Player ID.
        depth (int): Expected log hierarchy.
        card_ids (List[int], Optional): PutinHand card IDs.
        uniq_ids (List[int], Optional): PutinHand card unique IDS.
        from_pilename (PileName, Optional): PutinHand cards from this.

    Note:
        from_pilename is PileName.DECK use DrawStep!
    """
    def __init__(
            self, player_id: int, depth: int, card_ids: List[int] = None,
            uniq_ids: List[int] = [],
            from_pilename: PileName = PileName.LOOK):
        super().__init__(
            player_id, depth, from_pilename=from_pilename,
            to_pilename=PileName.HAND, card_ids=card_ids,
            uniq_ids=uniq_ids
        )

    def _get_step_string(self):
        pilename = self.from_pilename.value
        return "%d:putinhand:%s:%d:%s" % (
            self.depth,
            pilename,
            self.player_id, ",".join(
                ["%d-%d" % (self.card_ids[n], self.uniq_ids[
                    n]) for n in range(len(self.uniq_ids))]
            )
        )
