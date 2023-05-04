"""
Steps for sequence of turn.
"""
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..models.game import Game
from ..models.turn import Turn
from .abstract_step import AbstractStep
from ..models.turn import Phase
from ..models.pile import PileName
from ..models.card import CardColor
from ..utils.card_util import (
    get_colors, ids2uniq_ids
)
from ..utils.other_util import (
    make_permutation
)
from ..utils.choice_util import (
    cparsell
)
from itertools import product


class TurnStartStep(AbstractStep):
    """
    This is TurnStartStep.

    Args:
        player_id (int): turn player ID.
        turn (Turn): this turn.
    """
    def __init__(self, player_id: int, turn: Turn):
        super().__init__()
        self.player_id = player_id
        self.turn = turn
        self.depth = 0

    def __str__(self):
        return "%d:turnstart:%s" % (self.depth, str(self.turn))

    def process(self, game: Game):
        game.phase = Phase.TURN_START
        game.turn = self.turn
        assert game.turn.player_id == self.player_id
        game.starflake = 0
        return [PlaySelectStep(self.player_id)]


class PrepareFirstDeckStep(AbstractStep):
    """
    Make player's first deck.

    Args:
        player_id (int): player ID.
    """
    def __init__(self, player_id):
        super().__init__()
        self.player_id = player_id
        self.depth = 0

    def __str__(self):
        return "%d:preparefirstdeck:%d" % (self.depth, self.player_id)

    def process(self, game: Game):
        for card_id in game.start_deck:
            card = game.make_card(card_id)
            game.players[self.player_id].pile[PileName.DISCARD].push(
                card
            )
        return []


class PlaySelectStep(AbstractStep):
    """
    Select cards to play.

    Args:
        player_id (int): turn player ID.
    """
    def __init__(self, player_id: int):
        super().__init__()
        self.player_id = player_id
        self.depth = 0

    def __str__(self):
        return "%d:playselect:%d" % (self.depth, self.player_id)

    def process(self, game: Game):
        game.phase = Phase.PLAY
        assert game.turn.player_id == self.player_id
        if game.players[self.player_id].tmp_orbit >= 35:
            return []
        if game.players[self.player_id].pile[PileName.HAND].count <= 0:
            return []
        candidates = self._create_candidates(game)
        if game.choice == "":
            self.candidates = candidates
            return [self]
        else:
            self.candidates = []
        player_id, command, play_ids, uniq_ids = cparsell(game.choice)
        game.choice = ""
        assert command in ["play"]
        assert player_id == self.player_id
        assert len(play_ids) > 0
        if uniq_ids == []:
            uniq_ids = ids2uniq_ids(
                game.players[self.player_id].pile[PileName.HAND],
                play_ids, game
            )
        steps = []
        for play_id, uniq_id in zip(play_ids, uniq_ids):
            pass
        return steps

    def _create_candidates(self, game: Game):
        command = "play"
        candidates = []
        # only one play
        for card in game.players[self.player_id].pile[PileName.HAND].card_list:
            if [card.id] not in candidates:
                candidates.append([card.id])
        # same color
        same_color_list = {
            CardColor.RED: [],
            CardColor.BLUE: [],
            CardColor.GREEN: []
        }
        for color in [CardColor.RED, CardColor.BLUE, CardColor.GREEN]:
            for card in game.players[self.player_id].pile[
                    PileName.HAND].card_list:
                if color in get_colors(card.id, game):
                    same_color_list[color].append(card.id)
            perms = make_permutation(
                same_color_list[color], len(same_color_list[color]), True)
            for perm in perms:
                if len(perm) > 0 and perm not in candidates:
                    candidates.append(perm)
        # 3 colors
        color_3s = list(product(
            list(set(same_color_list[CardColor.RED])),
            list(set(same_color_list[CardColor.BLUE])),
            list(set(same_color_list[CardColor.GREEN]))
        ))
        for color_3 in color_3s:
            perms = make_permutation(color_3, 3, False)
            for perm in perms:
                if perm not in candidates:
                    candidates.append(perm)

        candidates = sorted(candidates)
        return ["%d:%s:%s" % (self.player_id, command, ",".join(
            [str(n) for n in cand])) for cand in candidates]
