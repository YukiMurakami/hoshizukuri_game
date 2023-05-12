"""
Izumi card steps.
"""
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Dict
if TYPE_CHECKING:
    from ...models.game import Game
from ..abstract_step import AbstractStep
from ...models.pile import PileName
from ..common.look_step import LookStep
from ..common.option_step import option_select_process
from ..common.discard_step import DiscardStep
from ..common.putin_step import PutinHandStep


class IzumiStep(AbstractStep):
    """
    Izumi card step.

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
        return "%d:izumi:%d" % (self.depth, self.player_id)

    def callback(self, card_ids, uniq_ids, game: Game):
        if len(uniq_ids) <= 0:
            return []
        return [IzumiSelectStep(self.player_id, self.depth, self.uniq_id)]

    def process(self, game: Game):
        return [
            LookStep(
                self.player_id, self.depth, count=1,
                from_pilename=PileName.DECK,
                next_step_callback=self.callback
            )
        ]


class IzumiSelectStep(AbstractStep):
    """
    Izumi select hand or discard step.

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
        return "%d:izumiselect:%d" % (self.depth, self.player_id)

    def process(self, game: Game):
        return option_select_process(
            game, self, {
                "%d:izumi:hand" % self.player_id: self._hand_step,
                "%d:izumi:discard" % self.player_id: self._discard_step
            }
        )

    def _discard_step(self, game: Game, params: Dict[Any]):
        card = game.players[self.player_id].pile[PileName.LOOK].card_list[0]
        return [DiscardStep(
            self.player_id, self.depth, [card.id], [card.uniq_id],
            from_pilename=PileName.LOOK
        )]

    def _hand_step(self, game: Game, params: Dict[Any]):
        card = game.players[self.player_id].pile[PileName.LOOK].card_list[0]
        return [
            PutinHandStep(
                self.player_id, self.depth, [card.id], [card.uniq_id],
                from_pilename=PileName.LOOK
            )
        ]

    def _create_candidates(self, game: Game, params: Dict[Any]):
        return [
            "%d:izumi:hand" % self.player_id,
            "%d:izumi:discard" % self.player_id
        ]
