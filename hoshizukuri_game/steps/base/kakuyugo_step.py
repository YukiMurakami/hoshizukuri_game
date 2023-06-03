"""
Kakuyugo card steps.
"""
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...models.game import Game
from ..abstract_step import AbstractStep
from ...models.pile import PileName
from ...models.log import LogCondition, Command
from ...utils.choice_util import cparsell, is_included_candidates
from ...utils.card_util import CardColor, get_colors, ids2uniq_ids
from ..common.trash_step import TrashStep


class KakuyugoStep(AbstractStep):
    """
    Kakuyugo card step.

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
        return "%d:kakuyugo:%d" % (self.depth, self.player_id)

    def process(self, game: Game):
        dic = {
            0: 1,
            1: 2,
            2: 4,
            3: 7,
            4: 10
        }
        card = game.players[self.player_id].pile[
            PileName.FIELD].get_card(self.uniq_id)
        if game.players[self.player_id].pile[PileName.HAND].count <= 0:
            card.starflake = dic[0]
            return []
        candidates = self._create_candidates(game)
        if game.log_manager is not None:
            game.choice = self._log2choice(game)
        if game.choice == "" or not is_included_candidates(
                game.choice, candidates):
            self.candidates = candidates
            return [self]
        else:
            self.candidates = []
        player_id, command, card_ids, uniq_ids = cparsell(game.choice)
        game.choice = ""
        assert command in ["kakuyugotrash"]
        assert player_id == self.player_id
        if card_ids == []:
            card.starflake = dic[0]
            return []
        if uniq_ids == []:
            uniq_ids = ids2uniq_ids(
                game.players[self.player_id].pile[PileName.HAND],
                card_ids, game
            )
        assert len(card_ids) <= 4
        card.starflake = dic[len(card_ids)]
        return [
            TrashStep(
                self.player_id, self.depth, card_ids, uniq_ids
            )
        ]

    def _create_candidates(self, game: Game):
        command = "kakuyugotrash"
        candidates = []
        # same color
        same_color_list = {
            CardColor.RED: [],
            CardColor.BLUE: [],
            CardColor.GREEN: [],
            CardColor.NEUTRAL: []
        }
        for color in [
                CardColor.RED, CardColor.BLUE,
                CardColor.GREEN, CardColor.NEUTRAL]:
            for card in game.players[self.player_id].pile[
                    PileName.HAND].card_list:
                if color in get_colors(card.id, game):
                    if card.id not in same_color_list[color]:
                        same_color_list[color].append(card.id)
        for red in same_color_list[CardColor.RED] + [0]:
            for blue in same_color_list[CardColor.BLUE] + [0]:
                for green in same_color_list[CardColor.GREEN] + [0]:
                    for neutral in same_color_list[CardColor.NEUTRAL] + [0]:
                        candidate = [n for n in [
                            red, blue, green, neutral] if n != 0]
                        candidate = sorted(candidate)
                        if candidate not in candidates:
                            candidates.append(candidate)
        candidates = sorted(candidates)
        return ["%d:%s:%s" % (self.player_id, command, ",".join(
            [str(n) for n in cand])) for cand in candidates]

    def _log2choice(self, game: Game):
        if not game.log_manager.has_logs():
            return game.choice
        log_condition = LogCondition(
            Command.TRASH_FROM_HAND, self.player_id, depth=self.depth)
        log = game.log_manager.get_nextlog(
            log_condition
        )
        if log is None:
            return "%d:kakuyugotrash:" % self.player_id
        return "%d:kakuyugotrash:%s" % (
            self.player_id, ",".join([str(n) for n in log.card_ids])
        )
