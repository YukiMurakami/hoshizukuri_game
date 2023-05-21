"""
Get kingdom step with card_id.
"""
from .card_util import get_card_id
from ..steps.common_card_steps import (
    HoshikuzuStep, GansekiStep, EiseiStep, WakuseiStep, KouseiStep
)
from ..steps.abstract_step import AbstractStep
from ..steps.base.seiun_step import SeiunStep
from ..steps.base.genshisei_step import GenshiseiStep
from ..steps.base.ikaduchi_step import IkaduchiStep
from ..steps.base.shinrin_step import ShinrinStep
from ..steps.base.sougen_step import SougenStep
from ..steps.base.mizu_step import MizuStep
from ..steps.base.suisho_step import SuishoStep
from ..steps.base.blackhole_step import BlackholeStep
from ..steps.base.funka_step import FunkaStep
from ..steps.base.kakuyugo_step import KakuyugoStep
from ..steps.base.kanketsusen_step import KanketsusenStep
from ..steps.base.kori_step import KoriStep
from ..steps.base.kudamononoki_step import KudamononokiStep
from ..steps.base.honow_step import HonowStep
from ..steps.base.izumi_step import IzumiStep
from ..steps.base.seiza_step import SeizaStep
from ..steps.base.arashi_step import ArashiStep
from ..steps.base.bisebutsu_step import BisebutsuStep
from ..steps.base.daichi_step import DaichiStep
from ..steps.base.inseki_step import InsekiStep


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
        "daichi": DaichiStep, "inseki": InsekiStep,
        "arashi": ArashiStep, "bisebutsu": BisebutsuStep,
        "izumi": IzumiStep, "seiza": SeizaStep,
        "kudamononoki": KudamononokiStep, "honow": HonowStep,
        "kanketsusen": KanketsusenStep, "kori": KoriStep,
        "funka": FunkaStep, "kakuyugo": KakuyugoStep,
        "suisho": SuishoStep, "blackhole": BlackholeStep,
        "sougen": SougenStep, "mizu": MizuStep,
        "ikaduchi": IkaduchiStep, "shinrin": ShinrinStep,
        "seiun": SeiunStep, "genshisei": GenshiseiStep,
        "wakusei": WakuseiStep, "kousei": KouseiStep,
        "hoshikuzu": HoshikuzuStep, "ganseki": GansekiStep, "eisei": EiseiStep,
    }
    step_id_dic = {}
    for k, v in step_dic.items():
        step_id_dic[get_card_id(k)] = v
    if card_id not in step_id_dic:
        print("Warining: Not found card step: %d" % card_id)
        return AbstractStep()
    return step_id_dic[card_id](player_id, depth, uniq_id)
