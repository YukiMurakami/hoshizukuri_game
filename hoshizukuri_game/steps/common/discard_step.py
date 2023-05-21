"""
Steps for discard cards.
"""
from __future__ import annotations
from typing import TYPE_CHECKING, List, Callable
if TYPE_CHECKING:
    from ...models.game import Game
from ..abstract_step import AbstractStep
from ...models.pile import PileName
from ...models.card_condition import CardCondition
from .card_move_step import CardMoveStep, select_process


class DiscardStep(CardMoveStep):
    """
    Discard some cards step.

    Args:
        player_id (int): Player ID.
        depth (int): Expected log hierarchy.
        card_ids (List[int], Optional): Discard card IDs.
        uniq_ids (List[int], Optional): Discard card unique IDS.
        count (int, Optional): the number of discard cards.
        from_pilename (PileName, Optional): Discard cards from this.
        next_step_callback (Callable, Optional): After step, call this.

    Note:
        - call discard trigger step.
    """
    def __init__(
            self, player_id: int, depth: int, card_ids: List[int] = None,
            uniq_ids: List[int] = [], count: int = None,
            from_pilename: PileName = PileName.HAND,
            next_step_callback: Callable[
                [List[int], List[int], Game], List[AbstractStep]] = None):
        super().__init__(
            player_id, depth, from_pilename=from_pilename,
            to_pilename=PileName.DISCARD, card_ids=card_ids,
            uniq_ids=uniq_ids, count=count,
            next_step_callback=next_step_callback
        )

    def _get_from_deck_step_string(self, step):
        card_str = ",".join(["%d-%d" % (
            a.id, a.uniq_id) for a in step.card_list])
        return "%d:discardfromdeck:%d:%s" % (
            step.depth, step.player_id, card_str
        )

    def _get_step_string(self):
        if self.from_pilename == PileName.DECK:
            return "%d:pre-discardfromdeck:%d:%d" % (
                self.depth, self.player_id, self.count
            )
        pilename = self.from_pilename.value
        return "%d:discard:%s:%d:%s" % (
            self.depth,
            pilename,
            self.player_id, ",".join(
                ["%d-%d" % (self.card_ids[n], self.uniq_ids[
                    n]) for n in range(len(self.uniq_ids))]
            )
        )


def discard_select_process(
        game: Game, source_step: AbstractStep,
        choice_name: str, count: int,
        can_less: bool = False, from_pilename: PileName = PileName.HAND,
        next_step_callback: Callable[
            [List[int], List[int], Game], List[AbstractStep]] = None,
        card_condition: CardCondition = None,
        can_pass: bool = False):
    """
    Common process of selecting discard cards.
    This function is assumed to be used in each Steps.

    Args:
        game (Game): now game.
        source_step (AbstractStep): the step which uses this process.
        choice_name (str): choice command.
        count (int): the number of discarded cards.
        can_less (bool): True is for that the number of discards can be less.
        from_pilename (PileName): This is where the card came from.
        next_step_callback (Callable, Optional): After step, call this.
        card_condition (CardCondition, Optional): condition of discard cards.
        can_pass (bool): True is for that can discard nothing.
            When can_less is True, can_pass is meaningless.

    Returns:
        List[AbstractStep]: the next steps.
    """
    def create_step(
            player_id: int, depth: int,
            from_pilename: PileName, to_pilename: PileName,
            card_ids: List[int], uniq_ids: List[int]):
        return DiscardStep(
            player_id, depth, card_ids,
            uniq_ids=uniq_ids,
            from_pilename=from_pilename
        )
    return select_process(
        create_step,
        game, source_step, choice_name, count,
        from_pilename, to_pilename=PileName.DISCARD,
        can_less=can_less, can_pass=can_pass,
        next_step_callback=next_step_callback,
        card_condition=card_condition
    )
