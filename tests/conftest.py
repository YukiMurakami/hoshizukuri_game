import sys
import os
import pytest

from hoshizukuri_game.models.log import LogFormatter, LogManager


sys.path.append(os.path.abspath(
    os.path.dirname(os.path.abspath(__file__)) + "/../hoshizukuri_game/"))


@pytest.fixture
def get_step_classes():
    def _get_class(steps):
        return [n.__class__ for n in steps]
    return _get_class


@pytest.fixture
def make_log_manager() -> LogManager:
    def _make_logs(line):
        log_manager = LogManager()
        log_formatter = LogFormatter()
        log_formatter.set_names(["A", "B"])
        lines = []
        if isinstance(line, str):
            lines = [line]
        else:
            lines = line
        log_manager._logs = []
        index = 0
        while len(lines) > 0:
            logs, lines = log_formatter._make_log(lines)
            for log in logs:
                log.line_n = index
            log_manager._logs += logs
            index += 1
        return log_manager
    return _make_logs


@pytest.fixture
def is_equal_candidates():
    def _is_equal_candidates(a, b):
        return sorted(a) == sorted(b)
    return _is_equal_candidates
