"""
This module defines the Trigger model.

Triggers define the content, timing of calling,
    and lifetime of an interrupt step.
"""
from __future__ import annotations
from typing import TYPE_CHECKING, List, Union
if TYPE_CHECKING:
    from ..models.limit import Limit
    from ..models.game import Game
    from ..models.activate import Activate, TargetActivate
    from ..steps.abstract_step import AbstractStep
from ..models.limit import (
    LimitTriggerActivate, is_match_limit, TargetLimit, LimitOr
)
from ..models.variable import VariableName, get_variable
from ..models.activate import is_match_activate
import uuid


class Trigger:
    """
    Trigger model class.

    Args:
        limit (Limit): the limit of this trigger.
        activate (Activate): the calling timing of this trigger.
        step (AbstractStep): When this trigger is called,
            this will be processed.
        can_pass (bool, Optional): True is that don't have to
            call this trigger. Default is False.
        auto (bool, Optional): True is that this trigger can be processed
            automatically without player choice when some triggers are called.
            Default is False.
        exist_uniq_id (int, Optional): This is card unique ID for trigger.
            This is not for game.triggers.

    Arrtibutes:
        id (int): Trigger unique ID.

    Note:
        - When auto is True, can_pass must be False.
    """
    def __init__(
            self, limit: Limit, activate: Activate,
            step: AbstractStep,
            can_pass: bool = False,
            auto: bool = False,
            exist_uniq_id: int = None):
        if auto:
            assert not can_pass
        self.id = str(uuid.uuid4()).replace("-", "")
        self.limit = limit
        if (isinstance(
                limit, LimitTriggerActivate) and limit.trigger_id is None):
            limit.trigger_id = self.id
        if isinstance(limit, LimitOr):
            for ll in limit.limits:
                if isinstance(
                        ll, LimitTriggerActivate) and ll.trigger_id is None:
                    ll.trigger_id = self.id
        self.activate = activate
        self.step = step
        self.can_pass = can_pass
        self.auto = auto
        self.exist_uniq_id = exist_uniq_id


def get_called_triggers(
        target_activates: List[TargetActivate],
        game: Game,
        source_step: AbstractStep):
    """
    Get all possible triggers.

    Args:
        target_activate (List[TargetActivate]): Activates which call triggers.
        game (Game): now game,
        source_step (AbstractStep): The step which calls this.

    Returns:
        List[Trigger], List[Trigger]: Auto triggers and select triggers.

    Note:
        - The closer to the turn player, the more end.
        - Auto trigger is more end.
    """
    if len(target_activates) <= 0:
        return [], []
    possible_triggers: List[Trigger] = []
    for target_activate in target_activates:
        possible_triggers += _get_called_triggers_with_activate(
            target_activate, game, source_step
        )
    # sort
    sort_triggers: Union[List[List[Trigger]], List[Trigger]] = []
    start_player_id = target_activates[0].player_id
    if start_player_id is None:
        start_player_id = game.turn.player_id
    for i in range(len(game.players)):
        triggers = []
        auto_triggers = []
        player_id = start_player_id + i
        if player_id >= len(game.players):
            player_id -= len(game.players)
        for trigger in possible_triggers:
            if trigger.step.player_id == player_id:
                if trigger.auto:
                    auto_triggers.append(trigger)
                else:
                    triggers.append(trigger)
        sort_triggers = auto_triggers + sort_triggers
        if len(triggers) >= 1:
            sort_triggers.insert(0, triggers)
    auto_triggers = []
    select_triggers = []
    for trigger in reversed(sort_triggers):
        if isinstance(trigger, list):
            select_triggers = trigger
            break
        else:
            auto_triggers = [trigger] + auto_triggers
    return auto_triggers, select_triggers


def _get_called_triggers_with_activate(
        target_activate: TargetActivate, game: Game,
        source_step: AbstractStep):
    possible_triggers = []
    if hasattr(game, "triggers"):
        for trigger in game.triggers:
            if is_match_activate(target_activate, trigger.activate, game):
                if trigger.step.can_play_trigger(game, target_activate):
                    value = "%s-%s" % (
                        source_step.step_id, trigger.step.step_id)
                    if value not in get_variable(
                            game, VariableName.DONE_TRIGGER_LIST, list):
                        trigger.step.trigger_activate = target_activate
                        trigger.step.depth = source_step.depth
                        possible_triggers.append(trigger)
    return possible_triggers


def remove_triggers(game: Game, target_limit: TargetLimit):
    """
    Remove triggers from game with target limit.

    Args:
        game (Game): now game
        target_limit (TargetLimit): target limit.
    """
    copy_triggers = list(game.triggers)
    for trigger in game.triggers:
        if is_match_limit(target_limit, trigger.limit):
            copy_triggers.remove(trigger)
    game.triggers = copy_triggers
