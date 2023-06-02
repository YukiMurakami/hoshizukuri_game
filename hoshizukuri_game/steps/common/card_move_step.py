"""
Abstract Steps for card move.
"""
from __future__ import annotations
from typing import TYPE_CHECKING, List, Callable
if TYPE_CHECKING:
    from ...models.game import Game
from ..abstract_step import AbstractStep
from ...models.pile import PileName, PileType
from ...models.card import Card
from ...models.card_condition import CardCondition, get_match_card_ids
from ...models.log import InvalidLogException, LogCondition
from ...utils.card_util import ids2cards, ids2uniq_ids
from ...utils.other_util import make_combination, make_permutation
from ...utils.choice_util import cparsell, is_included_candidates
from .shuffle_step import ReshuffleStep


def get_pile(pilename, game: Game, player_id):
    pile = None
    if pilename == PileName.SUPPLY:
        pile = game.supply
    elif pilename == PileName.TRASH:
        pile = game.trash
    else:
        pile = game.players[player_id].pile[pilename]
    return pile


class CardMoveStep(AbstractStep):
    """
    Card Move Step

    Args:
        player_id (int): Player ID.
        depth (int): Expected log hierarchy.
        from_pilename (PileName): move cards from this.
        to_pilename (PileName): move cards to this.
        card_ids (List[int], Optional): move card IDs.
        uniq_ids (List[int], Optional): move card unique IDS.
        count (int, Optional): the number of move cards.
        next_step_callback (Callable, Optional): After step, call this.
            This is for from deck, supply.
    """
    def __init__(
            self,
            player_id: int,
            depth: int,
            from_pilename: PileName,
            to_pilename: PileName,
            card_ids: List[int] = None,
            uniq_ids: List[int] = None,
            count: int = None,
            next_step_callback: Callable[
                [List[int], List[int], Game], List[AbstractStep]] = None):
        super().__init__()
        self.player_id = player_id
        self.depth = depth
        self.from_pilename = from_pilename
        self.to_pilename = to_pilename
        self.card_ids = card_ids
        self.uniq_ids = uniq_ids
        self.count = count
        self.next_step_callback = next_step_callback
        self.orbit_index = None
        if self.next_step_callback is None:
            self.next_step_callback = self._default_callback
        if from_pilename == PileName.DECK and count is None:
            raise Exception(
                "count is required for from DECK Pile."
            )
        if from_pilename != PileName.DECK and card_ids is None:
            raise Exception(
                "card_ids is required for from except for DECK Pile."
            )
        if next_step_callback is not None:
            if (from_pilename not in [PileName.DECK, PileName.SUPPLY] and
                    to_pilename is not PileName.FIELD):
                raise Exception(
                    "next_step_callback is used for from DECK Pile,"
                    "Supply or play cards."
                )

    def _default_callback(
            self, card_ids: List[int], uniq_ids: List[int], game: Game):
        return []

    def _after_process_callback(
            self, card_ids: List[int], uniq_ids: List[int], game: Game):
        pass

    def _get_step_string(self):
        return "card_move_step"

    def _get_from_deck_step_string(self, step):
        return "from_deck_step"

    def _get_log_condition(self):
        return None

    def __str__(self):
        return self._get_step_string()

    def process(self, game: Game):
        if self.from_pilename == PileName.DECK:
            deck_count = game.players[self.player_id].pile[PileName.DECK].count
            discard_count = game.players[self.player_id].pile[
                PileName.DISCARD].count
            if deck_count + discard_count < self.count:
                self.count = deck_count + discard_count
            if self.count <= 0:
                return self.next_step_callback([], [], game)
            if deck_count < self.count:
                return [
                    _ActualCardMoveFromDeckStep(
                        self.player_id, self.depth, self.count,
                        self.to_pilename,
                        self.next_step_callback,
                        self._get_from_deck_step_string,
                        self._after_process_callback,
                        self._get_log_condition),
                    ReshuffleStep(self.player_id, self.depth)]
            return [_ActualCardMoveFromDeckStep(
                self.player_id, self.depth, self.count, self.to_pilename,
                self.next_step_callback,
                self._get_from_deck_step_string,
                self._after_process_callback,
                self._get_log_condition)]
        from_pile = get_pile(
            self.from_pilename, game, self.player_id)
        to_pile = get_pile(
            self.to_pilename, game, self.player_id)
        if from_pile is not game.supply:
            if self.uniq_ids is None or len(self.uniq_ids) == 0:
                self.uniq_ids = ids2uniq_ids(from_pile, self.card_ids, game)
            if to_pile.type == PileType.LISTLIST and self.orbit_index is None:
                self.orbit_index = len(to_pile.card_list)
            game.move_card(
                from_pile,
                to_pile,
                uniq_ids=self.uniq_ids,
                orbit_index=self.orbit_index
            )
            self._after_process_callback(self.card_ids, self.uniq_ids, game)
        else:
            assert len(self.card_ids) == 1
            if (self.card_ids[0] not in from_pile or
                    from_pile[self.card_ids[0]].count <= 0):
                self._after_process_callback([], [], game)
                return self.next_step_callback([], [], game)
            self.uniq_ids = game.move_card(
                from_pile[self.card_ids[0]],
                to_pile, card_id=self.card_ids[0]
            )
            self._after_process_callback(self.card_ids, self.uniq_ids, game)
        log_condition = self._get_log_condition()
        if game.log_manager is not None and log_condition is not None:
            log = game.log_manager.check_nextlog_and_pop(log_condition)
            if log is None:
                raise InvalidLogException(game, log_condition)
        next_steps = self.next_step_callback(
            self.card_ids, self.uniq_ids, game)
        return next_steps


class _ActualCardMoveFromDeckStep(AbstractStep):
    def __init__(
            self, player_id, depth, count, to_pilename,
            next_step_callback, get_from_deck_step_string,
            after_process_callback, get_log_condition):
        super().__init__()
        self.player_id = player_id
        self.depth = depth
        self.count = count
        self.to_pilename = to_pilename
        self.next_step_callback = next_step_callback
        self.get_from_deck_step_string = get_from_deck_step_string
        self.card_list: List[Card] = []
        self.after_process_callback = after_process_callback
        self.get_log_condition = get_log_condition

    def __str__(self):
        return self.get_from_deck_step_string(self)

    def process(self, game: Game):
        self.card_list = list(game.players[
            self.player_id].pile[PileName.DECK].card_list[:self.count])
        log_condition = self.get_log_condition()
        if game.log_manager is not None and log_condition is not None:
            log = game.log_manager.check_nextlog_and_pop(log_condition)
            if log is None:
                raise InvalidLogException(game, log_condition)
            self.card_list = ids2cards(
                game.players[self.player_id].pile[PileName.DECK],
                log.card_ids, game
            )
        card_ids = [n.id for n in self.card_list]
        uniq_ids = [n.uniq_id for n in self.card_list]
        to_pile = get_pile(
            self.to_pilename, game, self.player_id)
        game.move_card(
            game.players[self.player_id].pile[PileName.DECK],
            to_pile,
            uniq_ids=uniq_ids
        )
        self.after_process_callback(card_ids, uniq_ids, game)
        return self.next_step_callback(card_ids, uniq_ids, game) + []


def select_process(
        create_step: Callable,
        game: Game, source_step: AbstractStep,
        choice_name: str, count: int,
        from_pilename: PileName,
        to_pilename: PileName,
        select_player_id: int = None,
        can_less: bool = False,
        can_pass: bool = False,
        card_condition: CardCondition = None,
        log_condition: LogCondition = None,
        next_step_callback: Callable[
            [List[int], List[int], Game], List[AbstractStep]] = None,
        previous_step_callback: Callable[
            [List[int], List[int], Game], List[AbstractStep]] = None
        ):
    """
    Common process of selecting cards.

    Args:
        create_step (Callable): create step function.
        game (Game): now game.
        source_step (AbstractStep): the step which uses this process.
        choice_name (str): choice command.
        count (int): the number of selected cards.
        from_pilename (PileName): move cards from this.
        to_pilename (PileName): move cards to this.
        select_player_id (int, Optional): select player ID.
            When this is None, source_step.player_id will be used.
        can_less (bool, Optional):
            True is for that the number of moves can be less.
        can_pass (bool, Optional): True is for that can move nothing.
            When can_less is True, can_pass is meaningless.
        card_condition (CardCondition): can move cards satisfy this.
        log_condition (LogCondition, Optional): the condition of moving log.
        next_step_callback (Callable, Optional): After step, call this.
        previous_step_callback (Callable, Optional): Before step, call this.
    Returns:
        List[AbstractStep]: the next steps.
    """
    if from_pilename == PileName.DECK:
        raise Exception(
            "Invalid from_pilename %s in select "
            "process." % from_pilename.value)
    if from_pilename == PileName.SUPPLY and count > 1:
        raise Exception(
            "Invalid count in select when from_pilename SUPPLY."
        )
    if select_player_id is None:
        select_player_id = source_step.player_id
    from_pile = get_pile(from_pilename, game, source_step.player_id)

    def _log2choice():
        if not game.log_manager.has_logs():
            return game.choice
        log = game.log_manager.get_nextlog(log_condition)
        if log is not None:
            card_ids = log.card_ids
            if log.card_ids is None:
                card_ids = [log.card_id]
            return "%d:%s:%s" % (
                select_player_id, choice_name, ",".join([
                    str(a) for a in card_ids])
            )
        if can_less is False and can_pass is False:
            raise InvalidLogException(game, log_condition)
        if count == 1:
            return "%d:%s:0" % (select_player_id, choice_name)
        return "%d:%s:" % (select_player_id, choice_name)

    def _create_candidates():
        card_list = []
        if from_pile is game.supply:
            for key, value in game.supply.items():
                if value.count > 0:
                    card_list.append(value.pile_card_id)
        else:
            card_list = from_pile.card_list
        if card_condition is not None:
            card_list = get_match_card_ids(
                from_pile, card_condition, game
            )
        candidates = make_combination(
            card_list, count, can_less
        )
        if to_pilename == PileName.DECK:
            candidates = make_permutation(
                card_list, count, can_less
            )
        if count > 0 and can_less is False and can_pass:
            candidates.append([])
        if count == 1:
            for i in range(len(candidates)):
                if candidates[i] == []:
                    candidates[i] = [0]
        return ["%d:%s:%s" % (select_player_id, choice_name, ",".join(
            [str(a) for a in n])) for n in candidates]

    def _default_callback(card_ids, uniq_ids, game):
        return []

    if next_step_callback is None:
        next_step_callback = _default_callback
    if previous_step_callback is None:
        previous_step_callback = _default_callback
    if count <= 0:
        return next_step_callback([], [], game) + previous_step_callback(
            [], [], game)
    candidates = _create_candidates()
    if len(candidates) == 0:
        return next_step_callback([], [], game) + previous_step_callback(
            [], [], game)
    if len(candidates) == 1:
        # auto
        card_ids = [
            int(n) for n in candidates[0].split(":")[2].split(",") if n != ""]
        if len(card_ids) <= 0 or card_ids[0] == 0:
            return next_step_callback(
                    [], [], game) + [] + previous_step_callback([], [], game)
        uniq_ids = []
        if from_pile is not game.supply:
            uniq_ids = ids2uniq_ids(
                from_pile, card_ids, game
            )
        return next_step_callback(card_ids, uniq_ids, game) + [
            create_step(
                source_step.player_id,
                source_step.depth,
                from_pilename, to_pilename,
                card_ids=card_ids,
                uniq_ids=uniq_ids,
            )
        ] + previous_step_callback(card_ids, uniq_ids, game)
    if game.log_manager is not None:
        game.choice = _log2choice()
        if game.choice != "" and game.choice not in candidates:
            if can_less:
                game.choice = ""
                return next_step_callback(
                    [], [], game) + previous_step_callback([], [], game)
            else:
                raise InvalidLogException(game, log_condition)
    if game.choice == "" or not is_included_candidates(
            game.choice, candidates):
        source_step.candidates = candidates
        return [source_step]
    else:
        source_step.candidates = []
    player_id, command, card_ids, uniq_ids = cparsell(game.choice)
    game.choice = ""
    assert command == choice_name
    assert player_id == select_player_id
    if len(card_ids) <= 0:
        return next_step_callback([], [], game) + [
            ] + previous_step_callback([], [], game)
    if len(uniq_ids) == 0 and from_pile is not game.supply:
        uniq_ids = ids2uniq_ids(
            from_pile, card_ids, game
        )
    return next_step_callback(card_ids, uniq_ids, game) + [
        create_step(
            source_step.player_id,
            source_step.depth,
            from_pilename, to_pilename,
            card_ids=card_ids,
            uniq_ids=uniq_ids,
        )
    ] + previous_step_callback(card_ids, uniq_ids, game)
