"""
Steps for gain a card.
"""
from __future__ import annotations
from typing import TYPE_CHECKING, Callable, List
if TYPE_CHECKING:
    from ...models.game import Game
from enum import Enum
from ..abstract_step import AbstractStep
from ...steps.common.card_move_step import CardMoveStep, select_process
from ...models.pile import PileName
from ...models.card_condition import CardCondition


class GainBy(Enum):
    NORMAL = "normal"


class GainStep(CardMoveStep):
    """
    Gain some cards step.

    Args:
        player_id (int): Player ID.
        depth (int): Expected log hierarchy.
        card_id (int, Optional): Gain card ID.
        uniq_id (int, Optional): Gain card unique ID. (This is for from trash)
        from_pilename (PileName, Optional): Gain cards from this.
        to_pilename (PileName, Optional): Gain cards will go.
        by (GainBy, Optional): What caused this gain.
        next_step_callback (Callable, Optional): After step, call this.

    Note:
        - call gain trigger step.
    """
    def __init__(
            self, player_id: int, depth: int, card_id: int = None,
            uniq_id: int = None,
            from_pilename: PileName = PileName.SUPPLY,
            to_pilename: PileName = PileName.DISCARD,
            by: GainBy = GainBy.NORMAL,
            next_step_callback: Callable[
                [List[int], List[int], Game], List[AbstractStep]] = None):
        assert from_pilename in [
            PileName.SUPPLY, PileName.TRASH]
        uniq_ids = []
        if uniq_id is not None:
            uniq_ids = [uniq_id]
        super().__init__(
            player_id, depth, from_pilename=from_pilename,
            to_pilename=to_pilename, card_ids=[card_id],
            uniq_ids=uniq_ids, count=None,
            next_step_callback=next_step_callback,
        )

    def _get_step_string(self):
        pilename = self.from_pilename.value
        to_pilename = self.to_pilename.value
        gain_str = "%d" % self.card_ids[0]
        if len(self.uniq_ids) == 1:
            gain_str = "%d-%d" % (self.card_ids[0], self.uniq_ids[0])
        return "%d:gain:%s:%d:%s:%s" % (
            self.depth,
            pilename,
            self.player_id, gain_str, to_pilename
        )


def gain_select_process(
        game: Game, source_step: AbstractStep,
        choice_name: str, condition: CardCondition,
        can_pass: bool = False, to_pilename: PileName = PileName.DISCARD,
        select_player_id: int = None,
        next_step_callback: Callable[
            [int, int, Game], List[AbstractStep]] = None,
        from_pilename: PileName = PileName.SUPPLY):
    """
    Common process of selecting gain a card.
    This function is assumed to be used in each Steps.

    Args:
        game (Game): now game.
        source_step (AbstractStep): the step which uses this process.
        choice_name (str): choice command.
        condition (CardCondition): This limits the possibility of gains.
        can_pass (bool): True is for that player can choose gain nothing.
        to_pilename (PileName): This is where the card will go to.
        select_player_id (int, Optional): select player ID.
            When this is None, source_step.player_id will be used.
        next_step_callback (Callable, Optional): steps after this.
        from_pilename (PileName, Optional): SUPPLY or TRASH.

    Returns:
        List[AbstractStep]: the next steps.
    """
    def create_step(
            player_id: int, depth: int,
            from_pilename: PileName, to_pilename: PileName,
            card_ids: List[int], uniq_ids: List[int]):
        uniq_id = None
        if len(uniq_ids) == 1:
            uniq_id = uniq_ids[0]
        assert len(card_ids) == 1
        return GainStep(
            player_id, depth, card_ids[0],
            uniq_id=uniq_id,
            from_pilename=from_pilename,
            to_pilename=to_pilename,
            next_step_callback=next_step_callback
        )
    return select_process(
        create_step,
        game, source_step, choice_name, 1,
        from_pilename, to_pilename=to_pilename,
        select_player_id=select_player_id,
        can_less=can_pass, can_pass=can_pass,
        card_condition=condition
    )
