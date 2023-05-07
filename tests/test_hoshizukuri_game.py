from hoshizukuri_game.hoshizukuri_game import HoshizukuriGame
from hoshizukuri_game.models.game import Game
from hoshizukuri_game.models.player import Player
from hoshizukuri_game.steps.abstract_step import AbstractStep
import random


class TestHoshizukuriGame:
    def test_simulate(self, is_equal_candidates):
        random.seed(0)
        simulator = HoshizukuriGame()
        game = Game()
        game.set_players([Player(0), Player(1)])
        game.set_supply([n for n in range(8, 17)])
        game.set_initial_step()
        candidates = simulator.simulate(game)
        assert is_equal_candidates(
            candidates,
            [
                '0:playset:1#0',
                '0:playset:3#0'
            ]
        )

    def test_simulate_nocandidates(self):
        simulator = HoshizukuriGame()
        game = Game()
        game.set_players([Player(0), Player(1)])
        game.set_supply([n for n in range(8, 17)])
        game.set_initial_step()
        game.stack = [AbstractStep()]
        candidates = simulator.simulate(game)
        assert candidates == []
