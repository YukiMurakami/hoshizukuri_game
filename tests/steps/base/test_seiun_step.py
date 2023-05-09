from hoshizukuri_game.steps.base.seiun_step import SeiunStep


class TestSeiunStep():
    def test_str(self):
        step = SeiunStep(0, 0, 0)
        assert str(step) == "0:seiun:0"
