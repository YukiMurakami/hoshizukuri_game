"""
Steps for draw.
"""
from __future__ import annotations
from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from ...models.game import Game
from ..abstract_step import AbstractStep
from .shuffle_step import ReshuffleStep
from ...models.card import Card
from ...models.pile import PileName
from ...models.log import Command, InvalidLogException, LogCondition
from ...utils.card_util import ids2cards


class DrawStep(AbstractStep):
    """
    Draw with string "+N Cards".

    Args:
        player_id (int): draw player ID.
        depth (int): Expected log hierarchy.
        count (int): the number of draw cards.
    """
    def __init__(
            self, player_id: int, depth: int, count: int):
        super().__init__()
        self.player_id = player_id
        self.depth = depth
        self.count = count

    def __str__(self):
        return "%d:pre-draw:%d:%d" % (self.depth, self.player_id, self.count)

    def process(self, game: Game):
        deck_n = game.players[self.player_id].pile[PileName.DECK].count
        discard_n = game.players[self.player_id].pile[PileName.DISCARD].count
        if deck_n + discard_n < self.count:
            self.count = deck_n + discard_n
        if self.count <= 0:
            return []
        if deck_n < self.count:
            return [
                _ActualDrawStep(
                    self.player_id, self.depth, self.count),
                ReshuffleStep(self.player_id, self.depth)
            ]
        return [_ActualDrawStep(
            self.player_id, self.depth, self.count)]


class _ActualDrawStep(AbstractStep):
    def __init__(self, player_id, depth, count):
        super().__init__()
        self.player_id = player_id
        self.depth = depth
        self.count = count
        self.draw_list: List[Card] = []

    def __str__(self):
        return "%d:draw:%d:%s" % (
            self.depth,
            self.player_id,
            ",".join(["%d-%d" % (n.id, n.uniq_id) for n in self.draw_list])
        )

    def process(self, game: Game):
        self.draw_list = list(game.players[
            self.player_id].pile[PileName.DECK].card_list[:self.count])
        if game.log_manager is not None:
            command = Command.DRAW
            log_condition = LogCondition(
                command=command, player_id=self.player_id,
                depth=self.depth
            )
            log = game.log_manager.check_nextlog_and_pop(log_condition)
            if log is None:
                raise InvalidLogException(game, log_condition)
            self.draw_list = ids2cards(
                game.players[self.player_id].pile[PileName.DECK],
                log.card_ids, game
            )
        game.move_card(
            game.players[self.player_id].pile[PileName.DECK],
            game.players[self.player_id].pile[PileName.HAND],
            uniq_ids=[n.uniq_id for n in self.draw_list]
        )
        return []
