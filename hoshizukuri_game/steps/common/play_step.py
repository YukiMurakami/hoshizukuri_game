"""
Steps for trash a card.
"""
from __future__ import annotations
from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from ...models.game import Game
from ...models.pile import PileName
from .card_move_step import CardMoveStep
from ..abstract_step import AbstractStep
from ...utils.kingdom_step_util import get_kingdom_steps


class PlayStep(CardMoveStep):
    """
    Play cards step.

    Args:
        player_id (int): Player ID.
        depth (int): Expected log hierarchy.
        card_ids (List[int], Optional): Play card IDs.
        uniq_ids (List[int], Optional): Play card unique IDS.
        from_pilename (PileName, Optional): Play cards from this.
        process_effect (bool, Optional): Default is True.
    """
    def __init__(
            self, player_id: int, depth: int, card_ids: List[int] = None,
            uniq_ids: List[int] = [],
            from_pilename: PileName = PileName.HAND,
            process_effect: bool = True):
        super().__init__(
            player_id, depth, from_pilename=from_pilename,
            to_pilename=PileName.FIELD, card_ids=card_ids,
            uniq_ids=uniq_ids, count=None,
            next_step_callback=self._callback
        )
        self.process_effect = process_effect

    def _get_step_string(self):
        pilename = self.from_pilename.value
        orbit_index = "none"
        if self.orbit_index is not None:
            orbit_index = "%d" % self.orbit_index
        return "%d:play:%s:%d:%s:%s" % (
            self.depth,
            pilename,
            self.player_id, ",".join(
                ["%d-%d" % (self.card_ids[n], self.uniq_ids[
                    n]) for n in range(len(self.uniq_ids))]
            ),
            orbit_index
        )

    def process(self, game: Game):
        if self.from_pilename == PileName.FIELD:
            # don't move card, only effect
            return self._callback(self.card_ids, self.uniq_ids, game)
        return super().process(game)

    def _callback(
            self, card_ids: List[int], uniq_ids: List[int], game: Game):
        # process effects after cards are moved.
        steps = []
        if self.process_effect is False:
            return steps
        for card_id, uniq_id in zip(reversed(card_ids), reversed(uniq_ids)):
            step = get_kingdom_steps(
                self.player_id, self.depth + 1, card_id, uniq_id,
                org_id=card_id
            )
            steps += [
                PlayEndStep(self.player_id, self.depth, card_id, uniq_id),
                step
            ]
        return steps


class PlayEndStep(AbstractStep):
    """
    After process effect step.

    Args:
        player_id (int): turn player ID.
        depth (int): Expected log hierarchy.
        card_id (int): played card ID.
        uniq_id (int): played card unique ID.
    """
    def __init__(self, player_id: int, depth: int, card_id: int, uniq_id: int):
        super().__init__()
        self.player_id = player_id
        self.depth = depth
        self.card_id = card_id
        self.uniq_id = uniq_id

    def __str__(self):
        return "%d:playend:%d:%d-%d" % (
            self.depth, self.player_id, self.card_id, self.uniq_id)

    def process(self, game: Game):
        game.update_starflake()
        return []
