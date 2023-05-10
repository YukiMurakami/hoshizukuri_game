from hoshizukuri_game.steps.base.kanketsusen_step import KanketsusenStep
from hoshizukuri_game.models.game import Game
from hoshizukuri_game.steps.common.draw_step import DrawStep


class TestKanketsusenStep():
    def test_str(self):
        step = KanketsusenStep(0, 0, 0)
        assert str(step) == "0:kanketsusen:0"

    def test_process_1(self, get_step_classes):
        game = Game()
        step = KanketsusenStep(0, 0, 0)
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [DrawStep]
        assert next_steps[0].count == 3
