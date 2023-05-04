from hoshizukuri_game.models.turn import TurnType, Turn


class TestTurn:
    def test_str(self):
        turn = Turn(1, 1, 0, TurnType.NORMAL)
        assert str(turn) == "1:0:normal:0"
