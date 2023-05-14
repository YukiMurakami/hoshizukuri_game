from hoshizukuri_game.models.game import Game
from hoshizukuri_game.models.player import Player
from hoshizukuri_game.models.trigger import (
    Trigger,
    _get_called_triggers_with_activate,
    get_called_triggers,
    remove_triggers,
)
from hoshizukuri_game.models.limit import (
    LimitOr,
    LimitTriggerActivate,
    TargetLimit,
)
from hoshizukuri_game.models.activate import (
    TargetActivate, ActivatePlaysetEnd
)
from hoshizukuri_game.steps.abstract_step import AbstractStep
import pytest


class TestTrigger:
    def test_trigger_1(self):
        step = AbstractStep()
        trigger = Trigger(
            limit=LimitTriggerActivate(trigger_id=None),
            activate=ActivatePlaysetEnd(
                player_id=0),
            step=step,
            can_pass=False
        )
        assert trigger.limit.trigger_id == trigger.id

    def test_trigger_2(self):
        step = AbstractStep()
        trigger = Trigger(
            limit=LimitOr([LimitTriggerActivate(trigger_id=None)]),
            activate=ActivatePlaysetEnd(
                player_id=0),
            step=step,
            can_pass=False
        )
        assert trigger.limit.limits[0].trigger_id == trigger.id

    def test_error(self):
        with pytest.raises(Exception):
            step = AbstractStep()
            Trigger(
                limit=LimitTriggerActivate(trigger_id=None),
                activate=ActivatePlaysetEnd(
                    player_id=0),
                step=step,
                can_pass=True, auto=True
            )


class TestGetCalledTriggersWithActivate:
    def test_get_triggers_1(self):
        target_activate = TargetActivate(
            ActivatePlaysetEnd, player_id=0
        )
        game = Game()
        source_step = AbstractStep()
        trigger_1 = Trigger(
            LimitTriggerActivate(None),
            ActivatePlaysetEnd(0),
            step=source_step, can_pass=False, auto=False
        )
        trigger_2 = Trigger(
            LimitTriggerActivate(None),
            ActivatePlaysetEnd(1),
            step=source_step, can_pass=False, auto=False
        )
        game.triggers = [trigger_1, trigger_2]
        triggers = _get_called_triggers_with_activate(
            target_activate, game, source_step
        )
        assert len(triggers) == 1 and triggers[0].id == trigger_1.id


def get_game_and_step():
    game = Game()
    game.turn.player_id = 0
    game.set_players([Player(0), Player(1), Player(2)])
    source_step = AbstractStep()
    source_step.player_id = 0
    trigger_1 = Trigger(
        LimitTriggerActivate(None),
        ActivatePlaysetEnd(None),
        step=source_step, can_pass=False, auto=False
    )
    trigger_2 = Trigger(
        LimitTriggerActivate(None),
        ActivatePlaysetEnd(None),
        step=source_step, can_pass=False, auto=True
    )
    trigger_3 = Trigger(
        LimitTriggerActivate(None),
        ActivatePlaysetEnd(None),
        step=source_step, can_pass=False, auto=True
    )
    game.triggers = [trigger_1, trigger_2, trigger_3]
    return game, source_step


class TestGetCalledTriggers:
    def test_get_triggers_1(self):
        target_activate_1 = TargetActivate(
            ActivatePlaysetEnd, player_id=0
        )
        game, source_step = get_game_and_step()
        auto_triggers, select_triggers = get_called_triggers(
            [target_activate_1], game, source_step
        )
        assert len(auto_triggers) == 2 and len(select_triggers) == 1
        assert auto_triggers[0].id == game.triggers[1].id

    def test_get_triggers_2(self):
        game, source_step = get_game_and_step()
        auto_triggers, select_triggers = get_called_triggers(
            [], game, source_step
        )
        assert len(auto_triggers) == 0 and len(select_triggers) == 0

    def test_get_triggers_3(self):
        target_activate_1 = TargetActivate(
            ActivatePlaysetEnd
        )
        game, source_step = get_game_and_step()
        game.turn.player_id = 1
        auto_triggers, select_triggers = get_called_triggers(
            [target_activate_1], game, source_step
        )
        assert len(auto_triggers) == 2 and len(select_triggers) == 1
        assert auto_triggers[0].id == game.triggers[1].id


class TestRemoveTriggers:
    def test_remove_triggers(self):
        game = Game()
        step = AbstractStep()
        trigger_1 = Trigger(
            LimitTriggerActivate(None),
            ActivatePlaysetEnd(0),
            step
        )
        trigger_2 = Trigger(
            LimitTriggerActivate(None),
            ActivatePlaysetEnd(0),
            step
        )
        game.triggers = [trigger_1, trigger_2]
        target_limit = TargetLimit(
            limit_class=LimitTriggerActivate, trigger_id=trigger_1.id
        )
        remove_triggers(game, target_limit)
        assert len(game.triggers) == 1
        assert game.triggers[0].id == trigger_2.id
