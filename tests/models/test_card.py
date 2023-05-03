from hoshizukuri_game.models.card import Card


class TestCard:
    def test_str(self):
        card = Card(card_id=1, uniq_id=1)
        assert str(card) == "1-1"
