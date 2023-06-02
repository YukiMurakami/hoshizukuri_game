"""
Steps for shuffle.
"""
from __future__ import annotations
from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from ...models.game import Game
from ..abstract_step import AbstractStep
from ...models.card import Card
from ...models.pile import PileName
from ...models.log import LogCondition, Command, InvalidLogException
import random


class ReshuffleStep(AbstractStep):
    """
    Reshuffle deck.

    Args:
        player_id (int): turn player ID.
        depth (int): Expected log hierarchy.

    TODO:
        - call reshuffle trigger.
    """
    def __init__(self, player_id: int, depth: int):
        super().__init__()
        self.player_id: int = player_id
        self.depth: int = depth
        self.deck_list: List[Card] = []

    def __str__(self):
        return "%d:reshuffle:%d:%s" % (self.depth, self.player_id, ",".join(
            ["%d-%d" % (n.id, n.uniq_id) for n in self.deck_list]))

    def process(self, game: Game):
        if game.players[self.player_id].pile[PileName.DISCARD].count > 0:
            if game.log_manager is not None:
                log_condition = LogCondition(
                    Command.SHUFFLE, self.player_id, depth=self.depth
                )
                log = game.log_manager.check_nextlog_and_pop(log_condition)
                if log is None:
                    raise InvalidLogException(game, log_condition)
            random.shuffle(
                game.players[self.player_id].pile[PileName.DISCARD].card_list)
            self.deck_list = list(
                game.players[self.player_id].pile[PileName.DISCARD].card_list)
            uniq_ids = [n.uniq_id for n in self.deck_list]
            game.move_card(
                game.players[self.player_id].pile[PileName.DISCARD],
                game.players[self.player_id].pile[PileName.DECK],
                uniq_ids=uniq_ids
            )
            return []
        return []
