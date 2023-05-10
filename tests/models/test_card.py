from hoshizukuri_game.models.card import Card


class TestCard:
    def test_str(self):
        card = Card(card_id=1, uniq_id=1)
        assert str(card) == "1-1"

    def test_reset(self):
        card = Card(1, 1)
        card.starflake = 10
        card.create = True
        card.stop_orbit = True
        card.reset()
        assert card.starflake == 1
        assert card.create is False
        assert card.stop_orbit is False
