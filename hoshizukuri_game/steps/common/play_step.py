"""
Steps for trash a card.
"""
from __future__ import annotations
from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from ...models.game import Game
from ...models.pile import PileName
from .card_move_step import CardMoveStep
from ...utils.kingdom_step_util import get_kingdom_steps
from ...utils.card_util import is_create


class PlayStep(CardMoveStep):
    """
    Play cards step.

    Args:
        player_id (int): Player ID.
        depth (int): Expected log hierarchy.
        card_ids (List[int], Optional): Discard card IDs.
        uniq_ids (List[int], Optional): Discard card unique IDS.
        from_pilename (PileName, Optional): Discard cards from this.
        create (bool, Optional):
            None is Depending on the card.
            True is force to Create.
            False is force to not Create.
    """
    def __init__(
            self, player_id: int, depth: int, card_ids: List[int] = None,
            uniq_ids: List[int] = [],
            from_pilename: PileName = PileName.HAND,
            create: bool = None):
        super().__init__(
            player_id, depth, from_pilename=from_pilename,
            to_pilename=PileName.FIELD, card_ids=card_ids,
            uniq_ids=uniq_ids, count=None,
            next_step_callback=self._callback
        )
        self.create = create

    def _get_step_string(self):
        pilename = self.from_pilename.value
        return "%d:play:%s:%d:%s" % (
            self.depth,
            pilename,
            self.player_id, ",".join(
                ["%d-%d" % (self.card_ids[n], self.uniq_ids[
                    n]) for n in range(len(self.uniq_ids))]
            )
        )

    def _callback(
            self, card_ids: List[int], uniq_ids: List[int], game: Game):
        # process effects after cards are moved.
        steps = []
        for card_id, uniq_id in zip(reversed(card_ids), reversed(uniq_ids)):
            step = get_kingdom_steps(
                self.player_id, self.depth + 1, card_id, uniq_id,
                org_id=card_id
            )
            steps.append(step)
        # check create
        if self.create is None:
            for card_id in card_ids:
                if is_create(card_id):
                    game.created = True
        elif self.create is True:
            game.created = True
        return steps
