from hoshizukuri_game.models.player import Player
from hoshizukuri_game.models.pile import Pile, PileName, PileType
from hoshizukuri_game.models.card import Card


class TestPlayer:
    def test_get_status_json(self):
        player = Player(player_id=1)
        player.pile[PileName.DECK] = Pile(
            PileType.LIST, card_list=[
                Card(card_id=1, uniq_id=1),
                Card(card_id=1, uniq_id=2),
                Card(card_id=4, uniq_id=3)
            ]
        )
        player.pile[PileName.HAND] = Pile(
            PileType.LIST, card_list=[
                Card(card_id=4, uniq_id=4),
                Card(card_id=4, uniq_id=5)
            ]
        )
        player.pile[PileName.FIELD] = Pile(
            PileType.LIST, card_list=[
                Card(card_id=1, uniq_id=6),
                Card(card_id=1, uniq_id=7),
                Card(card_id=2, uniq_id=8)
            ]
        )
        data = player.get_status_json()
        assert data == {
            "player_id": 1,
            "orbit": 0,
            "tmp_orbit": 0,
            "pile": {
                "deck": ["1-1", "1-2", "4-3"],
                "hand": ["4-4", "4-5"],
                "field": ["1-6", "1-7", "2-8"]
            }
        }
