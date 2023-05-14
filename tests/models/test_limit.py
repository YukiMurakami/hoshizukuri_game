from hoshizukuri_game.models.limit import (
    Limit, LimitOr, LimitTriggerActivate,
    is_match_limit,
    TargetLimit, LimitForever
)
import pytest


class TestTargetLimit():
    def test_1(self):
        TargetLimit(
            limit_class=LimitTriggerActivate, trigger_id="1234abcd")


class TestLimit():
    def test_limit(self):
        limit = Limit()
        assert str(limit) == "limit"

    def test_limit_or(self):
        limit = LimitOr([Limit(), Limit()])
        assert str(limit) == "limit:or:[limit,limit]"

    def test_limit_trigger_activate1(self):
        limit = LimitTriggerActivate("100")
        assert str(limit) == "limit:trigger_activate:100"

    def test_limit_trigger_activate2(self):
        limit = LimitTriggerActivate(None)
        assert str(limit) == "limit:trigger_activate:None"

    def test_limit_forever(self):
        limit = LimitForever()
        assert str(limit) == "limit:forever"


class TestIsMatchLimit():
    def test_match_1(self):
        a = TargetLimit(LimitTriggerActivate, trigger_id="100")
        b = LimitTriggerActivate("100")
        assert is_match_limit(a, b)

    def test_match_2(self):
        a = TargetLimit(LimitTriggerActivate, trigger_id="100")
        b = LimitTriggerActivate("50")
        assert not is_match_limit(a, b)

    def test_match_4(self):
        a = TargetLimit(LimitTriggerActivate, trigger_id="100")
        b = LimitOr([LimitTriggerActivate("10"), LimitTriggerActivate("100")])
        assert is_match_limit(a, b)

    def test_match_5(self):
        a = TargetLimit(LimitTriggerActivate, trigger_id="100")
        b = LimitOr([LimitTriggerActivate("10"), LimitTriggerActivate("20")])
        assert not is_match_limit(a, b)

    def test_match_6(self):
        a = TargetLimit(LimitTriggerActivate, trigger_id="100")
        b = LimitForever()
        assert not is_match_limit(a, b)

    def test_match_error(self):
        a = TargetLimit(int)
        b = 15
        with pytest.raises(Exception):
            is_match_limit(a, b)
