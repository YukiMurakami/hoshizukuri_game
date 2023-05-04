"""
Steps for sequence of turn.
"""
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..models.game import Game
from ..models.turn import Turn
from .abstract_step import AbstractStep
from .common.play_step import PlayStep
from .common.draw_step import DrawStep
from .common.starflake_step import AddStarflakeStep
from .common.gain_step import GainStep
from ..models.turn import Phase
from ..models.pile import PileName
from ..models.card import CardColor
from ..models.cost import Cost
from ..models.card_condition import (
    CardCondition,
    get_match_card_ids
)
from ..utils.card_util import (
    get_colors, get_cost, ids2uniq_ids
)
from ..utils.other_util import (
    make_permutation
)
from ..utils.choice_util import (
    cparsei,
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
        game.created = False
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
        game.players[self.player_id].update_tmp_orbit(game)
        if game.players[self.player_id].tmp_orbit >= 35:
            return [OrbitAdvanceStep(self.player_id)]
        if game.players[self.player_id].pile[PileName.HAND].count <= 0:
            return [OrbitAdvanceStep(self.player_id)]
        if game.created:
            return [OrbitAdvanceStep(self.player_id)]
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
        return [
            PlayContinueStep(self.player_id),
            PlayStep(
                self.player_id, self.depth, play_ids, uniq_ids,
                from_pilename=PileName.HAND
            )
        ]

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


class PlayContinueStep(AbstractStep):
    """
    Play continue step.

    Args:
        player_id (int): turn player ID.
    """
    def __init__(self, player_id: int):
        super().__init__()
        self.player_id = player_id
        self.depth = 0

    def __str__(self):
        return "%d:playcontinue:%d" % (self.depth, self.player_id)

    def process(self, game: Game):
        # draw up to 4.
        hand_count = game.players[self.player_id].pile[PileName.HAND].count
        if hand_count < 4:
            return [
                PlaySelectStep(self.player_id),
                DrawStep(self.player_id, self.depth, 4 - hand_count)
            ]
        return [PlaySelectStep(self.player_id)]


class OrbitAdvanceStep(AbstractStep):
    """
    Orbit advance step.

    Args:
        player_id (int): turn player ID.
    """
    def __init__(self, player_id: int):
        super().__init__()
        self.player_id = player_id
        self.depth = 0

    def __str__(self):
        return "%d:orbitadvance:%d" % (self.depth, self.player_id)

    def process(self, game: Game):
        game.phase = Phase.ORBIT
        game.players[self.player_id].update_tmp_orbit(game)
        now_orbit = int(game.players[self.player_id].tmp_orbit)
        add_float = 0
        for player_id in range(len(game.players)):
            if player_id != self.player_id:
                enemy_orbit = int(game.players[player_id].orbit)
                if enemy_orbit == now_orbit:
                    add_float += 0.1
        next_orbit = now_orbit + add_float
        game.players[self.player_id].orbit = next_orbit
        return [GenerateSelectStep(self.player_id)]


class GenerateSelectStep(AbstractStep):
    """
    Select generate card.

    Args:
        player_id (int): turn player ID.
    """
    def __init__(self, player_id: int):
        super().__init__()
        self.player_id = player_id
        self.depth = 0

    def __str__(self):
        return "%d:generateselect:%d" % (self.depth, self.player_id)

    def process(self, game: Game):
        game.phase = Phase.GENERATE
        assert game.turn.player_id == self.player_id
        candidates = self._create_candidates(game)
        if game.choice == "":
            self.candidates = candidates
            return [self]
        else:
            self.candidates = []
        player_id, command, card_id = cparsei(game.choice)
        game.choice = ""
        assert command in ["generate"]
        assert player_id == self.player_id
        if card_id == 0:
            return []
        cost = get_cost(card_id, game)
        return [
            GainStep(
                self.player_id, self.depth, card_id,
                to_pilename=PileName.HAND),
            AddStarflakeStep(self.player_id, self.depth, cost.cost * -1)
        ]

    def _create_candidates(self, game: Game):
        generate_list = get_match_card_ids(
            game.supply,
            CardCondition(le_cost=Cost(game.starflake)),
            game, uniq_flag=True
        )
        generate_list += [0]  # pass
        return ["%d:generate:%d" % (self.player_id, n) for n in generate_list]
