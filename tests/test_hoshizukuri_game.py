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
        result = simulator.simulate(game)
        assert is_equal_candidates(
            result["candidates"],
            [
                '0:playset:1#0',
                '0:playset:3#0'
            ]
        )
        assert result["steps"] == [
            '0:preparefirstdeck:0',
            '0:preparefirstdeck:1',
            '0:reshuffle:0:3-7,1-1,3-6,1-2,3-5,1-3,2-4',
            '0:reshuffle:1:3-13,3-12,2-11,3-14,1-8,1-9,1-10',
            '0:pre-draw:0:4',
            '0:draw:0:3-7,1-1,3-6,1-2',
            '0:pre-draw:1:4',
            '0:draw:1:3-13,3-12,2-11,3-14',
            '0:turnstart:1:0:normal:0',
            '0:playselect:0'
        ]

    def test_simulate_nocandidates(self):
        simulator = HoshizukuriGame()
        game = Game()
        game.set_players([Player(0), Player(1)])
        game.set_supply([n for n in range(8, 17)])
        game.set_initial_step()
        game.stack = [AbstractStep()]
        result = simulator.simulate(game)
        assert result["candidates"] == []
        assert result["steps"] == [
            "0:abstract"
        ]
