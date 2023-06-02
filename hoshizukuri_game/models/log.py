"""
This module defines the Log model.
"""
from __future__ import annotations
from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from ..models.game import Game
from enum import Enum
from ..utils.card_util import get_card_id, str2ids, is_same_card_ids
import re
from copy import deepcopy


class Command(Enum):
    START_WITH = "<PLAYER> starts with <CARDS>."
    SHUFFLE = "<PLAYER> shuffles their deck."
    DRAW = "<PLAYER> draws <CARDS>."
    TURN_START = "Turn - <PLAYER>."
    PLAY = "<PLAYER> plays <CARDS>."
    RESOLVE_EFFECT = "<PLAYER> resolves the effects of <CARD>."
    CHANGE_ORBIT = (
        "<PLAYER> changes the number of orbits "
        "from <NUMBER> to <NUMBER2>."
    )
    CREATE = "<PLAYER> creates <CARD>."
    DISCARD_FROM_PLAYAREA = "<PLAYER> discards <CARDS> from their playarea."
    DISCARD_FROM_HAND = "<PLAYER> discards <CARDS> from their hand."
    DISCARD_FROM_LOOK = "<PLAYER> discards <CARDS> from their look."
    LOOK_FROM_DECK = "<PLAYER> looks <CARDS> from their deck."
    REVEAL_FROM_DECK = "<PLAYER> reveals <CARDS> from their deck."
    PUT_HAND_FROM_LOOK = (
        "<PLAYER> puts <CARDS> into their hand from their look."
    )
    ADD_PLAY_FROM_REVEAL = (
        "<PLAYER> adds <CARDS> to the play from their reveal."
    )
    ADD_PLAY_FROM_HAND = (
        "<PLAYER> adds <CARDS> to the play from their hand."
    )
    TRASH_FROM_HAND = "<PLAYER> trashes <CARDS> from their hand."
    GAIN_INTO_HAND = "<PLAYER> gains <CARD> into their hand."
    GAIN_INTO_DISCARD = "<PLAYER> gains <CARD> into their discard."
    TRASH_FROM_PLAYAREA = "<PLAYER> trashes <CARDS> from their playarea."


class InvalidLogException(Exception):
    """
    InvalidLogException class.

    Args:
        game (Game): now game.
    """
    def __init__(self, game: Game, log_condition: LogCondition = None):
        self.game = deepcopy(game)
        self.log_condition = log_condition

    def __str__(self):
        log_str = ""
        line_n = 0
        if self.game.log_manager.has_logs():
            log_str = self.game.log_manager._logs[0].line
            line_n = self.game.log_manager._logs[0].line_n
        log_cond_str = ""
        if self.log_condition is not None:
            log_cond_str = str(self.log_condition)
        return "Invalid Log Exception - line %d: %s (%s)" % (
            line_n + 1, log_str, log_cond_str)


class LogCondition:
    """
    LogCondition model class.

    Args:
        command (Command): Must be this command.
        player_id (int): Must be this player ID.
        depth (int): Must be this depth (indent).
        numbers (List[int], Optional): Must be this number.
        card_ids (List[int], Optional): Must be this card IDs.
    """
    def __init__(
            self, command: Command, player_id: int, depth: int,
            numbers: List[int] = None, card_ids: List[int] = None):
        self.command = command
        self.player_id = player_id
        self.depth = depth
        self.numbers = None
        if numbers is not None:
            self.numbers = list(numbers)
        self.card_ids = None
        if card_ids is not None:
            self.card_ids = list(card_ids)

    def __str__(self):
        strings = [
            "command=%s" % str(self.command).lower().replace(
                "command.", ""),
            "player_id=%d" % self.player_id,
            "depth=%d" % self.depth
        ]
        if self.numbers is not None:
            strings.append("numbers=[%s]" % ",".join(
                [str(n) for n in self.numbers]))
        if self.card_ids is not None:
            strings.append("card_ids=[%s]" % ",".join(
                [str(n) for n in self.card_ids]))
        return ",".join(strings)


class LogConditionOr(LogCondition):
    """
    LogCondition which has OR conditions.

    Args:
        log_conditions (List[LogCondition]): LogCondition list.
    """
    def __init__(self, log_conditions):
        self.log_conditions = list(log_conditions)

    def __str__(self):
        return "%s" % (
            "|".join(str(n) for n in self.log_conditions))


class Log():
    """
    Log model class.

    Args:
        names (List[str]): player full names in order.
        command (COMMAND): Command of log.
        indent (int): Indent of log.
        line (str): Raw log.

    Params:
        indent (int): Indent of log.
        player_id (int): Player ID of <PLAYER> param.
        numbers (List[int]): The list of numbers of <NUMBER> params.
        card_ids (List[int]): The card IDs of <CARDS> param.
        card_id (int): The card ID of <CARD> param.
        command (COMMAND): Command of log.
        line (str): Raw Log.
        line_n (int): Log index.
    """
    def __init__(
            self, names: List[str],
            command: Command, indent: int, line: str):
        self.indent: int = indent
        self.player_id: int = None
        self.numbers: List[int] = None
        self.card_ids: List[int] = None
        self.card_id: int = None
        self.command: Command = command
        self.line: str = line
        self.line_n: int = 0
        self._names: List[str] = names

    def __str__(self):
        s = "%d:%s" % (self.indent, self.command.name)
        if self.player_id is not None:
            s += ",player_id=%d" % self.player_id
        if self.card_id is not None:
            s += ",card_id=%d" % self.card_id
        if self.card_ids is not None:
            s += ",card_ids=[%s]" % ",".join([
                str(n) for n in self.card_ids])
        if self.numbers is not None:
            s += ",numbers=[%s]" % ",".join([
                str(n) for n in self.numbers])
        return s

    def set_key(self, key: str, value: str) -> bool:
        """
        Set key and value into log.

        Args:
            key (str): Key which is included in Command values.
            value (str): Value which is input in Key of Command values.

        Returns:
            bool: True is for success.
        """
        if key == "PLAYER":
            if value not in self._names:
                return False
            self.player_id = self._names.index(value)
            return True
        if key == "NUMBER":
            if value.isdigit() is False:
                return False
            if self.numbers is None:
                self.numbers = [None, None]
            self.numbers[0] = int(value)
            return True
        if key == "NUMBER2":
            if value.isdigit() is False:
                return False
            if self.numbers is None:
                self.numbers = [None, None]
            self.numbers[1] = int(value)
            return True
        if key == "CARD":
            try:
                card_ids = str2ids(value)
                if len(card_ids) != 1:
                    return False
                self.card_id = card_ids[0]
                return True
            except Exception:
                return False
        if key == "CARDS":
            try:
                card_ids = str2ids(value)
                card_ids = sorted(card_ids)
                self.card_ids = card_ids
                return True
            except Exception:
                return False
        raise Exception("Not found key: %s", key)


class LogFormatter():
    """
    Make Log list from log strings.
    """
    def __init__(self):
        self._names = []
        self.preds = []
        for pred in sorted([
                n.value for n in Command]):
            self.preds.append(self._get_re_pattern(pred))

    def set_names(self, names):
        """
        Set player's names

        Args:
            names: List[str]: Player's full names.
        """
        self._names = names

    def _get_re_pattern(self, pred: str):
        replaced_pred = pred
        replace_tokens = ["(", ")", "+", "$", ".", "[", "]"]
        keys = []
        for token in replace_tokens:
            replaced_pred = replaced_pred.replace(token, "\\" + token)
        for a in re.finditer(r"<.*?>", pred):
            keys.append(a.group()[1: -1])
            replaced_pred = replaced_pred.replace(a.group(), "(.*?)", 1)
        if replaced_pred[-1] != "$":
            replaced_pred += "$"
        return {
            "command": Command(pred),
            "re_pattern": replaced_pred,
            "key_list": keys
        }

    def _get_indent_and_line(self, line: str):
        m = re.match(r"@*", line)
        indent = len(m.group())
        line = line.replace("@", "")
        return indent, line

    def format(self, lines: List[str]) -> List[Log]:
        # skip initial lines
        index = 0
        for n, line in enumerate(lines):
            if "starts with" in line:
                index = n
                break
        result_logs = []
        lines = lines[index:]
        while len(lines) > 0:
            if lines[0] == "Game over.":
                break
            logs, lines = self._make_log(lines)
            for log in logs:
                log.line_n = index
            index += 1
            result_logs += logs
        return result_logs

    def _make_log(self, lines: List[str]):
        line = lines[0]
        if line == "":
            return [], lines[1:]
        indent, line = self._get_indent_and_line(line)
        for pred in self.preds:
            m = re.match(pred["re_pattern"], line)
            if m:
                log = self._parse_log(m, pred, indent, line)
                if log is None:
                    continue
                return [log], lines[1:]
        raise Exception("Not found command pattern: %s", line)

    def _parse_log(self, m: re.Match, pred: dict, indent: int, line: str):
        assert m is not None
        log = Log(self._names, pred["command"], indent, line)
        for i, key in enumerate(pred["key_list"]):
            value = m.group(i + 1)
            if value is not None:
                result = log.set_key(key, value)
                if result is False:
                    return None
        return log


class LogManager():
    """
    LogManager model class.
    """
    def __init__(self):
        self.debug = False
        self._names: List[str] = []
        self._supply_ids: List[int] = []
        self._logs: List[Log] = []
        self._log_formatter: LogFormatter = LogFormatter()
        self._result: List[dict] = []

    def get_names(self):
        """
        Get player names.

        Returns:
            List[str]: names.
        """
        return self._names

    def get_supplies(self):
        """
        Get supplies.

        Returns:
            List[int]: supply Card IDs.
        """
        return self._supply_ids

    def _get_names(self, lines: List[str]):
        names = []
        div_keyword = " starts with "
        for line in lines:
            if div_keyword in line:
                name = line.split(div_keyword)[0]
                if name not in names:
                    names.append(name)
        return names

    def _get_supply(self, lines: List[str]):
        supply_ids = []
        div_keyword = "Supply:"
        for line in lines:
            if div_keyword in line:
                supply_ids = [
                    get_card_id(n.strip()) for n in line.split(
                        div_keyword)[1].split(".")[0].split(",")]
        return sorted(supply_ids)

    def _get_result(self, lines: List[str]):
        orders = []
        results = []
        order_index = None
        for i, line in enumerate(lines):
            m = re.match("The order is (.*?)\\.", line)
            if m:
                orders = m.group(1).split(", ")
                order_index = i + 1
                break
        if order_index is not None:
            for j in range(len(orders)):
                tmp_result = {
                    "point": 0,
                    "rank": 0,
                    "player_id": "",
                    "cards": []
                }
                name1, name2 = "", ""
                for i in range(2):
                    index = order_index + j * 2 + i
                    if i % 2 == 0:
                        m = re.match(
                            "^(.*?) has (\\d+?) points\\.", lines[index])
                        tmp_result["point"] = int(m.group(2))
                        name1 = m.group(1)
                        tmp_result["rank"] = orders.index(name1) + 1
                        tmp_result["player_id"] = self._names.index(name1)
                    else:
                        m = re.match(
                            "^(.*?) has (.*?)\\.", lines[index]
                        )
                        tmp_result["cards"] = sorted(str2ids(m.group(2)))
                        name2 = m.group(1)
                assert name1 == name2
                results.append(tmp_result)
        return results

    def check_result_log(self, result: List[dict]):
        """
        Check results of log and game.

        Args:
            result: the result of game.

        Returns:
            str: "ok" or error message.
        """
        if len(self._result) == 0:
            return "Not found result of log."
        if len(self._result) != len(result):
            return "The size of results doesn't match."
        a = sorted(self._result, key=lambda x: x["rank"])
        b = sorted(result, key=lambda x: x["rank"])
        for key in ["point", "rank", "player_id", "cards"]:
            for i in range(len(a)):
                if a[i][key] != b[i][key]:
                    return "%s doesn't match. %s vs %s" % (
                        key, a[i][key], b[i][key]
                    )
        return "ok"

    def read_log(self, filename: str):
        """
        Read log.

        Args:
            filename (str): filename of log.
        """
        lines = [n.strip() for n in open(filename).readlines()]
        lines = self._preprocess(lines)
        self._names = self._get_names(lines)
        self._supply_ids = self._get_supply(lines)
        self._log_formatter.set_names(self._names)
        self._logs = self._log_formatter.format(lines)
        self._result = self._get_result(lines)

    def _preprocess(self, lines: List[str]):
        """
        Fix invalid log with app bug.
        """
        fix_lines = []
        for line in lines:
            if "draws ." in line:
                continue
            fix_lines.append(line)
        return fix_lines

    def pop(self):
        """
        Pop next Log.

        Returns:
            Log: next log.
        """
        if len(self._logs) > 0:
            log = self._logs[0]
            del self._logs[0]
            if self.debug:
                print('\033[31m'+'%s' % log+'\033[0m')
            return log
        return None

    def check_nextlog(self, log_condition: LogCondition, offset: int = 0):
        """
        Check whether next log has command, player_id or not.

        Args:
            log_condition (LogCondition): Check if this is matched.
            offset (int): Check the Xth log from the top.

        Returns:
            bool: True if for match.
        """
        if log_condition is None:
            raise Exception("Invalid Log, %s %d" % (
                self._logs[offset].line, self._logs[offset].line_n + 1))
        if len(self._logs) <= offset:
            return False
        if isinstance(log_condition, LogConditionOr):
            for cond in log_condition.log_conditions:
                if self.check_nextlog(cond, offset=offset):
                    return True
            return False
        if (self._logs[offset].command == log_condition.command and
                self._logs[offset].indent == log_condition.depth) is False:
            return False
        if self._logs[offset].player_id is not None:
            if self._logs[offset].player_id != log_condition.player_id:
                return False
        if (log_condition.numbers is not None and
                self._logs[offset].numbers != log_condition.numbers):
            return False
        if log_condition.card_ids is not None:
            if len(log_condition.card_ids) == 1:
                if (self._logs[offset].card_id is not None and
                        self._logs[
                            offset].card_id != log_condition.card_ids[0]):
                    return False
                if (self._logs[offset].card_ids is not None and
                        is_same_card_ids(
                            self._logs[offset].card_ids,
                            log_condition.card_ids) is False):
                    return False
            elif len(log_condition.card_ids) > 1:
                if (self._logs[offset].card_ids is not None and
                        is_same_card_ids(
                            self._logs[offset].card_ids,
                            log_condition.card_ids) is False):
                    return False
        return True

    def has_logs(self):
        """
        Check exist of log.

        Returns:
            bool: True is that there are any logs.
        """
        return len(self._logs) > 0

    def get_indent(self, offset: int):
        """
        Get log indent.

        Args:
            offset (int): get the Xth log indent from the top.

        Returns:
            int: indent. (This is None when offset is out of log size.)
        """
        if len(self._logs) <= offset:
            return None
        return self._logs[offset].indent

    def check_nextlog_and_pop(self, log_condition: LogCondition):
        """
        Pop log if next log has command, player_id, number.

        Args:
            log_condition (LogCondition): Check if this is matched.

        Returns:
            Log: next log. If conditions doesn't match, None.
        """
        if not self.check_nextlog(log_condition):
            return None
        return self.pop()

    def get_nextlog(self, log_condition: LogCondition, offset: int = 0):
        """
        Get log if next log has command, player_id, number.

        Args:
            log_condition (LogCondition): Check if this is matched.
            offset (int): Check the Xth log from the top.

        Returns:
            Log: next log. If conditions doesn't match, None.
        """
        if not self.check_nextlog(log_condition, offset=offset):
            return None
        if self.debug:
            print('\033[32m'+'%s' % self._logs[0]+'\033[0m')
        return self._logs[offset]
