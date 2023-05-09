from hoshizukuri_game.steps.base.genshisei_step import GenshiseiStep


class TestGenshiseiStep():
    def test_str(self):
        step = GenshiseiStep(0, 0, 0)
        assert str(step) == "0:genshisei:0"
