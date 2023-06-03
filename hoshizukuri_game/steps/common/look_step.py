"""
Steps for look cards.
"""
from __future__ import annotations
from typing import TYPE_CHECKING, List, Callable
if TYPE_CHECKING:
    from ...models.game import Game
from ..abstract_step import AbstractStep
from ...models.pile import PileName
from ...models.log import LogCondition, Command
from .card_move_step import CardMoveStep


class LookStep(CardMoveStep):
    """
    Look some cards step.

    Args:
        player_id (int): Player ID.
        depth (int): Expected log hierarchy.
        card_ids (List[int], Optional): Look card IDs.
        uniq_ids (List[int], Optional): Look card unique IDS.
        count (int, Optional): the number of look cards.
        from_pilename (PileName, Optional): Look cards from this.
        next_step_callback (Callable, Optional): After step, call this.
    """
    def __init__(
            self, player_id: int, depth: int, card_ids: List[int] = None,
            uniq_ids: List[int] = [], count: int = None,
            from_pilename: PileName = PileName.HAND,
            next_step_callback: Callable[
                [List[int], List[int], Game], List[AbstractStep]] = None):
        super().__init__(
            player_id, depth, from_pilename=from_pilename,
            to_pilename=PileName.LOOK, card_ids=card_ids,
            uniq_ids=uniq_ids, count=count,
            next_step_callback=next_step_callback
        )

    def _get_from_deck_step_string(self, step):
        card_str = ",".join(["%d-%d" % (
            a.id, a.uniq_id) for a in step.card_list])
        return "%d:lookfromdeck:%d:%s" % (
            step.depth, step.player_id, card_str
        )

    def _get_step_string(self):
        if self.from_pilename == PileName.DECK:
            return "%d:pre-lookfromdeck:%d:%d" % (
                self.depth, self.player_id, self.count
            )
        pilename = self.from_pilename.value
        return "%d:look:%s:%d:%s" % (
            self.depth,
            pilename,
            self.player_id, ",".join(
                ["%d-%d" % (self.card_ids[n], self.uniq_ids[
                    n]) for n in range(len(self.uniq_ids))]
            )
        )

    def _get_log_condition(self):
        return LogCondition(
            Command.LOOK_FROM_DECK,
            self.player_id, self.depth
        )
