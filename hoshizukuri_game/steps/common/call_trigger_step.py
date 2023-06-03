"""
Steps for call triggers.
"""
from __future__ import annotations
from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from ...models.game import Game
from ..abstract_step import AbstractStep
from ...models.activate import (
    TargetActivate,
    is_match_activate
)
from ...models.limit import (
    TargetLimit,
    LimitTriggerActivate, LimitForever,
)
from ...models.trigger import (
    get_called_triggers,
    Trigger, remove_triggers
)
from ...models.variable import (
    set_variable, VariableName
)
from ...models.log import InvalidLogException
from ...utils.choice_util import cparses


class CallTriggerStep(AbstractStep):
    """
    call triggers with target activates.

    Args:
        player_id (int): player who has added buy.
        depth (int): Expected log hierarchy.
        target_activates (List[TargetActivate]): Target Activates
            to call triggers.
    """
    def __init__(
            self, player_id: int, depth: int,
            target_activates: List[TargetActivate]):
        super().__init__()
        self.player_id = player_id
        self.depth = depth
        self.target_activates = target_activates

    def __str__(self):
        return "%d:calltrigger:%d:[%s]" % (
            self.depth, self.player_id,
            ",".join([str(n) for n in self.target_activates]))

    def process(self, game: Game):
        auto_triggers, select_triggers = get_called_triggers(
            self.target_activates, game, self
        )
        if len(auto_triggers) > 0:
            # process automatically
            for auto_trigger in auto_triggers:
                _process_triggers(game, auto_trigger, self)
            return [self] + [t.step for t in auto_triggers]
        if len(select_triggers) <= 0:
            # all trigger checks done
            # cancel triggers which were not played
            #   and has only LimitTriggerActivate.
            cancel_triggers = []
            if hasattr(game, "triggers"):
                for trigger in game.triggers:
                    for t_activate in self.target_activates:
                        if is_match_activate(
                                t_activate, trigger.activate, game):
                            if not trigger.step.can_play_trigger(
                                    game, t_activate):
                                if isinstance(
                                        trigger.limit, LimitTriggerActivate):
                                    # cancel
                                    cancel_triggers.append(trigger)
            for trigger in cancel_triggers:
                game.triggers.remove(trigger)
            return []
        return [self, _TriggerSelectStep(
            self.player_id, self.depth, select_triggers, self
        )]  # call trigger select step


def _process_triggers(game: Game, trigger: Trigger, source_step: AbstractStep):
    target_limit = TargetLimit(
        LimitTriggerActivate, trigger_id=trigger.id
    )
    value = "%s-%s" % (source_step.step_id, trigger.step.step_id)
    set_variable(
        game, VariableName.DONE_TRIGGER_LIST, list, LimitForever(), value)
    remove_triggers(game, target_limit)


class _TriggerSelectStep(AbstractStep):
    def __init__(
            self, player_id: int, depth: int, triggers: List[Trigger],
            source_step: AbstractStep):
        super().__init__()
        self.player_id = player_id
        self.depth = depth
        self.triggers = triggers
        self.source_step = source_step

    def __str__(self):
        activate_str = ",".join(
            [str(n.step.trigger_activate) for n in self.triggers]
        )
        return "%d:triggerselect:%d:%s" % (
            self.depth, self.player_id, activate_str
        )

    def process(self, game: Game):
        if game.choice == "":
            self.candidates = []
            cannot_pass_count = 0
            all_can_pass = True
            for trigger in self.triggers:
                self.candidates.append(
                    "%d:triggerselect:%s" % (
                        self.player_id, trigger.step.get_trigger_name())
                )
                if not trigger.can_pass:
                    all_can_pass = False
                    cannot_pass_count += 1
            if all_can_pass:
                self.candidates.append(
                    "%d:triggerselect:pass" % self.player_id
                )
            if cannot_pass_count == 1 and len(self.candidates) == 1:
                # auto select trigger
                game.choice = self.candidates[0]
            elif game.log_manager is not None:
                game.choice = self._log2choice(game, all_can_pass)
        if game.choice == "":
            return [self]
        else:
            self.candidates = []
        player_id, command, trigger_name = cparses(game.choice)
        game.choice = ""
        assert player_id == self.player_id
        assert command == "triggerselect"
        if trigger_name == "pass":
            for trigger in self.triggers:
                _process_triggers(game, trigger, self.source_step)
            return []
        index = [n.step.get_trigger_name() for n in self.triggers].index(
            trigger_name)
        assert index is not None
        _process_triggers(game, self.triggers[index], self.source_step)
        return [self.triggers[index].step]

    def _log2choice(self, game: Game, can_pass: bool):
        if not game.log_manager.has_logs():
            return game.choice
        for trigger in self.triggers:
            log_condition = trigger.step.get_trigger_log_condition(game)
            log = game.log_manager.get_nextlog(log_condition)
            if log is not None:
                return "%d:triggerselect:%s" % (
                    self.player_id, trigger.step.get_trigger_name()
                )
        if can_pass is False:
            raise InvalidLogException(game)
        return "%d:triggerselect:pass" % self.player_id
