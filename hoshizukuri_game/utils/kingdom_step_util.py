"""
Get kingdom step with card_id.
"""
from .card_util import get_card_id
from ..steps.common_card_steps import (
    StardustStep, RockStep, SatelliteStep, PlanetStep, StarStep
)
from ..steps.abstract_step import AbstractStep


def get_kingdom_steps(
        player_id: int, depth: int,
        card_id: int, uniq_id: int, org_id: int = 0):
    """
    Get kingdom step with card_id.

    Args:
        player_id (int): player ID.
        depth (int): Expected log hierarchy.
        card_id (int): card ID of card step.
        uniq_id (int): unique ID of played card.
        org_id (int, Optional): Original card ID when card ID is way.

    Returns:
        AbstractStep: step.
    """
    if org_id == 0:
        org_id = card_id
    step_dic = {
        "planet": PlanetStep, "star": StarStep,
        "stardust": StardustStep, "rock": RockStep, "satellite": SatelliteStep,
    }
    step_id_dic = {}
    for k, v in step_dic.items():
        step_id_dic[get_card_id(k)] = v
    if card_id not in step_id_dic:
        print("Warining: Not found card step: %d" % card_id)
        return AbstractStep()
    return step_id_dic[card_id](player_id, depth, uniq_id)
