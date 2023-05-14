from hoshizukuri_game.models.activate import (
    Activate,
    ActivatePlaysetEnd,
    TargetActivate,
    is_match_activate
)
from hoshizukuri_game.models.game import Game
import pytest


class TestActivate:
    def test_activate_str(self):
        act = Activate()
        assert str(act) == "act"

    def test_activate_playset_end_str(self):
        act = ActivatePlaysetEnd(player_id=0)
        assert str(act) == "act:playsetend:0"


class TestTargetActivate:
    def test_target_activate(self):
        TargetActivate(
            ActivatePlaysetEnd, player_id=0, card_id=2
        )

    def test_str(self):
        target_activate = TargetActivate(
            ActivatePlaysetEnd, player_id=0, card_id=2, uniq_id=3, uniq_turn=1
        )
        assert str(target_activate) == (
            "target_activate:ActivatePlaysetEnd:"
            "player_id=0,card_id=2,uniq_id=3,uniq_turn=1"
        )


class TestIsMatchActivate:
    def test_match_1(self):
        game = Game()
        target_activate = TargetActivate(ActivatePlaysetEnd, player_id=0)
        activate = ActivatePlaysetEnd(0)
        assert is_match_activate(target_activate, activate, game)

    def test_match_2(self):
        game = Game()
        target_activate = TargetActivate(ActivatePlaysetEnd, player_id=1)
        activate = ActivatePlaysetEnd(0)
        assert not is_match_activate(target_activate, activate, game)

    def test_match_3(self):
        game = Game()
        target_activate = TargetActivate(ActivatePlaysetEnd)
        activate = ActivatePlaysetEnd(player_id=1)
        assert not is_match_activate(target_activate, activate, game)

    def test_match_4(self):
        game = Game()
        target_activate = TargetActivate(ActivatePlaysetEnd, player_id=1)
        activate = Activate()
        assert not is_match_activate(target_activate, activate, game)

    def test_match_error(self):
        with pytest.raises(Exception):
            game = Game()
            target_activate = TargetActivate(Activate)
            activate = Activate()
            is_match_activate(target_activate, activate, game)
