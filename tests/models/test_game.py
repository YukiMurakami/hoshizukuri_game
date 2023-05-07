from hoshizukuri_game.models.card import Card
from hoshizukuri_game.models.game import Game
from hoshizukuri_game.models.pile import Pile, PileName, PileType
from hoshizukuri_game.models.player import Player
from hoshizukuri_game.models.turn import Turn, TurnType
from hoshizukuri_game.utils.card_util import get_card_id
import random


class TestGame:
    def test_set_players(self):
        game = Game()
        players = [
            Player(1),
            Player(0)
        ]
        game.set_players(players=players)
        assert len(game.players) == 2
        assert game.players[0].player_id == 0

    def test_set_supply1(self):
        game = Game()
        players = [Player(1), Player(0)]
        game.set_players(players=players)
        game.set_supply([n for n in range(6, 14)])
        supply1 = game.supply[get_card_id("eisei")]
        assert supply1.count == 12
        assert supply1.pile_card_id == get_card_id("eisei")
        supply2 = game.supply[get_card_id("honow")]
        assert supply2.count == 10
        assert supply2.pile_card_id == get_card_id("honow")

    def test_set_supply2(self):
        random.seed(0)
        game = Game()
        players = [
            Player(1)
        ]
        game.set_players(players=players)
        game.set_supply([n for n in range(6, 16)])
        supply1 = game.supply[get_card_id("eisei")]
        assert supply1.count == 12
        assert supply1.pile_card_id == get_card_id("eisei")
        supply2 = game.supply[get_card_id("honow")]
        assert supply2.count == 10
        assert supply2.pile_card_id == get_card_id("honow")

    def test_set_initial_step(self):
        game = Game()
        game.set_players([Player(0), Player(1)])
        game.set_initial_step()
        assert len(game.stack) == 7

    def test_get_status_json(self):
        game = Game()
        game.set_players([Player(0)])
        game.set_supply([n for n in range(6, 14)])
        game.set_initial_step()
        status = game.get_status_json()
        assert status == {
            "num_player": 1,
            "starflake": 0,
            "player_id": 0,
            "players": [{
                "orbit": 0, "tmp_orbit": 0, "pile": {}, "player_id": 0}],
            "phase": "turn_start",
            "trash": [],
            "turn": "1:0:normal:0",
            "supply": {
                3: "{3:12}",
                4: "{4:12}",
                5: "{5:12}",
                6: "{6:10}",
                7: "{7:10}",
                8: "{8:10}",
                9: "{9:10}",
                10: "{10:10}",
                11: "{11:10}",
                12: "{12:10}",
                13: "{13:10}"
            },
            "created": False,
        }

    def test_make_card(self):
        game = Game()
        card1 = game.make_card(5)
        card2 = game.make_card(6)
        assert str(card1) == "5-1"
        assert str(card2) == "6-2"

    def test_move_card_1(self):
        game = Game()
        game.set_players([Player(0)])
        game.set_supply([n for n in range(6, 14)])
        game.players[0].pile[PileName.DECK] = Pile(
            PileType.LIST, card_list=[
                Card(1, 1), Card(1, 2), Card(4, 3)
            ]
        )
        deck = game.players[0].pile[PileName.DECK]
        game.players[0].pile[PileName.HAND] = Pile(
            PileType.LIST, card_list=[
                Card(2, 4), Card(2, 5), Card(5, 6)
            ]
        )
        hand = game.players[0].pile[PileName.HAND]
        game.move_card(deck, hand, uniq_ids=[1, 2])
        assert str(deck) == "[4-3]"
        assert str(hand) == "[2-4,2-5,5-6,1-1,1-2]"

    def test_move_card_2(self):
        game = Game()
        game.set_players([Player(0)])
        game.set_supply([n for n in range(6, 14)])
        game.players[0].pile[PileName.DECK] = Pile(
            PileType.LIST, card_list=[
                Card(1, 1), Card(1, 2), Card(4, 3)
            ]
        )
        deck = game.players[0].pile[PileName.DECK]
        game.players[0].pile[PileName.HAND] = Pile(
            PileType.LIST, card_list=[
                Card(2, 4), Card(2, 5), Card(5, 6)
            ]
        )
        hand = game.players[0].pile[PileName.HAND]
        game.move_card(deck, hand, uniq_ids=[1, 2], reverse=True)
        assert str(deck) == "[4-3]"
        assert str(hand) == "[1-2,1-1,2-4,2-5,5-6]"

    def test_move_card_3(self):
        game = Game()
        game.set_players([Player(0)])
        game.set_supply([n for n in range(6, 14)])
        game.players[0].pile[PileName.DISCARD] = Pile(
            PileType.LIST, card_list=[
                Card(1, 1), Card(1, 2), Card(4, 3)
            ]
        )
        discard = game.players[0].pile[PileName.DISCARD]
        game.move_card(game.supply[8], discard, card_id=8)
        assert str(game.supply[8]) == "{8:9}"
        assert str(discard) == "[1-1,1-2,4-3,8-1]"

    def test_move_card_4(self):
        game = Game()
        game.set_players([Player(0)])
        game.set_supply([n for n in range(6, 14)])
        game.players[0].pile[PileName.DISCARD] = Pile(
            PileType.LIST, card_list=[
                Card(1, 1), Card(1, 2), Card(4, 3)
            ]
        )
        discard = game.players[0].pile[PileName.DISCARD]
        game.move_card(game.supply[8], discard, card_id=8, reverse=True)
        assert str(game.supply[8]) == "{8:9}"
        assert str(discard) == "[8-1,1-1,1-2,4-3]"

    def test_move_card_5(self):
        game = Game()
        game.set_players([Player(0)])
        game.set_supply([n for n in range(6, 14)])
        game.players[0].pile[PileName.FIELD] = Pile(
            PileType.LISTLIST, card_list=[
                [Card(1, 1), Card(1, 2), Card(4, 3)],
                [Card(1, 4)]
            ]
        )
        field = game.players[0].pile[PileName.FIELD]
        discard = game.players[0].pile[PileName.DISCARD]
        game.move_card(field, discard, uniq_ids=[1, 2])
        assert str(field) == "[[4-3],[1-4]]"
        assert str(discard) == "[1-1,1-2]"

    def test_move_card_6(self):
        game = Game()
        game.set_players([Player(0)])
        game.set_supply([n for n in range(6, 14)])
        game.players[0].pile[PileName.FIELD] = Pile(
            PileType.LISTLIST, card_list=[
                [Card(1, 1), Card(1, 2), Card(4, 3)],
                [Card(1, 4)]
            ]
        )
        field = game.players[0].pile[PileName.FIELD]
        discard = game.players[0].pile[PileName.DISCARD]
        game.move_card(field, discard, uniq_ids=[1, 2], reverse=True)
        assert str(field) == "[[4-3],[1-4]]"
        assert str(discard) == "[1-2,1-1]"

    def test_move_card_7(self):
        game = Game()
        game.set_players([Player(0)])
        game.set_supply([n for n in range(6, 14)])
        game.players[0].pile[PileName.FIELD] = Pile(
            PileType.LISTLIST, card_list=[
                [Card(1, 1), Card(1, 2), Card(4, 3)],
                [Card(1, 4)]
            ]
        )
        field = game.players[0].pile[PileName.FIELD]
        game.move_card(
            game.supply[3],
            field,
            card_id=3, orbit_index=1)
        assert str(game.supply[3]) == "{3:11}"
        assert str(field) == "[[1-1,1-2,4-3],[1-4,3-1]]"

    def test_update_starflake(self):
        game = Game()
        game.set_players([Player(0)])
        game.set_supply([n for n in range(6, 14)])
        game.players[0].pile[PileName.FIELD] = Pile(
            PileType.LISTLIST, card_list=[
                [Card(1, 1), Card(1, 2), Card(4, 3)],
                [Card(1, 4)]
            ]
        )
        game.starflake = 0
        game.turn = Turn(5, 5, 0, TurnType.NORMAL)
        game.update_starflake()
        assert game.starflake == 4
