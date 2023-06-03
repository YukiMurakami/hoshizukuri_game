"""
Steps for trash a card.
"""
from __future__ import annotations
from typing import TYPE_CHECKING, List, Callable
if TYPE_CHECKING:
    from ...models.game import Game
from ..abstract_step import AbstractStep
from enum import Enum
from ...models.card_condition import CardCondition
from ...models.pile import PileName
from ...models.log import LogCondition, Command
from ..common.card_move_step import CardMoveStep, select_process


class TrashBy(Enum):
    NORMAL = "normal"


class TrashStep(CardMoveStep):
    """
    Trash cards step.

    Args:
        player_id (int): player ID who trashes cards.
        depth (int): Expected log hierarchy.
        card_ids (List[int], Optional): trashed card IDs.
        uniq_ids (List[int], Optional): trashed unique IDs.
        count (int, Optional): the number of trashed cards.
        from_pilename (PileName, Optional): Pilename of the pile which
            trashed card came from. Default is PileName.HAND.
        by (TrashBy, Optional): What caused this trash.
        next_step_callback (Callable, Optional): After step, call this.
    """
    def __init__(
            self, player_id: int, depth: int, card_ids: List[int] = None,
            uniq_ids: List[int] = [], count: int = None,
            from_pilename: PileName = PileName.HAND,
            by: TrashBy = TrashBy.NORMAL,
            next_step_callback: Callable[
                [List[int], List[int], Game], List[AbstractStep]] = None):
        super().__init__(
            player_id, depth, from_pilename, PileName.TRASH,
            card_ids=card_ids, uniq_ids=uniq_ids, count=count,
            next_step_callback=next_step_callback
        )
        self.by = by

    def _get_from_deck_step_string(self, step):
        card_str = ",".join(["%d-%d" % (
            a.id, a.uniq_id) for a in step.card_list])
        return "%d:trashfromdeck:%d:%s" % (
            step.depth, step.player_id, card_str
        )

    def _get_step_string(self):
        if self.from_pilename == PileName.DECK:
            return "%d:pre-trashfromdeck:%d:%d" % (
                self.depth, self.player_id, self.count
            )
        pilename = self.from_pilename.value
        return "%d:trash:%s:%d:%s" % (
            self.depth,
            pilename,
            self.player_id, ",".join(
                ["%d-%d" % (self.card_ids[n], self.uniq_ids[
                    n]) for n in range(len(self.uniq_ids))]
            )
        )

    def _get_log_condition(self):
        if self.from_pilename == PileName.HAND:
            return LogCondition(
                Command.TRASH_FROM_HAND, self.player_id, self.depth,
                card_ids=self.card_ids
            )
        if self.from_pilename == PileName.FIELD:
            return LogCondition(
                Command.TRASH_FROM_PLAYAREA, self.player_id, self.depth,
                card_ids=self.card_ids
            )
        return None


def trash_select_process(
        game: Game, source_step: AbstractStep,
        choice_name: str, count: int,
        can_less: bool = False, from_pilename: PileName = PileName.HAND,
        card_condition: CardCondition = None,
        next_step_callback: Callable[
            [List[int], List[int], Game], List[AbstractStep]] = None,
        can_pass: bool = False):
    """
    Common process of selecting trash cards.
    This function is assumed to be used in each Steps.

    Args:
        game (Game): now game.
        source_step (AbstractStep): the step which uses this process.
        choice_name (str): choice command.
        count (int): the number of trashed cards.
        can_less (bool): True is for that the number of trashs can be less.
        from_pilename (PileName): This is where the card came from.
        card_condition (CardCondition, Optional): condition of trashed cards.
        next_step_callback (Callable, Optional): After step, call this.
        can_pass (bool): True is for that can trash nothing.
            When can_less is True, can_pass is meaningless.

    Returns:
        List[AbstractStep]: the next steps.
    """
    def create_step(
            player_id: int, depth: int,
            from_pilename: PileName, to_pilename: PileName,
            card_ids: List[int], uniq_ids: List[int]):
        return TrashStep(
            player_id, depth, card_ids,
            uniq_ids=uniq_ids,
            from_pilename=from_pilename
        )
    command = Command.TRASH_FROM_HAND
    log_condition = LogCondition(
        command=command, player_id=source_step.player_id,
        depth=source_step.depth
    )
    return select_process(
        create_step,
        game, source_step, choice_name, count,
        from_pilename, to_pilename=PileName.TRASH,
        can_less=can_less, can_pass=can_pass,
        log_condition=log_condition,
        card_condition=card_condition,
        next_step_callback=next_step_callback
    )
