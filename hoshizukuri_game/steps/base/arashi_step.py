"""
Arashi card steps.
"""
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...models.game import Game
from ..abstract_step import AbstractStep
from ...models.pile import PileName
from ..common.discard_step import DiscardStep
from ...utils.choice_util import cparsei, is_included_candidates


class ArashiStep(AbstractStep):
    """
    Arashi card step.

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
        return "%d:arashi:%d" % (self.depth, self.player_id)

    def process(self, game: Game):
        if len(game.players[self.player_id].pile[
                PileName.FIELD].card_list) <= 1:
            return []
        candidates = self._create_candidates(game)
        if game.choice == "" or not is_included_candidates(
                game.choice, candidates):
            self.candidates = candidates
            return [self]
        else:
            self.candidates = []
        player_id, command, index = cparsei(game.choice)
        game.choice = ""
        assert command in ["arashiindex"]
        assert player_id == self.player_id
        if index == -1:
            return []
        card_ids = [n.id for n in game.players[
            self.player_id].pile[PileName.FIELD].card_list[index]]
        uniq_ids = [n.uniq_id for n in game.players[
            self.player_id].pile[PileName.FIELD].card_list[index]]
        discard_step = DiscardStep(
            self.player_id, self.depth, card_ids, uniq_ids,
            from_pilename=PileName.FIELD
        )
        discard_step.orbit_index = index
        return [discard_step]

    def _create_candidates(self, game: Game):
        candidates = []
        field = game.players[self.player_id].pile[PileName.FIELD].card_list
        for i, cardlist in enumerate(field):
            if len(cardlist) == 1 and i != len(field) - 1:
                candidates.append(i)
        return [
            "%d:arashiindex:%d" % (
                self.player_id, n
            ) for n in candidates + [-1]
        ]
