from hoshizukuri_game.models.trigger import Trigger
from hoshizukuri_game.steps.abstract_step import AbstractStep
from hoshizukuri_game.steps.common.call_trigger_step import (
    CallTriggerStep, _TriggerSelectStep,
    _process_triggers
)
from hoshizukuri_game.models.activate import (
    TargetActivate,
    ActivatePlaysetEnd
)
from hoshizukuri_game.models.game import Game
from hoshizukuri_game.models.player import Player
from hoshizukuri_game.models.limit import (
    LimitForever,
    LimitTriggerActivate,
)
from hoshizukuri_game.steps.base.daichi_step import _DaichiTriggerStep
from hoshizukuri_game.utils.card_util import get_card_id
from hoshizukuri_game.models.log import InvalidLogException
import pytest


class TestCallTriggerStep:
    def test_str(self):
        step = CallTriggerStep(0, 0, [TargetActivate(
            ActivatePlaysetEnd, player_id=0)])
        assert str(step) == (
            "0:calltrigger:0:[target_activate:"
            "ActivatePlaysetEnd:player_id=0]"
        )

    def test_process_1(self, get_step_classes):
        game = Game()
        game.set_players([Player(0)])
        source_step = AbstractStep()
        source_step.player_id = 0
        trigger_1 = Trigger(
            LimitTriggerActivate(None),
            ActivatePlaysetEnd(0),
            source_step, can_pass=False, auto=True)
        game.triggers = [trigger_1]
        step = CallTriggerStep(0, 0, [TargetActivate(
            ActivatePlaysetEnd, player_id=0)])
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [
            CallTriggerStep, AbstractStep
        ]
        assert next_steps[1].step_id == source_step.step_id
        assert len(game.triggers) == 0

    def test_process_2(self, get_step_classes):
        game = Game()
        game.set_players([Player(0)])
        source_step = AbstractStep()
        source_step.player_id = 0
        trigger_1 = Trigger(
            LimitTriggerActivate(None),
            ActivatePlaysetEnd(0),
            source_step, can_pass=False, auto=False)
        game.triggers = [trigger_1]
        step = CallTriggerStep(0, 0, [TargetActivate(
            ActivatePlaysetEnd, player_id=0)])
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [
            CallTriggerStep, _TriggerSelectStep]

    def test_process_3(self, get_step_classes):
        game = Game()
        game.set_players([Player(0)])
        game.triggers = []
        step = CallTriggerStep(0, 0, [TargetActivate(
            ActivatePlaysetEnd, player_id=0)])
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == []

    def test_process_4(self, get_step_classes, mocker):
        source_step = AbstractStep()
        source_step.player_id = 0
        mocker.patch(
            "hoshizukuri_game.steps.abstract_step."
            "AbstractStep.can_play_trigger", return_value=False)
        game = Game()
        game.set_players([Player(0)])
        game.triggers = [
            Trigger(
                LimitTriggerActivate(None),
                ActivatePlaysetEnd(0),
                source_step
            )
        ]
        step = CallTriggerStep(0, 0, [
            TargetActivate(ActivatePlaysetEnd, 0)
        ])
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == []
        assert len(game.triggers) == 0


class TestProcessTriggers:
    def test_1(self):
        game = Game()
        step = AbstractStep()
        source_step = AbstractStep()
        trigger = Trigger(
            LimitTriggerActivate(None),
            ActivatePlaysetEnd(0),
            step
        )
        game.triggers = [trigger]
        _process_triggers(game, trigger, source_step)
        assert len(game.triggers) == 0


class TestTriggerSelectStep:
    def test_str(self):
        source_step = AbstractStep()
        trigger_step = AbstractStep()
        trigger = Trigger(
            LimitForever(),
            ActivatePlaysetEnd(0), trigger_step)
        trigger.step.trigger_activate = TargetActivate(
            ActivatePlaysetEnd, 0)
        step = _TriggerSelectStep(0, 0, [trigger], source_step)
        assert str(step) == (
            "0:triggerselect:0:target_activate:"
            "ActivatePlaysetEnd:player_id=0")

    def get_triggers(self, can_pass=True):
        step_1 = _DaichiTriggerStep(0, 0, 0)
        step_1.trigger_activate = TargetActivate(ActivatePlaysetEnd, 0)
        step_2 = _DaichiTriggerStep(0, 0, 1)
        step_2.trigger_activate = TargetActivate(ActivatePlaysetEnd, 0)
        triggers = [
            Trigger(
                LimitForever(),
                ActivatePlaysetEnd(0),
                step_1, can_pass=can_pass
            ),
            Trigger(
                LimitForever(),
                ActivatePlaysetEnd(0),
                step_2, can_pass=can_pass
            )
        ]
        return triggers

    def test_process_1(self, get_step_classes):
        triggers = self.get_triggers()
        source_step = AbstractStep()
        step = _TriggerSelectStep(0, 0, triggers, source_step)
        game = Game()
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [_TriggerSelectStep]
        assert next_steps[0].get_candidates(game) == [
            "0:triggerselect:daichi:%d-0#0" % get_card_id("daichi"),
            "0:triggerselect:daichi:%d-1#0" % get_card_id("daichi"),
            "0:triggerselect:pass#0"
        ]

    def test_process_2(self, get_step_classes):
        triggers = self.get_triggers()
        source_step = AbstractStep()
        step = _TriggerSelectStep(0, 0, triggers, source_step)
        game = Game()
        game.choice = "0:triggerselect:daichi:%d-1" % get_card_id("daichi")
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [_DaichiTriggerStep]
        assert next_steps[0].get_candidates(game) == []

    def test_process_3(self, get_step_classes):
        triggers = self.get_triggers()
        source_step = AbstractStep()
        step = _TriggerSelectStep(0, 0, triggers, source_step)
        game = Game()
        game.choice = "0:triggerselect:pass"
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == []
        assert game.triggers == []

    def test_process_4(self, get_step_classes):
        step_1 = _DaichiTriggerStep(0, 0, 0)
        step_1.trigger_activate = TargetActivate(ActivatePlaysetEnd, 0)
        triggers = [
            Trigger(
                LimitForever(),
                ActivatePlaysetEnd(0),
                step_1, can_pass=False
            )
        ]
        source_step = AbstractStep()
        step = _TriggerSelectStep(0, 0, triggers, source_step)
        game = Game()
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [_DaichiTriggerStep]
        assert next_steps[0].get_candidates(game) == []

    def test_process_log_1(self, get_step_classes, make_log_manager):
        triggers = self.get_triggers()
        source_step = AbstractStep()
        step = _TriggerSelectStep(0, 0, triggers, source_step)
        game = Game()
        game.log_manager = make_log_manager(
            "A trashes 大地 from their playarea."
        )
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [_DaichiTriggerStep]
        assert next_steps[0].get_candidates(game) == []

    def test_process_log_2(self, get_step_classes, make_log_manager):
        triggers = self.get_triggers()
        source_step = AbstractStep()
        step = _TriggerSelectStep(0, 0, triggers, source_step)
        game = Game()
        game.log_manager = make_log_manager("")
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [_TriggerSelectStep]
        assert next_steps[0].get_candidates(game) == [
            "0:triggerselect:daichi:%d-0#0" % get_card_id("daichi"),
            "0:triggerselect:daichi:%d-1#0" % get_card_id("daichi"),
            "0:triggerselect:pass#0"
        ]

    def test_process_log_3(self, get_step_classes, make_log_manager):
        triggers = self.get_triggers()
        source_step = AbstractStep()
        step = _TriggerSelectStep(0, 0, triggers, source_step)
        game = Game()
        game.log_manager = make_log_manager(
            "A draws 星屑."
        )
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == []

    def test_process_log_4(self, get_step_classes, make_log_manager):
        triggers = self.get_triggers()
        triggers[0].can_pass = False
        triggers[1].can_pass = False
        source_step = AbstractStep()
        step = _TriggerSelectStep(0, 0, triggers, source_step)
        game = Game()
        game.log_manager = make_log_manager(
            "A draws 星屑."
        )
        with pytest.raises(InvalidLogException):
            step.process(game)
