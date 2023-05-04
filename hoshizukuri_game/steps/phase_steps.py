"""
Steps for sequence of turn.
"""
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..models.game import Game
from ..models.turn import Turn
from .abstract_step import AbstractStep
from ..models.turn import Phase
from ..models.pile import PileName


class TurnStartStep(AbstractStep):
    """
    This is TurnStartStep.

    Args:
        player_id (int): turn player ID.
        turn (Turn): this turn.
    """
    def __init__(self, player_id: int, turn: Turn):
        super().__init__()
        self.player_id = player_id
        self.turn = turn
        self.depth = 0

    def __str__(self):
        return "%d:turnstart:%s" % (self.depth, str(self.turn))

    def process(self, game: Game):
        game.phase = Phase.TURN_START
        game.turn = self.turn
        assert game.turn.player_id == self.player_id
        game.coin = 0
        return []


class PrepareFirstDeckStep(AbstractStep):
    """
    Make player's first deck.

    Args:
        player_id (int): player ID.
    """
    def __init__(self, player_id):
        super().__init__()
        self.player_id = player_id
        self.depth = 0

    def __str__(self):
        return "%d:preparefirstdeck:%d" % (self.depth, self.player_id)

    def process(self, game: Game):
        for card_id in game.start_deck:
            card = game.make_card(card_id)
            game.players[self.player_id].pile[PileName.DISCARD].push(
                card
            )
        return []
