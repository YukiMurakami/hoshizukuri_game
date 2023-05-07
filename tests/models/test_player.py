from hoshizukuri_game.models.game import Game
from hoshizukuri_game.models.player import Player
from hoshizukuri_game.models.pile import Pile, PileName, PileType
from hoshizukuri_game.models.card import Card
from hoshizukuri_game.utils.card_util import get_card_id


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
            PileType.LISTLIST, card_list=[[
                Card(card_id=1, uniq_id=6),
                Card(card_id=1, uniq_id=7),
                Card(card_id=2, uniq_id=8)
            ]]
        )
        data = player.get_status_json()
        assert data == {
            "player_id": 1,
            "orbit": 0,
            "tmp_orbit": 0,
            "pile": {
                "deck": ["1-1", "1-2", "4-3"],
                "hand": ["4-4", "4-5"],
                "field": [["1-6", "1-7", "2-8"]]
            }
        }

    def test_update_tmp_orbit(self):
        player = Player(player_id=0)
        player.pile[PileName.FIELD] = Pile(
            PileType.LISTLIST, card_list=[
                [
                    Card(card_id=get_card_id("honow"), uniq_id=6),
                    Card(card_id=get_card_id("mizu"), uniq_id=7),
                    Card(card_id=get_card_id("daichi"), uniq_id=8)
                ],
                [
                    Card(card_id=get_card_id("hoshikuzu"), uniq_id=9)
                ],
                [
                    Card(card_id=get_card_id("mizu"), uniq_id=10),
                    Card(card_id=get_card_id("shinrin"), uniq_id=11)
                ],
                [],
                []
            ]
        )
        game = Game()
        game.set_players([player, Player(1)])
        player.orbit = 10
        player.update_tmp_orbit(game)
        assert player.tmp_orbit == 12
