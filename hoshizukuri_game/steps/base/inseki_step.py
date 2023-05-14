"""
Inseki card steps.
"""
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...models.game import Game
from ...models.pile import PileName
from ..abstract_step import AbstractStep
from ..common.reveal_step import RevealAllHandStep
from ..common.discard_step import discard_select_process
from ..common.draw_step import DrawStep
from ...models.card_condition import (
    CardConditionOr, CardCondition, get_match_card_ids
)
from ...utils.card_util import (
    get_colors, CardColor
)
from ...utils.other_util import get_enemy_ids


class InsekiStep(AbstractStep):
    """
    Inseki card step.

    Args:
        player_id (int): player ID.
        depth (int): Expected log hierarchy.
        uniq_id (int): unique ID.
    """
    def __init__(self, player_id: int, depth: int, uniq_id: int):
        super().__init__()
        self.player_id = player_id
        self.depth = depth
        self.uniq_id = uniq_id

    def __str__(self):
        return "%d:inseki:%d" % (self.depth, self.player_id)

    def process(self, game: Game):
        steps = []
        for e_id in reversed(get_enemy_ids(self.player_id, len(game.players))):
            steps.append(_InsekiAttackStep(
                e_id, self.depth, self.player_id, self.uniq_id))
        return steps


class _InsekiAttackStep(AbstractStep):
    """
    Inseki discard step. (Attack)

    Args:
        player_id (int): player ID.
        depth (int): Expected log hierarchy.
        attacker_id (int): Attacker player ID.
        uniq_id (int): unique ID.
    """
    def __init__(
            self, player_id: int, depth: int, attacker_id: int, uniq_id: int):
        super().__init__()
        self.player_id = player_id
        self.depth = depth
        self.attacker_id = attacker_id
        self.uniq_id = uniq_id

    def __str__(self):
        return "%d:insekiattack:%d" % (self.depth, self.player_id)

    def callback(self, card_ids, uniq_ids, game):
        return [DrawStep(self.player_id, self.depth, 1)]

    def process(self, game: Game):
        field_colors = []
        for card_list in game.players[
                self.attacker_id].pile[PileName.FIELD].card_list:
            for card in card_list:
                for color in get_colors(card.id):
                    if (color != CardColor.NEUTRAL and
                            color not in field_colors):
                        field_colors.append(color)
        if len(field_colors) <= 0:
            return []
        condition = CardConditionOr(
            [CardCondition(color=n) for n in field_colors]
        )
        candidates = get_match_card_ids(
            game.players[self.player_id].pile[PileName.HAND], condition, game)
        if len(candidates) <= 0:
            if game.players[self.player_id].pile[PileName.HAND].count > 0:
                return [RevealAllHandStep(self.player_id, self.depth)]
            return []
        return discard_select_process(
            game, self, "insekidiscard", 1, next_step_callback=self.callback,
            card_condition=condition
        )
