"""
This module defines the Variable model.
"""
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Type, Union
if TYPE_CHECKING:
    from .game import Game, Player
from .limit import Limit, TargetLimit, is_match_limit
from enum import Enum


class VariableName(Enum):
    DONE_TRIGGER_LIST = "done_trigger_list"


class Variable:
    """
    Variable model class.

    Args:
        limit (Limit): the limit of this variable.
        type (Type): the type of this variable.

    Arrtibutes:
        value (Any): the value of this variable.
    """
    def __init__(self, limit: Limit, type: Type):
        self.limit = limit
        self.type = type
        if type == list:
            self.value = []
        elif type == int:
            self.value = 0
        else:
            raise Exception("Unsupported Variable type: %s" % str(self.type))

    def set_value(self, value: Any):
        """
        Set value.

        Args:
            value (Any): set value
        """
        if self.type == list:
            self.value.append(value)
        if self.type == int:
            self.value = value


def remove_variables(game: Game, target_limit: TargetLimit):
    """
    Remove variables from game with target limit.

    Args:
        game (Game): now game
        target_limit (TargetLimit): target limit.
    """
    copy_variables = dict(game.variables)
    for name, variable in game.variables.items():
        if is_match_limit(target_limit, variable.limit):
            del copy_variables[name]
    game.variables = copy_variables
    """
    for player_id in range(len(game.players)):
        copy_variables = dict(game.players[player_id].variables)
        for name, variable in game.players[player_id].variables.items():
            if is_match_limit(target_limit, variable.limit):
                del copy_variables[name]
        game.players[player_id].variables = copy_variables
    """


def set_variable(
        game_or_player: Union[Game, Player], name: VariableName, type: Type,
        limit: Limit, value: Any):
    """
    Set variable into game with limit.

    Args:
        game_or_player (Game | Player): now game or player
        name (VariableName): name of added variable.
        type (Type): the type of added variable.
        limit (Limit): the limit of added variable.
        value (Any): the value of added variable.
    """
    if name not in game_or_player.variables:
        game_or_player.variables[name] = Variable(
            limit=limit, type=type
        )
    game_or_player.variables[name].set_value(value)


def get_variable(game: Game, name: VariableName, type: Type):
    """
    Get variable from game with name.

    Args:
        game (Game): now game
        name (VariableName): name of variable.
        type (Type): type of variable.
    """
    if name in game.variables:
        return game.variables[name].value
    if type == list:
        return []
    if type == int:
        return 0
    raise Exception("Unsupported Variable type: %s" % str(type))


def delete_variable(game: Game, name: VariableName, type: Type, value: Any):
    """
    Delete value of variable from game with name and value.

    Args:
        game (Game): now game.
        name (VariableName): name of variable.
        type (Type): type of variable.
        value (Any): value which will be deleted.
    """
    if name not in game.variables:
        return
    if type == list:
        values = get_variable(game, name, type)
        if value in values:
            values.remove(value)
        return
    raise Exception("Unsupported Variable type: %s" % str(type))
