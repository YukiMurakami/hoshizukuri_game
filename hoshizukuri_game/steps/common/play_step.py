"""
Steps for trash a card.
"""
from __future__ import annotations
from typing import TYPE_CHECKING, Callable, List
if TYPE_CHECKING:
    from ...models.game import Game
from ...models.pile import PileName
from .card_move_step import CardMoveStep, select_process
from ..abstract_step import AbstractStep
from ...utils.kingdom_step_util import get_kingdom_steps
from ...models.card_condition import CardCondition
from ...models.log import Command, InvalidLogException, LogCondition


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
        add (bool, Optional): Default is False.
        orbit_index (int, Optional): Added card index.
    """
    def __init__(
            self, player_id: int, depth: int, card_ids: List[int] = None,
            uniq_ids: List[int] = [],
            from_pilename: PileName = PileName.HAND,
            process_effect: bool = True,
            add: bool = False,
            orbit_index: int = None):
        super().__init__(
            player_id, depth, from_pilename=from_pilename,
            to_pilename=PileName.FIELD, card_ids=card_ids,
            uniq_ids=uniq_ids, count=None,
            next_step_callback=self._callback
        )
        self.process_effect = process_effect
        self.orbit_index = orbit_index
        self.add = add

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

    def _get_log_condition(self):
        if self.add:
            if self.from_pilename == PileName.REVEAL:
                return LogCondition(
                    command=Command.ADD_PLAY_FROM_REVEAL,
                    player_id=self.player_id, depth=self.depth,
                    card_ids=self.card_ids
                )
            if self.from_pilename == PileName.HAND:
                return LogCondition(
                    command=Command.ADD_PLAY_FROM_HAND,
                    player_id=self.player_id, depth=self.depth,
                    card_ids=self.card_ids
                )
        return LogCondition(
            command=Command.PLAY, player_id=self.player_id,
            depth=self.depth,
            card_ids=self.card_ids
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
                step,
                _ProcessResolveLogStep(self.player_id, self.depth, card_id)
            ]
        return steps


class _ProcessResolveLogStep(AbstractStep):
    def __init__(self, player_id: int, depth: int, card_id: int):
        super().__init__()
        self.player_id = player_id
        self.depth = depth
        self.card_id = card_id

    def __str__(self):
        return "%d:processresolvelog:%d:%d" % (
            self.depth, self.player_id, self.card_id
        )

    def process(self, game: Game):
        if game.log_manager is not None:
            log_condition = LogCondition(
                Command.RESOLVE_EFFECT, self.player_id,
                self.depth, card_ids=[self.card_id]
            )
            log = game.log_manager.check_nextlog_and_pop(log_condition)
            if log is None:
                raise InvalidLogException(game, log_condition)
        return []


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


def play_add_select_process(
        game: Game, source_step: AbstractStep,
        choice_name: str, count: int,
        can_less: bool = False, from_pilename: PileName = PileName.HAND,
        card_condition: CardCondition = None,
        next_step_callback: Callable[
            [List[int], List[int], Game], List[AbstractStep]] = None,
        can_pass: bool = False):
    """
    Common process of selecting play_add cards.
    This function is assumed to be used in each Steps.

    Args:
        game (Game): now game.
        source_step (AbstractStep): the step which uses this process.
        choice_name (str): choice command.
        count (int): the number of play_added cards.
        can_less (bool): True is for that the number of play_adds can be less.
        from_pilename (PileName): This is where the card came from.
        card_condition (CardCondition, Optional): condition of play_adds cards.
        next_step_callback (Callable, Optional): After step, call this.
        can_pass (bool): True is for that can play_add nothing.
            When can_less is True, can_pass is meaningless.

    Returns:
        List[AbstractStep]: the next steps.
    """
    def create_step(
            player_id: int, depth: int,
            from_pilename: PileName, to_pilename: PileName,
            card_ids: List[int], uniq_ids: List[int]):
        orbit_index = len(game.players[player_id].pile[
            PileName.FIELD].card_list) - 1
        return PlayStep(
            player_id, depth, card_ids,
            uniq_ids=uniq_ids,
            from_pilename=from_pilename,
            process_effect=False,
            add=True,
            orbit_index=orbit_index
        )
    command = Command.ADD_PLAY_FROM_HAND
    log_condition = LogCondition(
        command=command, player_id=source_step.player_id,
        depth=source_step.depth
    )
    return select_process(
        create_step,
        game, source_step, choice_name, count,
        from_pilename, to_pilename=PileName.FIELD,
        can_less=can_less, can_pass=can_pass,
        card_condition=card_condition,
        log_condition=log_condition,
        next_step_callback=next_step_callback
    )
