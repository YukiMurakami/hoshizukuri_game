"""
Steps for reveal cards.
"""
from __future__ import annotations
from typing import TYPE_CHECKING, List, Callable
if TYPE_CHECKING:
    from ...models.game import Game
from ..abstract_step import AbstractStep
from ...models.pile import PileName
from ...models.log import LogCondition, Command, InvalidLogException
from .card_move_step import CardMoveStep
from ...utils.card_util import ids2uniq_ids


class RevealStep(CardMoveStep):
    """
    Reveal some cards step.

    Args:
        player_id (int): Player ID.
        depth (int): Expected log hierarchy.
        card_ids (List[int], Optional): Reveal card IDs.
        uniq_ids (List[int], Optional): Reveal card unique IDS.
        count (int, Optional): the number of reveal cards.
        from_pilename (PileName, Optional): Reveal cards from this.
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
            to_pilename=PileName.REVEAL, card_ids=card_ids,
            uniq_ids=uniq_ids, count=count,
            next_step_callback=next_step_callback
        )

    def _get_from_deck_step_string(self, step):
        card_str = ",".join(["%d-%d" % (
            a.id, a.uniq_id) for a in step.card_list])
        return "%d:revealfromdeck:%d:%s" % (
            step.depth, step.player_id, card_str
        )

    def _get_step_string(self):
        if self.from_pilename == PileName.DECK:
            return "%d:pre-revealfromdeck:%d:%d" % (
                self.depth, self.player_id, self.count
            )
        pilename = self.from_pilename.value
        return "%d:reveal:%s:%d:%s" % (
            self.depth,
            pilename,
            self.player_id, ",".join(
                ["%d-%d" % (self.card_ids[n], self.uniq_ids[
                    n]) for n in range(len(self.uniq_ids))]
            )
        )

    def _get_log_condition(self):
        return LogCondition(
            Command.REVEAL_FROM_DECK,
            self.player_id, self.depth
        )


class RevealAllHandStep(AbstractStep):
    """
    Reveal all hand cards. (Don't move cards)

    Args:
        player_id (int): player ID.
        depth (int): Expected log hierarchy.
    """
    def __init__(self, player_id: int, depth: int):
        super().__init__()
        self.player_id = player_id
        self.depth = depth
        self.card_ids = []
        self.uniq_ids = []

    def __str__(self):
        return "%d:revealallhand:%d:%s" % (
            self.depth, self.player_id,
            ",".join(["%d-%d" % (card_id, uniq_id) for card_id, uniq_id in zip(
                self.card_ids, self.uniq_ids)]))

    def process(self, game: Game):
        self.card_ids = [n.id for n in game.players[
            self.player_id].pile[PileName.HAND].card_list]
        if game.log_manager is not None:
            log_condition = LogCondition(
                command=Command.REVEAL_ALL_HAND, player_id=self.player_id,
                depth=self.depth, card_ids=self.card_ids
            )
            log = game.log_manager.check_nextlog_and_pop(log_condition)
            if log is None:
                raise InvalidLogException(game, log_condition)
        self.uniq_ids = ids2uniq_ids(
            game.players[self.player_id].pile[PileName.HAND],
            self.card_ids, game
        )
        return []
