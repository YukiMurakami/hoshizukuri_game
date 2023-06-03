"""
Daichi card steps.
"""
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...models.game import Game
from ...models.pile import PileName
from ...models.trigger import Trigger
from ...models.activate import ActivatePlaysetEnd
from ...models.limit import LimitTriggerActivate
from ...models.log import Command, LogCondition
from ..abstract_step import AbstractStep
from ..common.gain_step import GainStep
from ..common.trash_step import TrashStep
from ...utils.card_util import get_card_id


class DaichiStep(AbstractStep):
    """
    Daichi card step.

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
        return "%d:daichi:%d" % (self.depth, self.player_id)

    def process(self, game: Game):
        count = len(game.players[self.player_id].pile[
            PileName.FIELD].card_list[-1])
        if count >= 5:
            game.triggers.append(
                Trigger(
                    limit=LimitTriggerActivate(None),
                    activate=ActivatePlaysetEnd(self.player_id),
                    step=_DaichiTriggerStep(
                        self.player_id, self.depth, self.uniq_id),
                    auto=True
                )
            )
            return [GainStep(
                self.player_id, self.depth, card_id=get_card_id("kousei")
            )]
        return [GainStep(
            self.player_id, self.depth, card_id=get_card_id("wakusei"))]


class _DaichiTriggerStep(AbstractStep):
    def __init__(self, player_id: int, depth: int, uniq_id: int):
        super().__init__()
        self.player_id = player_id
        self.depth = depth
        self.uniq_id = uniq_id
        self.card_id = get_card_id("daichi")

    def __str__(self):
        return "%d:daichitrigger:%d:%d-%d" % (
            self.depth, self.player_id,
            get_card_id("daichi"), self.uniq_id)

    def process(self, game: Game):
        index = game.players[self.player_id].pile[
            PileName.FIELD].index(uniq_id=self.uniq_id)
        if index == -1:
            return []
        trash_step = TrashStep(
            self.player_id, self.depth, [self.card_id], [self.uniq_id],
            from_pilename=PileName.FIELD
        )
        trash_step.orbit_index = index
        return [trash_step]

    def get_trigger_name(self):
        return "daichi:%d-%d" % (
            self.card_id, self.uniq_id
        )

    def get_trigger_log_condition(self, game) -> LogCondition:
        return LogCondition(
            Command.TRASH_FROM_PLAYAREA, self.player_id, self.depth,
            card_ids=[get_card_id("daichi")]
        )
