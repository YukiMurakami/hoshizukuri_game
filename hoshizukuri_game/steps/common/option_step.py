"""
Select option steps and process.
"""
from __future__ import annotations
from typing import TYPE_CHECKING, List, Dict, Callable, Any
if TYPE_CHECKING:
    from ...models.game import Game
from ..abstract_step import AbstractStep
from ...utils.choice_util import is_included_candidates


def option_select_process(
        game: Game, source_step: AbstractStep,
        next_steps_dic: Dict[str, Callable[[Game], List[AbstractStep]]],
        params: Dict[Any] = {}):
    """
    Common process of selecting option process.
    This function is assumed to be used in each Steps.

    Args:
        game (Game): now game.
        source_step (AbstractStep): the step which uses this process.
        next_steps_dic (Dict[str, Callable[[Game], List[AbstractStep]]]):
            next_steps for each choices.
        params (Dict[Any], Optional): params

    Returns:
        List[AbstractStep]: the next steps.

    Note:
        - source_step must have below methods.
            - _log2choice(game: Game, params: Dict[Any]) -> str
            - _create_candidates(game: Game, params: Dict[Any]) -> List[str]
    """
    candidates = source_step._create_candidates(game, params)
    if len(candidates) == 1:
        assert candidates[0] in next_steps_dic
        return next_steps_dic[candidates[0]](game, params)
    if game.choice == "" or not is_included_candidates(
            game.choice, candidates):
        source_step.candidates = candidates
        return [source_step]
    else:
        source_step.candidates = []
    choice = game.choice
    game.choice = ""
    assert choice in next_steps_dic
    return next_steps_dic[choice](game, params)
