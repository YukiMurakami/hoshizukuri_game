from hoshizukuri_game.models.limit import (
    LimitForever, LimitTriggerActivate,
    TargetLimit
)
from hoshizukuri_game.models.variable import (
    Variable, VariableName,
    get_variable, set_variable, remove_variables,
    delete_variable,
)
import pytest
from hoshizukuri_game.models.game import Game


class TestVariable:
    def test_1(self):
        variable = Variable(LimitForever(), list)
        assert variable.value == []

    def test_2(self):
        variable = Variable(LimitForever(), int)
        assert variable.value == 0

    def test_error(self):
        with pytest.raises(Exception):
            Variable(LimitForever(), float)

    def test_set_value_1(self):
        variable = Variable(LimitForever(), list)
        variable.set_value(15)
        variable.set_value(2)
        assert variable.value == [15, 2]

    def test_set_value_2(self):
        variable = Variable(LimitForever(), int)
        variable.set_value(15)
        variable.set_value(2)
        assert variable.value == 2


class TestRemoveVariables:
    def test_1(self):
        game = Game()
        game.variables[VariableName.DONE_TRIGGER_LIST] = Variable(
            LimitTriggerActivate("1234"), list
        )
        game.variables[VariableName.DONE_TRIGGER_LIST].value = ["1-5", "2-6"]
        remove_variables(game, TargetLimit(
            LimitTriggerActivate, trigger_id="1234"))
        assert VariableName.DONE_TRIGGER_LIST not in game.variables


class TestSetVariables:
    def test_1(self):
        game = Game()
        set_variable(
            game, VariableName.DONE_TRIGGER_LIST, list, LimitForever(), "1-5")
        set_variable(
            game, VariableName.DONE_TRIGGER_LIST, list, LimitForever(), "3-8")
        assert game.variables[
            VariableName.DONE_TRIGGER_LIST].value == ["1-5", "3-8"]


class TestGetVariables:
    def test_1(self):
        game = Game()
        game.variables[VariableName.DONE_TRIGGER_LIST] = Variable(
            LimitForever(), list
        )
        game.variables[VariableName.DONE_TRIGGER_LIST].value = ["1-5", "2-6"]
        assert get_variable(
            game, VariableName.DONE_TRIGGER_LIST, list) == ["1-5", "2-6"]

    def test_2(self):
        game = Game()
        assert get_variable(
            game, VariableName.DONE_TRIGGER_LIST, list) == []

    def test_3(self):
        game = Game()
        assert get_variable(
            game, VariableName.DONE_TRIGGER_LIST, int) == 0

    def test_error(self):
        game = Game()
        with pytest.raises(Exception):
            get_variable(
                game, VariableName.DONE_TRIGGER_LIST, float)


class TestDeleteVariable:
    def test_1(self):
        game = Game()
        variable = Variable(None, list)
        variable.value = ["1-5", "2-6"]
        game.variables[VariableName.DONE_TRIGGER_LIST] = variable
        delete_variable(game, VariableName.DONE_TRIGGER_LIST, list, "1-5")
        assert get_variable(
            game, VariableName.DONE_TRIGGER_LIST, list) == ["2-6"]

    def test_2(self):
        game = Game()
        delete_variable(game, VariableName.DONE_TRIGGER_LIST, list, "1-5")
        assert get_variable(
            game, VariableName.DONE_TRIGGER_LIST, list) == []

    def test_3(self):
        game = Game()
        variable = Variable(None, list)
        variable.value = ["1-5", "2-6"]
        game.variables[VariableName.DONE_TRIGGER_LIST] = variable
        with pytest.raises(Exception):
            delete_variable(game, VariableName.DONE_TRIGGER_LIST, int, "1-5")
