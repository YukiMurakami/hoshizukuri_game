from hoshizukuri_game.hoshizukuri_game import HoshizukuriGame
from hoshizukuri_game.models.game import Game
from hoshizukuri_game.models.player import Player
from hoshizukuri_game.models.pile import Pile, PileName, PileType
from hoshizukuri_game.models.card import Card
from hoshizukuri_game.steps.abstract_step import AbstractStep


class TestHoshizukuriGame:
    def test_simulate(self):
        simulator = HoshizukuriGame()
        game = Game()
        game.set_players([Player(0), Player(1)])
        game.set_supply([n for n in range(8, 17)])
        game.set_initial_step()
        game.players[0].pile[PileName.HAND] = Pile(PileType.LIST, card_list=[
                Card(8, 0), Card(9, 0), Card(4, 0)
        ])
        candidates = simulator.simulate(game)
        assert candidates == []

    def test_simulate_nocandidates(self):
        simulator = HoshizukuriGame()
        game = Game()
        game.set_players([Player(0), Player(1)])
        game.set_supply([n for n in range(8, 17)])
        game.set_initial_step()
        game.stack = [AbstractStep()]
        candidates = simulator.simulate(game)
        assert candidates == []
