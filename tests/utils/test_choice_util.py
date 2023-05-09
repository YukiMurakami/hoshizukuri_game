from hoshizukuri_game.utils.choice_util import (
    cparseii,
    cparsei,
    cparsell,
    cparses,
    is_included_candidates,
)


class TestChoiceUtil:
    def test_cparseii_1(self):
        player_id, command, card_id, uniq_id = cparseii("1:play:8-2")
        assert player_id == 1
        assert command == "play"
        assert card_id == 8
        assert uniq_id == 2

    def test_cparseii_2(self):
        player_id, command, card_id, uniq_id = cparseii("1:play:8")
        assert player_id == 1
        assert command == "play"
        assert card_id == 8
        assert uniq_id == -1

    def test_cparsei(self):
        player_id, command, card_id = cparsei("1:play:8")
        assert player_id == 1
        assert command == "play"
        assert card_id == 8

    def test_cparsell_1(self):
        player_id, command, card_ids, uniq_ids = cparsell("1:play:1-1,2-4")
        assert player_id == 1
        assert command == "play"
        assert card_ids == [1, 2]
        assert uniq_ids == [1, 4]

    def test_cparsell_2(self):
        player_id, command, card_ids, uniq_ids = cparsell("1:play:")
        assert player_id == 1
        assert command == "play"
        assert card_ids == []
        assert uniq_ids == []

    def test_cparsell_3(self):
        player_id, command, card_ids, uniq_ids = cparsell("1:play:1-1,2")
        assert player_id == 1
        assert command == "play"
        assert card_ids == [1, 2]
        assert uniq_ids == []

    def test_cparsell_4(self):
        player_id, command, card_ids, uniq_ids = cparsell("1:play:0")
        assert player_id == 1
        assert command == "play"
        assert card_ids == []
        assert uniq_ids == []

    def test_cparses_1(self):
        player_id, command, param = cparses("1:play:param1")
        assert player_id == 1
        assert command == "play"
        assert param == "param1"

    def test_cparses_2(self):
        player_id, command, param = cparses(
            "1:triggerselect:moatreaction:23-1")
        assert player_id == 1
        assert command == "triggerselect"
        assert param == "moatreaction:23-1"

    def test_is_included_candidates(self):
        assert is_included_candidates(
            "0:playset:1-1,2-3,3-4",
            [
                "0:playset:1,2,3"
            ]
        )
        assert is_included_candidates(
            "0:playset:6-8,7-11",
            [
                "0:playset:6,7"
            ]
        )
