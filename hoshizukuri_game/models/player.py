"""
This module defines the Player model.
"""
from .pile import Pile, PileName, PileType
from typing import Dict


class Player:
    """Card model class.

    Args:
        player_id (int): Player ID. 0 is the first player.

    Attributes:
        player_id (int): Player ID. 0 is the first player.
        orbit (float): Orbital progress of this.
        tmp_orbit (float): Orbital progress of this before Phase.ORBIT.
        pile (Dict[PileName, Pile]): Player piles.
        side_pile (Dict[str, SidePile]): Player side piles.
        card_pool (Pile): The card list that player has.

    """
    def __init__(self, player_id: int):
        self.player_id = player_id
        self.orbit: float = 0
        self.tmp_orbit: float = 0
        self.pile: Dict[PileName, Pile] = {
            PileName.HAND: Pile(PileType.LIST, card_list=[]),
            PileName.FIELD: Pile(PileType.LISTLIST, card_list=[]),
            PileName.DECK: Pile(PileType.LIST, card_list=[]),
            PileName.DISCARD: Pile(PileType.LIST, card_list=[]),
            PileName.LOOK: Pile(PileType.LIST, card_list=[]),
            PileName.REVEAL: Pile(PileType.LIST, card_list=[])
        }

    def get_status_json(self):
        piles = {}
        for pilename, pile in self.pile.items():
            if len(pile.card_list) > 0:
                piles[pilename.value] = [
                    str(n) for n in pile.card_list
                ]
                if pile.type == PileType.LISTLIST:
                    piles[pilename.value] = [[str(
                        n) for n in card_list] for card_list in pile.card_list
                    ]
        return {
            "player_id": self.player_id,
            "orbit": self.orbit,
            "tmp_orbit": self.tmp_orbit,
            "pile": piles
        }
