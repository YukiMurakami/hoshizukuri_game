"""
This module defines the Turn model.
"""
from enum import Enum


class Phase(Enum):
    TURN_START = "turn_start"
    PLAY = "play"
    ORBIT = "orbit"
    GENERATE = "generate"
    CLEAN_UP = "cleanup"
    TURN_END = "turn_end"
    FINISH = "finish"


class TurnType(Enum):
    """
    Turn types.
    """
    NORMAL = "normal"
    """Normal player turn."""


class Turn:
    """Turn model class.

    This controls the turn.

    Args:
        turn (int): Now turn.
        uniq_turn (int): Now unique turn. (Increment even when extra turn.)
        player_id (int): Turn player ID.
        turn_type (TurnType): Turn type of this.

    Attributes:
        turn (int): Now turn.
        uniq_turn (int): Now unique turn. (Increment even when extra turn.)
        player_id (int): Turn player ID.
        turn_type (TurnType): Turn type of this.
    """
    def __init__(
            self, turn: int, uniq_turn: int,
            player_id: int, turn_type: TurnType):
        self.turn = turn
        self.uniq_turn = uniq_turn
        self.player_id = player_id
        self.turn_type = turn_type

    def __str__(self):
        return "%d:%d:%s:%d" % (
            self.turn,
            self.player_id,
            self.turn_type.value,
            self.player_id
        )
