from hoshizukuri_game.utils.other_util import (
    make_combination, make_permutation
)
from hoshizukuri_game.models.card import Card


class TestMakeCombination():
    def test_make_combination1(self):
        result = make_combination([1, 1, 2, 3], 2, False)
        assert result == [[2, 3], [1, 1], [1, 2], [1, 3]]

    def test_make_combination2(self):
        result = make_combination([
            Card(1, 1), Card(1, 2), Card(2, 3), Card(3, 4)
        ], 2, False)
        assert result == [[2, 3], [1, 1], [1, 2], [1, 3]]

    def test_make_combination3(self):
        result = make_combination([], 0, False)
        assert result == [[]]

    def test_make_combination4(self):
        result = make_combination([1, 1, 2, 3], 2, True)
        assert result == [[1], [2], [3], [2, 3], [1, 1], [1, 2], [1, 3], []]

    def test_make_combination5(self):
        result = make_combination([1, 1, 2], 5, False)
        assert result == [[1, 1, 2]]


class TestMakePermutation():
    def test_make_permutation1(self):
        result = make_permutation([1, 1, 3], 2, False)
        assert result == [
            [1, 1], [1, 3], [3, 1]
        ]

    def test_make_permutation2(self):
        result = make_permutation(
            [Card(1, 1), Card(1, 2), Card(3, 3)], 2, False)
        assert result == [
            [1, 1], [1, 3], [3, 1]
        ]

    def test_make_permutation3(self):
        result = make_permutation([], 0, False)
        assert result == [[]]

    def test_make_permutation4(self):
        result = make_permutation([1, 1, 3], 2, True)
        assert result == [[1], [3], [1, 1], [1, 3], [3, 1], []]

    def test_make_permutation5(self):
        result = make_permutation([1, 1, 3], 5, False)
        assert result == [[1, 1, 3], [1, 3, 1], [3, 1, 1]]
