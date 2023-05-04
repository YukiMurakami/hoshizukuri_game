"""
This module defines the Game model.
"""
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..steps.abstract_step import AbstractStep
    from .player import Player
from .pile import Pile, PileType
from ..steps.phase_steps import (
    TurnStartStep,
    PrepareFirstDeckStep,
)
from ..steps.common.draw_step import DrawStep
from ..steps.common.shuffle_step import ReshuffleStep
from .card import Card
from .turn import Phase, Turn, TurnType
from typing import Dict, List
import random
from ..utils.card_util import (
    get_card_id
)


class Game:
    """Game model class.

    Attributes:
        supply (Dict[int, Pile]): Supply piles. Key is pile_card_id.
        trash (Pile): Trash pile.
        players (List[Player]): List of players.
        coin (int): Now player's coin.
        turn (Turn): Now turn.
        phase (Phase): Now phase.
        stack (List[AbstractStep]): Steps that is going to be processed.
        choice (str): Now player's choice.
        start_deck (List[int]): The contents of start deck.
    """
    def __init__(self):
        self.supply: Dict[int, Pile] = {}
        self.trash: Pile = Pile(PileType.LIST, card_list=[])
        self.players: List[Player] = []
        self.coin: int = 0
        self.turn: Turn = Turn(1, 0, 0, TurnType.NORMAL)
        self.phase: Phase = Phase.TURN_START
        self.stack: List[AbstractStep] = []
        self.choice: str = ""
        self.start_deck: List[int] = [get_card_id(
            "stardust")] * 3 + [get_card_id("rock")] * 1 + [get_card_id(
                "satellite")] * 3
        self._uniq_id = 0
        self.result: List[dict] = []
        self.winner_id: int = -1

    def make_card(self, card_id: int):
        """
        Create new Card.

        Args:
            card_id (int): card ID.

        Returns:
            Card: created card.
        """
        self._uniq_id += 1
        card = Card(card_id, self._uniq_id)
        return card

    def set_players(self, players: List[Player]):
        """
        Set players before starting game.

        Args:
            players (List[Player]): The list of players.
        """
        self.players = list(players)
        for n, p in enumerate(self.players):
            p.player_id = n

    def set_supply(self, candidates: List[int]):
        """
        Set supplies before starting game.
        Call set_players before this.

        Args:
            candidates (List[int]): Choose supply cards from these at random.
        """
        cands = list(candidates)
        if len(cands) > 8:
            random.shuffle(cands)
            cands = sorted(cands[:8])

        common_supplys = [
            get_card_id("satellite"),
            get_card_id("planet"),
            get_card_id("star")
        ]

        for card_id in common_supplys + cands:
            count = self._get_start_supply_count(card_id, len(self.players))
            pile = Pile(PileType.NUMBER, card_id_and_count=[card_id, count])
            self.supply[pile.pile_card_id] = pile

    def set_initial_step(self):
        """
        Set initial step for starting game.
        Call this after set_players, set_supply.
        """
        self.stack.append(
            TurnStartStep(0, Turn(1, 0, 0, TurnType.NORMAL))
        )
        for n in reversed(range(len(self.players))):
            self.stack.append(DrawStep(n, 0, 4))
        for n in reversed(range(len(self.players))):
            self.stack.append(ReshuffleStep(n, 0))
        for n in reversed(range(len(self.players))):
            self.stack.append(PrepareFirstDeckStep(n))

    def _get_start_supply_count(self, card_id: int, player_num: int):
        dic = {
            "satellite": 12,
            "planet": 12,
            "star": 12
        }
        for k in dic:
            if get_card_id(k) == card_id:
                return dic[k]
        return 10

    def get_status_json(self):
        supply = {}
        for k, v in self.supply.items():
            supply[k] = str(v)
        data = {
            "num_player": len(self.players),
            "player_id": self.turn.player_id,
            "supply": supply,
            "trash": ["%d-%d" % (
                n.id, n.uniq_id) for n in self.trash.card_list],
            "turn": str(self.turn),
            "coin": self.coin,
            "phase": self.phase.value,
            "players": [n.get_status_json() for n in self.players],
        }
        return data

    def move_card(
            self, from_pile: Pile, to_pile: Pile, card_id: int = None,
            uniq_ids: List[int] = None, reverse: bool = False):
        """
        Move cards between piles.

        Args:
            from_pile (Pile): From pile.
            to_pile (Pile): To pile.
            card_id (int, Optional): move card ID.
            uniq_ids (List[int], Optional): move card unique IDs.
            reverse (bool, Optional): True is for push from the top of pile.

        Note:
            When PileType of from_pile is LIST, use uniq_ids.

            When PileType of from_pile is NUMBER, use card_ids.
            (For gain from supply)

            This push a card into last position of list.
            from = [1,2,3], to = [4,5,6] > to = [4,5,6,1,2,3]
            When reverse is True,
            from = [1,2,3], to = [4,5,6] > to = [3,2,1,4,5,6]
        Returns:
            List[int]: Unique IDs of moved cards.
        """
        assert card_id is not None or uniq_ids is not None
        assert card_id is None or uniq_ids is None
        moved_uniq_ids = []
        if from_pile.type == PileType.LIST:
            assert uniq_ids is not None
            for uniq_id in uniq_ids:
                index = from_pile.index(uniq_id=uniq_id)
                assert index != -1
                move_card = from_pile.card_list[index]
                moved_uniq_ids.append(move_card.uniq_id)
                from_pile.remove_at(index)
                if reverse:
                    to_pile.insert(move_card, 0)
                else:
                    to_pile.push(move_card)
        elif from_pile.type == PileType.LISTLIST:
            pass
        else:
            assert card_id is not None
            assert from_pile.pile_card_id == card_id
            assert from_pile.count > 0
            move_card = self.make_card(card_id)
            moved_uniq_ids.append(move_card.uniq_id)
            from_pile.remove_at(0)
            if reverse:
                to_pile.insert(move_card, 0)
            else:
                to_pile.push(move_card)
        return moved_uniq_ids
