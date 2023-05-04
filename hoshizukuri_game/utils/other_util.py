"""
Other utility methods.
"""
from __future__ import annotations
from typing import Union, List
from ..models.card import Card
import itertools


def make_combination(
        cards: Union[List[int], List[Card]], count: int, less_flag: bool):
    """
    Make card_id combinations list.

    Args:
        cards (List[int] or List[Card]): Select cards from this list.
        count (int): the number of select cards.
        less_flag (bool): True is that the number of select cards can be less.

    Returns:
        List[List[int]]: The list of selected card list.

    Note:
        - When count is less than the size of cards, count will be this size.
    """
    if count > len(cards):
        count = len(cards)
    candidates = []
    if len(cards) <= 0:
        return [[]]
    if isinstance(cards[0], Card):
        candidates = [card.id for card in cards]
    else:
        candidates = [n for n in cards]
    candidates = sorted(candidates)
    result = []
    if less_flag is False:
        tmp = list(set(list(itertools.combinations(
            candidates, count))))
        for t_e in tmp:
            result.append(list(t_e))
    else:
        for i in range(count):
            result += make_combination(candidates, i + 1, False)
        result += [[]]
    return result


def make_permutation(
        cards: Union[List[int], List[Card]], count: int, less_flag: bool):
    """
    Make card_id permutation list.

    Args:
        cards (List[int] or List[Card]): Select cards from this list.
        count (int): the number of select cards.
        less_flag (bool): True is that the number of select cards can be less.

    Returns:
        List[List[int]]: The list of selected card list.

    Note:
        - When count is less than the size of cards, count will be this size.
    """
    if count > len(cards):
        count = len(cards)
    candidates = []
    if len(cards) <= 0:
        return [[]]
    if isinstance(cards[0], Card):
        candidates = [card.id for card in cards]
    else:
        candidates = [n for n in cards]
    candidates = sorted(candidates)
    result = []
    if less_flag is False:
        tmp = _make_permutation_without_itertools(candidates, count)
        for t_e in tmp:
            result.append(list(t_e))
    else:
        for i in range(count):
            result += make_permutation(candidates, i + 1, False)
        result += [[]]
    return result


def _make_permutation_without_itertools(candidates, count):
    queue = [[[], candidates]]
    while len(queue[0][1]) > len(candidates) - count:
        next_queue = []
        for item in queue:
            for cand in list(set(item[1])):
                now_list = list(item[0])
                next_list = now_list + [cand]
                next_candidates = list(item[1])
                next_candidates.remove(cand)
                next_queue.append([next_list, next_candidates])
        queue = next_queue
    return [n[0] for n in queue]
