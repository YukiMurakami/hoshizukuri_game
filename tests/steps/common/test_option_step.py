from hoshizukuri_game.models.game import Game
from hoshizukuri_game.steps.abstract_step import AbstractStep
from hoshizukuri_game.steps.common.draw_step import DrawStep
from hoshizukuri_game.steps.common.gain_step import GainStep
from hoshizukuri_game.steps.common.option_step import option_select_process


class TestOptionSelectProcess():
    def callback_a(self, game, params):
        return [GainStep(0, 0, 2)]

    def callback_b(self, game, params):
        return [DrawStep(0, 1)]

    def create_candidates(self, game, params):
        return ["0:select:option_a", "0:select:option_b"]

    def create_one_candidates(self, game, params):
        return ["0:select:option_a"]

    def test_option_select_process(self, get_step_classes):
        game = Game()
        step = AbstractStep()
        step._create_candidates = self.create_candidates
        game.choice = "0:select:option_a"
        next_steps = option_select_process(
            game, step, {
                "0:select:option_a": self.callback_a,
                "0:select:option_b": self.callback_b
            }
        )
        assert get_step_classes(next_steps) == [GainStep]

    def test_option_select_process_one_candidate(self, get_step_classes):
        game = Game()
        step = AbstractStep()
        step._create_candidates = self.create_one_candidates
        next_steps = option_select_process(
            game, step, {
                "0:select:option_a": self.callback_a,
                "0:select:option_b": self.callback_b
            }
        )
        assert get_step_classes(next_steps) == [GainStep]
