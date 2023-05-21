"""
This module defines the utility functions about choice.
"""
from typing import List
import re


def cparseii(choice: str):
    """
    Parse the double int type choice.
    (a:command:b-c)
    Assumed that a is player ID, b is card ID, c is card uniq ID.
    If c lacks, uniq iD will be -1.

    Args:
        choice (str): choice.

    Returns:
        List[Any]: n1, command, n2, n3  (if n3 is None, n3 = -1)
    """
    div = choice.split(":")
    assert len(div) in [2, 3]
    div2 = div[2].split("-")
    card_id = int(div2[0])
    uniq_id = -1
    if len(div2) == 2:
        uniq_id = int(div2[1])
    return int(div[0]), div[1], card_id, uniq_id


def cparsei(choice: str):
    """
    Parse the int type choice.
    (a:command:b)
    Assumed that a is player ID, b is card ID.

    Args:
        choice (str): choice.

    Returns:
        List[Any]: n1, command, n2.
    """
    div = choice.split(":")
    assert len(div) == 3
    return int(div[0]), div[1], int(div[2])


def cparsell(choice: str):
    """
    Parse the list of double int type choice.
    (a:command:b-c,d-e)
    Assumed that a is player ID, b, d are card IDs, c, e are card uniq IDs.

    Args:
        choice (str): choice.

    Returns:
        List[Any]: n1, command, [n2, n3, ...], [n4, n5, ...].
    """
    div = choice.split(":")
    card_ids = []
    uniq_ids = []
    for d_e in div[2].split(","):
        if d_e == "":
            continue
        div2 = d_e.split("-")
        card_ids.append(int(div2[0]))
        if len(div2) == 2:
            uniq_ids.append(int(div2[1]))
    if len(card_ids) != len(uniq_ids):
        uniq_ids = []
    if card_ids == [0]:
        card_ids = []
    return int(div[0]), div[1], card_ids, uniq_ids


def cparses(choice: str):
    """
    Parse the str type choice.
    (a:command:param)
    Assumed that a is player ID.

    Args:
        choice (str): choice.

    Returns:
        List[Any]: n1, command, param.
    """
    div = choice.split(":")
    assert len(div) >= 3
    param = ":".join(div[2:])
    return int(div[0]), div[1], param


def is_included_candidates(choice: str, candidates: List[str]):
    no_hyphen_candidates = [
        re.sub(r"(\d+)-(\d+)", "\\1", n) for n in candidates
    ]
    no_hyphen_choice = re.sub(r"(\d+)-(\d+)", "\\1", choice)
    return no_hyphen_choice in no_hyphen_candidates
