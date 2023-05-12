"""
Blackhole card steps.
"""
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...models.game import Game
from ..abstract_step import AbstractStep
from ...models.card_condition import CardCondition, get_match_card_ids
from ...models.pile import PileName


class BlackholeStep(AbstractStep):
    """
    Blackhole card step.

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
        return "%d:blackhole:%d" % (self.depth, self.player_id)

    def process(self, game: Game):
        neutral_creates = get_match_card_ids(
            game.players[self.player_id].pile[PileName.HAND],
            CardCondition(create=True), game
        )
        if len(neutral_creates) <= 0:
            return []
        from ..common.play_step import play_add_select_process
        return play_add_select_process(
            game, self, "blackholeaddplay", len(neutral_creates),
            can_less=True,
            card_condition=CardCondition(
                create=True
            ),
            next_step_callback=self.callback
        )

    def callback(self, card_ids, uniq_ids, game: Game):
        for uniq_id in uniq_ids:
            for card in game.players[
                    self.player_id].pile[PileName.HAND].card_list:
                if card.uniq_id == uniq_id:
                    card.create = False
        return []
