import sys
import os
import pytest


sys.path.append(os.path.abspath(
    os.path.dirname(os.path.abspath(__file__)) + "/../hoshizukuri_game/"))


@pytest.fixture
def get_step_classes():
    def _get_class(steps):
        return [n.__class__ for n in steps]
    return _get_class


@pytest.fixture
def is_equal_candidates():
    def _is_equal_candidates(a, b):
        return sorted(a) == sorted(b)
    return _is_equal_candidates
