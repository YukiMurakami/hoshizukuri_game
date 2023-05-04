from hoshizukuri_game.models.cost import Cost
import pytest


class TestCost:
    def test_str1(self):
        c = Cost(3)
        assert str(c) == "3"

    def test_str2(self):
        c = Cost(0)
        assert str(c) == "0"

    def test_compare_starflake_lt(self):
        assert Cost(2) < Cost(4)

    def test_compare_starflake_gt(self):
        assert Cost(5) > Cost(4)

    def test_compare_starflake_le(self):
        assert Cost(2) <= Cost(4)
        assert Cost(4) <= Cost(4)

    def test_compare_starflake_ge(self):
        assert Cost(5) >= Cost(4)
        assert Cost(5) >= Cost(5)

    def test_compare_starflake_eq(self):
        assert Cost(4) == Cost(4)

    def test_compare_starflake_not_eq(self):
        assert Cost(4) != Cost(5)

    def test_compare_error1(self):
        a = Cost(3)
        b = 10
        with pytest.raises(NotImplementedError):
            a == b

    def test_compare_error2(self):
        a = Cost(3)
        b = 10
        with pytest.raises(NotImplementedError):
            a > b

    def test_compare_error3(self):
        a = Cost(3)
        b = 10
        with pytest.raises(NotImplementedError):
            a < b

    def test_str2cost1(self):
        c: Cost = Cost.str2cost("2")
        assert c.cost == 2

    def test_str2cost2(self):
        c: Cost = Cost.str2cost("?")
        assert c.cost == 0

    def test_add(self):
        a: Cost = Cost(3)
        b: Cost = Cost(5)
        c = a + b
        assert c.cost == 8

    def test_sub(self):
        a: Cost = Cost(3)
        b: Cost = Cost(5)
        c = b - a
        assert c.cost == 2

    def test_mul(self):
        b: Cost = Cost(5)
        c = b * 2
        assert c.cost == 10
