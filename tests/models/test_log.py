from hoshizukuri_game.models.log import (
    Command, LogConditionOr, LogFormatter, LogManager, Log, LogCondition,
    InvalidLogException
)
from hoshizukuri_game.models.game import Game
import pytest
import re


class TestInvalidLogException:
    def test_str(self):
        game = Game()
        game.log_manager = LogManager()
        game.log_manager._logs.append(
            Log(["Alice"], Command.TURN_START, 0, "log_line")
        )
        game.log_manager._logs[0].line_n = 0
        log_condition = LogCondition(Command.TURN_START, player_id=0, depth=0)
        e = InvalidLogException(game, log_condition)
        assert str(e) == "Invalid Log Exception - line 1: %s (%s)" % (
            game.log_manager._logs[0].line, str(log_condition)
        )


class TestLogCondition():
    def test_str1(self):
        log_condition = LogCondition(
            Command.TRASH_FROM_HAND, 0, 1, numbers=None, card_ids=[4]
        )
        assert str(log_condition) == (
            "command=trash_from_hand,player_id=0"
            ",depth=1,card_ids=[4]")

    def test_str2(self):
        log_condition = LogCondition(
            Command.DRAW, 0, 2, numbers=[1]
        )
        assert str(log_condition) == (
            "command=draw,player_id=0"
            ",depth=2,numbers=[1]")

    def test_str3(self):
        log_condition = LogConditionOr(
            [
                LogCondition(
                    Command.DRAW, 0, 1, numbers=[1]
                ),
                LogCondition(
                    Command.SHUFFLE, 0, 1
                )
            ]
        )
        assert str(log_condition) == (
            "command=draw,player_id=0,depth=1,numbers=[1]|"
            "command=shuffle,player_id=0,depth=1"
        )


class TestLog():
    def test_str_1(self):
        log = Log(["A", "B"], Command.CHANGE_ORBIT, 2, "")
        log.set_key("PLAYER", "B")
        log.set_key("NUMBER", "1")
        log.set_key("NUMBER2", "3")
        assert str(log) == "2:CHANGE_ORBIT,player_id=1,numbers=[1,3]"

    def test_str_2(self):
        log = Log(["A", "B"], Command.GAIN_INTO_HAND, 1, "")
        log.set_key("PLAYER", "A")
        log.set_key("CARD", "星屑")
        assert str(log) == "1:GAIN_INTO_HAND,player_id=0,card_id=1"

    def test_str_3(self):
        log = Log(["A", "B"], Command.DRAW, 1, "")
        log.set_key("PLAYER", "A")
        log.set_key("CARDS", "星屑, 衛星")
        assert str(log) == "1:DRAW,player_id=0,card_ids=[1,3]"

    def test_set_key_1(self):
        log = Log(["A", "B"], Command.GAIN_INTO_HAND, 1, "")
        assert log.set_key("PLAYER", "C") is False

    def test_set_key_2(self):
        log = Log(["A", "B"], Command.GAIN_INTO_HAND, 1, "")
        assert log.set_key("PLAYER", "A")
        assert log.player_id == 0

    def test_set_key_3(self):
        log = Log(["A", "B"], Command.CHANGE_ORBIT, 1, "")
        assert log.set_key("NUMBER", "abc") is False
        assert log.set_key("NUMBER2", "15")
        assert log.numbers == [None, 15]

    def test_set_key_4(self):
        log = Log(["A", "B"], Command.CHANGE_ORBIT, 1, "")
        assert log.set_key("NUMBER", "13")
        assert log.set_key("NUMBER2", "abc") is False
        assert log.numbers == [13, None]

    def test_set_key_5(self):
        log = Log(["A", "B"], Command.CHANGE_ORBIT, 1, "")
        assert log.set_key("NUMBER", "1")
        assert log.numbers == [1, None]

    def test_set_key_6(self):
        log = Log(["A", "B"], Command.CHANGE_ORBIT, 1, "")
        assert log.set_key("NUMBER2", "1")
        assert log.numbers == [None, 1]

    def test_set_key_7(self):
        log = Log(["A", "B"], Command.GAIN_INTO_DISCARD, 1, "")
        assert log.set_key(
            "CARD", "星屑, 岩石") is False

    def test_set_key_invalid_card(self):
        log = Log(["A", "B"], Command.GAIN_INTO_DISCARD, 1, "")
        assert log.set_key(
            "CARD", "a invalid card") is False

    def test_set_key_invalid_cards(self):
        log = Log(["A", "B"], Command.DISCARD_FROM_HAND, 1, "")
        assert log.set_key(
            "CARDS", "a invalid card") is False

    def test_set_key_invalid_key(self):
        log = Log(["A", "B"], Command.GAIN_INTO_DISCARD, 1, "")
        with pytest.raises(Exception):
            log.set_key(
                "INVALID_KEY", "aaaa") is False


class TestLogFormatter():
    def test_set_names(self):
        log_formatter = LogFormatter()
        log_formatter.set_names(["A", "B"])
        assert log_formatter._names == ["A", "B"]

    def test_get_re_pattern(self):
        log_formatter = LogFormatter()
        result = log_formatter._get_re_pattern(
            "<PLAYER> gains <CARD> into their hand.")
        assert result["command"] == Command.GAIN_INTO_HAND
        assert result["re_pattern"] == "(.*?) gains (.*?) into their hand\\.$"
        assert result["key_list"] == ["PLAYER", "CARD"]

    def test_get_indent_line(self):
        log_formatter = LogFormatter()
        indent, line = log_formatter._get_indent_and_line(
            "@@H gains 衛星 into their hand.")
        assert indent == 2
        assert line == "H gains 衛星 into their hand."

    def test_make_log(self):
        log_formatter = LogFormatter()
        log_formatter.set_names(["A", "B"])
        logs, lines = log_formatter._make_log([
            "A gains 衛星 into their hand.",
            "A gains 岩石 into their hand."
        ])
        assert len(logs) == 1
        assert str(logs[0]) == "0:GAIN_INTO_HAND,player_id=0,card_id=3"
        assert len(lines) == 1
        assert lines[0] == "A gains 岩石 into their hand."

    def test_make_log_2(self):
        log_formatter = LogFormatter()
        log_formatter.set_names(["A", "B"])
        logs, lines = log_formatter._make_log([
            "",
            ""
        ])
        assert len(logs) == 0
        assert len(lines) == 1
        assert lines[0] == ""

    def test_make_log_invalid(self):
        log_formatter = LogFormatter()
        log_formatter.set_names(["A", "B"])
        with pytest.raises(Exception):
            log_formatter._make_log([
                "Invalid gains a invalid card into their hand."
            ])

    def test_parse_log(self):
        log_formatter = LogFormatter()
        log_formatter.set_names(["A", "B"])
        line = "B gains 岩石 into their hand."
        pred = log_formatter._get_re_pattern(
            "<PLAYER> gains <CARD> into their hand.")
        m = re.match(pred["re_pattern"], line)
        log = log_formatter._parse_log(m, pred, 0, line)
        assert log.player_id == 1
        assert log.command == Command.GAIN_INTO_HAND
        assert log.card_id == 2

    def test_parse_log_invalid(self):
        log_formatter = LogFormatter()
        log_formatter.set_names(["A", "B"])
        line = "B gains invalid card into their hand."
        pred = log_formatter._get_re_pattern(
            "<PLAYER> gains <CARD> into their hand.")
        m = re.match(pred["re_pattern"], line)
        log = log_formatter._parse_log(m, pred, 0, line)
        assert log is None

    def test_format(self):
        log_formatter = LogFormatter()
        log_formatter.set_names(["A", "B"])
        logs = log_formatter.format([
            "Hoge Hoge",
            "A starts with 5 星屑.",
            "A shuffles their deck.",
            "A draws 星屑, 星屑, 星屑, 星屑.",
            "Game over.",
            "hoge hoge."
        ])
        assert len(logs) == 3
        assert str(logs[0]) == "0:START_WITH,player_id=0,card_ids=[1,1,1,1,1]"


class TestLogManager():
    def get_lines(self):
        lines = open("tests/test_log/test_1.txt").readlines()
        return [n.strip() for n in lines if n.strip() != ""]

    def test__get_names(self):
        lines = self.get_lines()
        log_manager = LogManager()
        names = log_manager._get_names(lines)
        assert names == ["エンケ", "ハレー"]

    def test__get_supply(self):
        lines = self.get_lines()
        log_manager = LogManager()
        supply_ids = log_manager._get_supply(lines)
        assert supply_ids == [
            3, 4, 5, 6, 12, 13, 15, 17, 18, 19, 25]

    def test_get_names(self):
        log_manager = LogManager()
        log_manager.read_log("tests/test_log/test_1.txt")
        names = log_manager.get_names()
        assert names == ["エンケ", "ハレー"]

    def test_get_supplies(self):
        log_manager = LogManager()
        log_manager.read_log("tests/test_log/test_1.txt")
        supply_ids = log_manager.get_supplies()
        assert supply_ids == [
            3, 4, 5, 6, 12, 13, 15, 17, 18, 19, 25]

    def test_read_log(self):
        log_manager = LogManager()
        log_manager.read_log("tests/test_log/test_1.txt")
        assert log_manager._logs[0].player_id == 0
        assert log_manager._logs[0].command == Command.START_WITH

    def test_pop(self):
        log_manager = LogManager()
        log_manager.read_log("tests/test_log/test_1.txt")
        log = log_manager.pop()
        assert log.command == Command.START_WITH
        assert log.player_id == 0

    def test_pop_no_log(self):
        log_manager = LogManager()
        log = log_manager.pop()
        assert log is None

    def test_check_next_log1(self):
        log_manager = LogManager()
        log_manager.read_log("tests/test_log/test_1.txt")
        assert log_manager.check_nextlog(
            LogCondition(Command.START_WITH, player_id=0, depth=0))

    def test_check_next_log2(self):
        log_manager = LogManager()
        log = Log(["A", "B"], Command.TURN_START, 1, "")
        log.set_key("PLAYER", "A")
        log_manager._logs = [log]
        assert log_manager.check_nextlog(
            LogCondition(Command.TURN_START, player_id=0, depth=1))
        assert log_manager.check_nextlog(
            LogCondition(
                Command.TURN_START, player_id=1, depth=1)) is False

    def test_check_next_log3(self, make_log_manager):
        log_manager = make_log_manager(
            "A draws 星屑, 岩石."
        )
        assert log_manager.check_nextlog(
            LogCondition(Command.DRAW, player_id=0, depth=0, card_ids=[1, 2]))
        assert log_manager.check_nextlog(
            LogCondition(
                Command.DRAW, player_id=0, depth=0, card_ids=[1])) is False
        assert log_manager.check_nextlog(
            LogCondition(
                Command.DRAW, player_id=0,
                depth=0, card_ids=[1, 2, 3])) is False

    def test_check_next_log4(self, make_log_manager):
        log_manager = make_log_manager(
            "A plays 星屑."
        )
        assert log_manager.check_nextlog(
            LogCondition(Command.PLAY, player_id=0, depth=0, card_ids=[1]))
        assert not log_manager.check_nextlog(
            LogCondition(Command.PLAY, player_id=1, depth=0, card_ids=[1]))
        assert log_manager.check_nextlog(
            LogCondition(
                Command.PLAY, player_id=0, depth=0, card_ids=[2])) is False

    def test_check_next_log5(self, make_log_manager):
        log_manager = make_log_manager(
            "@A plays 星屑."
        )
        assert log_manager.check_nextlog(
            LogCondition(Command.PLAY, player_id=0, depth=1, card_ids=[1]))
        assert log_manager.check_nextlog(
            LogCondition(
                Command.PLAY, player_id=0, depth=0, card_ids=[1])) is False

    def test_check_next_log6(self, make_log_manager):
        log_manager = make_log_manager(
            "@A gains 星屑 into their hand."
        )
        assert log_manager.check_nextlog(
            LogCondition(
                Command.GAIN_INTO_HAND, player_id=0, depth=1, card_ids=[1]))
        assert not log_manager.check_nextlog(
            LogCondition(
                Command.GAIN_INTO_HAND,
                player_id=0, depth=1, card_ids=[2]))

    def test_check_next_log11(self, make_log_manager):
        log_manager = make_log_manager(
            "@A shuffles their deck."
        )
        assert log_manager.check_nextlog(
            LogConditionOr(
                [
                    LogCondition(Command.SHUFFLE, 0, 1),
                    LogCondition(Command.DRAW, 0, 1)
                ]
            ))

    def test_check_next_log12(self, make_log_manager):
        log_manager = make_log_manager(
            "@A gains 星屑 into their hand."
        )
        assert not log_manager.check_nextlog(
            LogConditionOr(
                [
                    LogCondition(Command.SHUFFLE, 0, 1),
                    LogCondition(Command.DRAW, 0, 1)
                ]
            ))

    def test_check_next_log13(self, make_log_manager):
        log_manager = make_log_manager(
            "@A gains 星屑 into their hand."
        )
        with pytest.raises(Exception):
            log_manager.check_nextlog(None)

    def test_check_next_log14(self, make_log_manager):
        log_manager = make_log_manager(
            "@A changes the number of orbits from 0 to 3."
        )
        assert not log_manager.check_nextlog(LogCondition(
            Command.CHANGE_ORBIT, player_id=0, depth=1,
            numbers=[1, 4]
        ))

    def test_check_next_log_no_log(self):
        log_manager = LogManager()
        assert log_manager.check_nextlog(
            LogCondition(Command.START_WITH, player_id=0, depth=0)) is False

    def test_has_log(self):
        log_manager = LogManager()
        log_manager.read_log("tests/test_log/test_1.txt")
        assert log_manager.has_logs()

    def test_check_next_log_and_pop(self):
        log_manager = LogManager()
        log_manager.read_log("tests/test_log/test_1.txt")
        log = log_manager.check_nextlog_and_pop(
            LogCondition(Command.START_WITH, player_id=0, depth=0))
        assert log.command == Command.START_WITH
        assert log.player_id == 0

    def test_check_next_log_and_pop_error(self):
        log_manager = LogManager()
        log_manager.read_log("tests/test_log/test_1.txt")
        assert log_manager.check_nextlog_and_pop(
            LogCondition(Command.DRAW, player_id=0, depth=0)) is None

    def test_get_nextlog(self):
        log_manager = LogManager()
        log_manager.read_log("tests/test_log/test_1.txt")
        size = len(log_manager._logs)
        log_manager.get_nextlog(
            LogCondition(Command.START_WITH, player_id=0, depth=0))
        assert len(log_manager._logs) == size

    def test_get_indent(self, make_log_manager):
        log_manager: LogManager = make_log_manager(
            ["A draws 星屑.", "@@A draws 岩石."]
        )
        assert log_manager.get_indent(0) == 0
        assert log_manager.get_indent(1) == 2
        assert log_manager.get_indent(2) is None

    def test_get_nextlog_error(self):
        log_manager = LogManager()
        log_manager.read_log("tests/test_log/test_1.txt")
        size = len(log_manager._logs)
        log = log_manager.get_nextlog(
            LogCondition(Command.DRAW, player_id=0, depth=0))
        assert log is None
        assert len(log_manager._logs) == size

    def test_check_result_log_1(self):
        log_manager = LogManager()
        log_manager.read_log("tests/test_log/test_1.txt")
        result = [
            {
                'point': 19, 'rank': 2, 'player_id': 0,
                'cards': [
                    1, 2, 3, 3, 3, 5, 5, 6, 6, 6,
                    13, 13, 13, 15, 15, 17, 25, 25]
            },
            {
                'point': 51, 'rank': 1, 'player_id': 1,
                'cards': [
                    1, 3, 3, 3, 4, 4, 4, 4, 4, 4, 5, 5, 5,
                    6, 12, 12, 13, 15, 15, 17, 17, 25]
            }
        ]
        assert log_manager.check_result_log(result) == "ok"

    def test_check_result_log_2(self):
        log_manager = LogManager()
        log_manager.read_log("tests/test_log/test_1.txt")
        result = []
        assert log_manager.check_result_log(
            result) == "The size of results doesn't match."

    def test_check_result_log_3(self):
        log_manager = LogManager()
        log_manager.read_log("tests/test_log/test_1.txt")
        result = [
            {
                'point': 18, 'rank': 2, 'player_id': 0,
                'cards': [
                    1, 2, 3, 3, 3, 5, 5, 6, 6, 6,
                    13, 13, 13, 15, 15, 17, 25, 25]
            },
            {
                'point': 51, 'rank': 1, 'player_id': 1,
                'cards': [
                    1, 3, 3, 3, 4, 4, 4, 4, 4, 4, 5, 5, 5,
                    6, 12, 12, 13, 15, 15, 17, 17, 25]
            }
        ]
        assert log_manager.check_result_log(
            result) == "point doesn't match. 19 vs 18"

    def test_check_result_log_4(self):
        log_manager = LogManager()
        log_manager.read_log("tests/test_log/test_1.txt")
        result = [
            {
                'point': 19, 'rank': 2, 'player_id': 0,
                'cards': [
                    2, 3, 3, 3, 5, 5, 6, 6, 6,
                    13, 13, 13, 15, 15, 17, 25, 25]
            },
            {
                'point': 51, 'rank': 1, 'player_id': 1,
                'cards': [
                    1, 3, 3, 3, 4, 4, 4, 4, 4, 4, 5, 5, 5,
                    6, 12, 12, 13, 15, 15, 17, 17, 25]
            }
        ]
        assert log_manager.check_result_log(result) == (
            "cards doesn't match. "
            "[1, 2, 3, 3, 3, 5, 5, 6, 6, 6, 13, 13, 13, 15, 15, 17, 25, 25]"
            " vs "
            "[2, 3, 3, 3, 5, 5, 6, 6, 6, 13, 13, 13, 15, 15, 17, 25, 25]"
        )

    def test_check_result_log_5(self):
        log_manager = LogManager()
        log_manager.read_log("tests/test_log/test_1.txt")
        log_manager._result = []
        result = [
            {
                'point': 19, 'rank': 2, 'player_id': 0,
                'cards': [
                    2, 3, 3, 3, 5, 5, 6, 6, 6,
                    13, 13, 13, 15, 15, 17, 25, 25]
            },
            {
                'point': 51, 'rank': 1, 'player_id': 1,
                'cards': [
                    1, 3, 3, 3, 4, 4, 4, 4, 4, 4, 5, 5, 5,
                    6, 12, 12, 13, 15, 15, 17, 17, 25]
            }
        ]
        assert log_manager.check_result_log(result) == (
            "Not found result of log."
        )

    def test_reprocess(self):
        log_manager = LogManager()
        lines = log_manager._preprocess([
            "A draws 星屑.",
            "A draws .",
            "A draws 岩石."
        ])
        assert lines == [
            "A draws 星屑.",
            "A draws 岩石."
        ]
