"""
Steps for sequence of turn.
"""
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..models.game import Game
from ..models.turn import Turn, TurnType
from ..models.activate import ActivatePlaysetEnd, TargetActivate
from .abstract_step import AbstractStep
from .common.play_step import PlayStep
from .common.draw_step import DrawStep
from .common.starflake_step import AddStarflakeStep
from .common.gain_step import GainStep
from .common.discard_step import DiscardStep, discard_select_process
from .common.call_trigger_step import CallTriggerStep
from ..models.turn import Phase
from ..models.pile import PileName, PileType
from ..models.cost import Cost
from ..models.log import InvalidLogException, LogCondition, Command
from ..models.card_condition import (
    CardCondition,
    get_match_card_ids
)
from ..utils.card_util import (
    get_colors, get_cost, ids2uniq_ids, CardColor
)
from ..utils.other_util import (
    make_combination, call_choice_callback
)
from ..utils.choice_util import (
    cparsei,
    cparseii,
    cparsell,
    is_included_candidates
)
from ..utils.kingdom_step_util import get_kingdom_steps
from itertools import product


FINISH_ORBIT = 35


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
        if game.log_manager is not None:
            log_condition = LogCondition(
                command=Command.TURN_START, player_id=self.player_id,
                depth=self.depth
            )
            log = game.log_manager.check_nextlog_and_pop(log_condition)
            if log is None:
                raise InvalidLogException(game, log_condition)
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
        if game.log_manager is not None:
            game.start_deck = []
            for _ in range(100):
                log = game.log_manager.check_nextlog_and_pop(
                    LogCondition(
                        Command.START_WITH, self.player_id, self.depth
                    ))
                if log is not None:
                    game.start_deck += log.card_ids
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
        if game.players[self.player_id].tmp_orbit >= FINISH_ORBIT:
            return [OrbitAdvanceStep(self.player_id)]
        if game.players[self.player_id].pile[PileName.HAND].count <= 0:
            return [OrbitAdvanceStep(self.player_id)]
        if game.created:
            return [OrbitAdvanceStep(self.player_id)]
        candidates = self._create_candidates(game)
        if game.log_manager is not None:
            game.choice = self._log2choice(game)
            call_choice_callback(game, candidates, game.choice, self)
        if game.choice == "" or not is_included_candidates(
                game.choice, candidates):
            self.candidates = candidates
            return [self]
        else:
            self.candidates = []
        player_id, command, play_ids, uniq_ids = cparsell(game.choice)
        game.choice = ""
        assert command in ["playset"]
        assert player_id == self.player_id
        assert len(play_ids) > 0
        if uniq_ids == []:
            uniq_ids = ids2uniq_ids(
                game.players[self.player_id].pile[PileName.HAND],
                play_ids, game
            )
        return [
            PlayCardSelectStep(self.player_id),
            PlayStep(
                self.player_id, self.depth, play_ids, uniq_ids,
                from_pilename=PileName.HAND, process_effect=False
            )
        ]

    def _create_candidates(self, game: Game):
        command = "playset"
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
            perms = make_combination(
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
            perm = sorted(list(color_3))
            if perm not in candidates:
                candidates.append(perm)

        candidates = sorted(candidates)
        return ["%d:%s:%s" % (self.player_id, command, ",".join(
            [str(n) for n in cand])) for cand in candidates]

    def _log2choice(self, game: Game):
        if not game.log_manager.has_logs():
            return game.choice
        log_condition = LogCondition(
            Command.PLAY, self.player_id, depth=self.depth)
        log = game.log_manager.get_nextlog(
            log_condition
        )
        if log is None:
            raise InvalidLogException(game, log_condition)
        return "%d:playset:%s" % (
            self.player_id, ",".join([str(n) for n in log.card_ids])
        )


class PlayCardSelectStep(AbstractStep):
    """
    Select card to play from card set in field.

    Args:
        player_id (int): turn player ID.
    """
    def __init__(self, player_id: int):
        super().__init__()
        self.player_id = player_id
        self.depth = 0
        self.played_ids_and_uniq_ids = []

    def __str__(self):
        return "%d:playcardselect:%d" % (self.depth, self.player_id)

    def process(self, game: Game):
        candidates = self._create_candidates(game)
        if len(candidates) == 0:
            return [PlaysetEndStep(self.player_id)]
        if len(candidates) == 1:
            game.choice = candidates[0]
        if game.log_manager is not None:
            game.choice = self._log2choice(game)
            call_choice_callback(game, candidates, game.choice, self)
        if game.choice == "" or not is_included_candidates(
                game.choice, candidates):
            self.candidates = candidates
            return [self]
        else:
            self.candidates = []
        player_id, command, play_id, uniq_id = cparseii(game.choice)
        game.choice = ""
        assert command in ["play"]
        assert player_id == self.player_id
        if uniq_id == -1:
            for card in game.players[self.player_id].pile[
                    PileName.FIELD].card_list[-1]:
                if (card.id == play_id and
                        [play_id,
                            card.uniq_id] not in self.played_ids_and_uniq_ids):
                    uniq_id = card.uniq_id
        self.played_ids_and_uniq_ids.append([play_id, uniq_id])
        return [
            self,
            PlayStep(
                self.player_id, self.depth, [play_id], [uniq_id],
                from_pilename=PileName.FIELD, process_effect=True
            )
        ]

    def _create_candidates(self, game: Game):
        rest_id_uniq_ids = [[n.id, n.uniq_id] for n in game.players[
            self.player_id].pile[PileName.FIELD].card_list[-1]]
        for id_uniq_id in self.played_ids_and_uniq_ids:
            rest_id_uniq_ids.remove(id_uniq_id)
        return ["%d:play:%d" % (
            self.player_id, n[0]) for n in rest_id_uniq_ids]

    def _log2choice(self, game: Game):
        if not game.log_manager.has_logs():
            return game.choice
        log_condition = LogCondition(
            Command.RESOLVE_EFFECT, self.player_id, depth=self.depth)
        log = game.log_manager.get_nextlog(
            log_condition
        )
        if log is None:
            raise InvalidLogException(game, log_condition)
        return "%d:play:%d" % (
            self.player_id, log.card_id
        )


class PlaysetEndStep(AbstractStep):
    """
    Play set end step.

    Args:
        player_id (int): turn player ID.
    """
    def __init__(self, player_id: int):
        super().__init__()
        self.player_id = player_id
        self.depth = 0

    def __str__(self):
        return "%d:playsetend:%d" % (self.depth, self.player_id)

    def process(self, game: Game):
        trigger_steps = [CallTriggerStep(
            self.player_id, self.depth, [TargetActivate(
                ActivatePlaysetEnd, player_id=self.player_id
            )]
        )]
        return [PlayContinueStep(self.player_id)] + trigger_steps


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
        # check created
        for card in game.players[self.player_id].pile[
                PileName.FIELD].card_list[-1]:
            if card.create:
                game.created = True
                break
        game.players[self.player_id].update_tmp_orbit(game)
        if game.players[self.player_id].tmp_orbit >= FINISH_ORBIT:
            return [OrbitAdvanceStep(self.player_id)]
        if game.created:
            return [OrbitAdvanceStep(self.player_id)]
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

    def _advance(self, game: Game, next_orbit: float, e_player_id: int):
        after = int(next_orbit)
        before = int(game.players[e_player_id].orbit)
        if game.log_manager is not None:
            log_condition = LogCondition(
                Command.CHANGE_ORBIT, e_player_id, self.depth,
                numbers=[before, after]
            )
            log = game.log_manager.check_nextlog_and_pop(log_condition)
            if log is None:
                raise InvalidLogException(game, log_condition)
        next_orbit = int(next_orbit)
        add_float = 0
        for player_id in range(len(game.players)):
            if player_id != e_player_id:
                enemy_orbit = int(game.players[player_id].orbit)
                if enemy_orbit == next_orbit:
                    add_float += 0.1
        game.players[e_player_id].orbit = next_orbit + add_float

    def process(self, game: Game):
        game.phase = Phase.ORBIT
        game.players[self.player_id].update_tmp_orbit(game)
        self._advance(
            game, game.players[self.player_id].tmp_orbit, self.player_id)
        # When orbit is 35, increase the other player's arbit.
        if int(game.players[self.player_id].orbit) == FINISH_ORBIT:
            moves = []
            for player_id in range(len(game.players)):
                if player_id != self.player_id:
                    if game.players[player_id].orbit < FINISH_ORBIT:
                        moves.append([
                            int(game.players[player_id].orbit),
                            game.players[player_id].orbit - int(
                                game.players[player_id].orbit),
                            player_id])
            moves = sorted(
                moves, key=lambda x: (x[0], x[1] * -1), reverse=True)
            for player_id in [n[2] for n in moves]:
                self._advance(
                    game, game.players[player_id].orbit + 1, player_id
                )
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
        game.update_starflake()
        assert game.turn.player_id == self.player_id
        candidates = self._create_candidates(game)
        if game.log_manager is not None:
            game.choice = self._log2choice(game)
            call_choice_callback(game, candidates, game.choice, self)
        if game.choice == "" or not is_included_candidates(
                game.choice, candidates):
            self.candidates = candidates
            return [self]
        else:
            self.candidates = []
        player_id, command, card_id = cparsei(game.choice)
        game.choice = ""
        assert command in ["generate"]
        assert player_id == self.player_id
        if card_id is None:
            return [CleanupStep(self.player_id)]
        cost = get_cost(card_id, game)
        return [
            CleanupStep(self.player_id),
            GainStep(
                self.player_id, self.depth, card_id,
                to_pilename=PileName.HAND, create=True),
            AddStarflakeStep(self.player_id, self.depth, cost.cost * -1)
        ]

    def _create_candidates(self, game: Game):
        generate_list = get_match_card_ids(
            game.supply,
            CardCondition(le_cost=Cost(game.starflake)),
            game, uniq_flag=True
        )
        return ["%d:generate:%d" % (
            self.player_id, n) for n in generate_list] + [
            "%d:generate:" % self.player_id
        ]

    def _log2choice(self, game: Game):
        if not game.log_manager.has_logs():
            return game.choice
        log_condition = LogCondition(
            Command.CREATE, self.player_id, depth=self.depth)
        log = game.log_manager.get_nextlog(
            log_condition
        )
        if log is None:
            return "%d:generate:" % self.player_id
        return "%d:generate:%d" % (
            self.player_id, log.card_id
        )


class CleanupStep(AbstractStep):
    """
    cleanup step.

    Args:
        player_id (int): turn player ID.
    """
    def __init__(self, player_id: int):
        super().__init__()
        self.player_id = player_id
        self.depth = 0

    def __str__(self):
        return "%d:cleanup:%d" % (self.depth, self.player_id)

    def process(self, game: Game):
        game.phase = Phase.CLEAN_UP
        steps = []
        card_ids = []
        uniq_ids = []
        for card_list in reversed(game.players[
                self.player_id].pile[PileName.FIELD].card_list):
            for card in card_list:
                card_ids.append(card.id)
                uniq_ids.append(card.uniq_id)
        if len(card_ids) > 0:
            steps = [
                DiscardStep(
                    self.player_id, self.depth,
                    card_ids=card_ids, uniq_ids=uniq_ids,
                    from_pilename=PileName.FIELD
                )
            ]
        # draw up to 4 or discard down to 4.
        hand_count = game.players[self.player_id].pile[PileName.HAND].count
        draw_steps = []
        if hand_count < 4:
            draw_steps = [DrawStep(
                self.player_id, self.depth, 4 - hand_count)]
        elif hand_count > 4:
            draw_steps = [CleanupDiscardHandStep(self.player_id)]
        # reset all cards
        for player_id in range(len(game.players)):
            for v in game.players[player_id].pile.values():
                if v.type == PileType.LIST:
                    for c in v.card_list:
                        c.reset()
                elif v.type == PileType.LISTLIST:
                    for cl in v.card_list:
                        for c in cl:
                            c.reset()
        return [UpdateTurnStep(self.player_id)] + draw_steps + steps


class CleanupDiscardHandStep(AbstractStep):
    """
    cleanup discard hand step.

    Args:
        player_id (int): turn player ID.
    """
    def __init__(self, player_id: int):
        super().__init__()
        self.player_id = player_id
        self.depth = 0

    def __str__(self):
        return "%d:cleanupdiscardhand:%d" % (self.depth, self.player_id)

    def process(self, game: Game):
        hands = game.players[self.player_id].pile[PileName.HAND].card_list
        assert len(hands) >= 5
        return discard_select_process(
            game, self, "cleanupdiscard", len(hands) - 4
        )


class UpdateTurnStep(AbstractStep):
    """
    Update turn step.

    Args:
        player_id (int): now turn player ID.
    """
    def __init__(self, player_id: int):
        super().__init__()
        self.player_id = player_id
        self.depth = 0

    def __str__(self):
        return "%d:updateturn:%d" % (self.depth, self.player_id)

    def process(self, game: Game):
        game.phase = Phase.TURN_END
        next_turn = game.turn.turn + 1
        next_uniq_turn = game.turn.uniq_turn + 1
        # next player is who has hewest orbit.
        next_player_id = 0
        min_orbit = 10000
        for player_id in range(len(game.players)):
            orbit = game.players[player_id].orbit
            if min_orbit > orbit:
                min_orbit = orbit
                next_player_id = player_id
        if min_orbit >= FINISH_ORBIT:
            # finish
            return [GameFinishStep()]
        turn = Turn(
            next_turn, next_uniq_turn, next_player_id, TurnType.NORMAL)
        return [TurnStartStep(next_player_id, turn)]


class GameFinishStep(AbstractStep):
    """
    game finish step.
    """
    def __init__(self):
        super().__init__()
        self.depth = 0

    def __str__(self):
        return "%d:gamefinish:" % (self.depth)

    def process(self, game: Game):
        game.phase = Phase.FINISH
        # calc points
        scores = []
        cards = []
        for player_id in range(len(game.players)):
            sum_point = 0
            cards.append([])
            for name, pile in game.players[player_id].pile.items():
                if pile.type == PileType.LIST:
                    for card in pile.card_list:
                        cards[-1].append(card.id)
                        step = get_kingdom_steps(0, 0, card.id, card.uniq_id)
                        point = step.get_victory(game)
                        sum_point += point
                elif pile.type == PileType.LISTLIST:
                    for cardlist in pile.card_list:
                        for card in cardlist:
                            cards[-1].append(card.id)
                            step = get_kingdom_steps(
                                0, 0, card.id, card.uniq_id)
                            point = step.get_victory(game)
                            sum_point += point
            scores.append(
                [player_id, sum_point, game.players[player_id].orbit])
        scores = sorted(scores, key=lambda x: (x[1], -x[2]), reverse=True)
        sort_player_ids = [n[0] for n in scores]

        game.result = []
        for player_id in range(len(game.players)):
            index = sort_player_ids.index(player_id)
            game.result.append(
                {
                    "point": scores[index][1],
                    "rank": index + 1,
                    "player_id": player_id,
                    "cards": sorted(cards[player_id])
                 }
            )
        game.winner_id = scores[0][0]
        return []
