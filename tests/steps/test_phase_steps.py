from hoshizukuri_game.models.card import Card
from hoshizukuri_game.models.pile import Pile, PileName, PileType
from hoshizukuri_game.steps.common.discard_step import DiscardStep
from hoshizukuri_game.steps.common.draw_step import DrawStep
from hoshizukuri_game.steps.common.gain_step import GainStep
from hoshizukuri_game.steps.common.play_step import PlayStep
from hoshizukuri_game.steps.common.starflake_step import AddStarflakeStep
from hoshizukuri_game.steps.phase_steps import (
    GameFinishStep,
    OrbitAdvanceStep,
    PlayContinueStep,
    PlayCardSelectStep,
    TurnStartStep,
    PrepareFirstDeckStep,
    PlaySelectStep,
    GenerateSelectStep,
    CleanupStep,
    CleanupDiscardHandStep,
    UpdateTurnStep,
)
from hoshizukuri_game.models.turn import Phase, Turn, TurnType
from hoshizukuri_game.models.game import Game
from hoshizukuri_game.models.player import Player
from hoshizukuri_game.utils.card_util import get_card_id


class TestTurnStartStep:
    def test_str(self):
        step = TurnStartStep(0, Turn(0, 0, 0, TurnType.NORMAL))
        assert str(step) == "0:turnstart:0:0:normal:0"

    def test_process(self, get_step_classes):
        step = TurnStartStep(0, Turn(1, 0, 0, TurnType.NORMAL))
        game = Game()
        game.set_players([Player(0), Player(1)])
        game.set_supply([])
        game.turn = Turn(0, -1, 1, TurnType.NORMAL)
        next_steps = step.process(game)
        assert game.turn.turn == 1
        assert game.turn.player_id == 0
        assert game.turn.turn_type == TurnType.NORMAL
        assert get_step_classes(next_steps) == [PlaySelectStep]


class TestPrepareFirstDeckStep:
    def test_str(self):
        step = PrepareFirstDeckStep(0)
        assert str(step) == "0:preparefirstdeck:0"

    def get_base_game(self):
        game = Game()
        game.set_players([Player(0)])
        game.set_supply([n for n in range(6, 14)])
        game.turn = Turn(1, 0, 0, TurnType.NORMAL)
        return game

    def test_process(self):
        step = PrepareFirstDeckStep(0)
        game = self.get_base_game()
        step.process(game)
        assert game.players[0].pile[PileName.DISCARD].count == 7


class TestPlaySelectStep:
    def test_str(self):
        step = PlaySelectStep(0)
        assert str(step) == "0:playselect:0"

    def get_game(self, hand_list):
        game = Game()
        game.set_players([Player(0), Player(1)])
        game.set_supply([n for n in range(8, 17)])
        game.turn = Turn(1, 0, 0, TurnType.NORMAL)
        game.players[0].pile[PileName.HAND] = Pile(
            PileType.LIST, card_list=hand_list)
        return game

    def test_process_normal(self, get_step_classes, is_equal_candidates):
        step = PlaySelectStep(0)
        game = self.get_game([
            Card(get_card_id("honow"), 0),
            Card(get_card_id("funka"), 1),
            Card(get_card_id("hoshikuzu"), 2),
        ])
        game.choice = ""
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [
            PlaySelectStep
        ]
        assert is_equal_candidates(
            step.get_candidates(game),
            [
                "0:playset:%d#0" % get_card_id("hoshikuzu"),
                "0:playset:%d#0" % get_card_id("funka"),
                "0:playset:%d#0" % get_card_id("honow"),
                "0:playset:%d,%d#0" % (
                    get_card_id("honow"), get_card_id("funka"))
            ]
        )

    def test_process_3_colors(self, get_step_classes, is_equal_candidates):
        step = PlaySelectStep(0)
        game = self.get_game([
            Card(get_card_id("honow"), 0),
            Card(get_card_id("funka"), 1),
            Card(get_card_id("shinrin"), 2),
            Card(get_card_id("kori"), 3),
        ])
        game.choice = ""
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [
            PlaySelectStep
        ]
        R1 = get_card_id("honow")
        R2 = get_card_id("funka")
        B = get_card_id("kori")
        G = get_card_id("shinrin")
        assert is_equal_candidates(
            step.get_candidates(game),
            [
                "0:playset:%d#0" % R1,
                "0:playset:%d#0" % R2,
                "0:playset:%d#0" % G,
                "0:playset:%d#0" % B,
                "0:playset:%d,%d#0" % (R1, R2),
                "0:playset:%d,%d,%d#0" % (R1, G, B),
                "0:playset:%d,%d,%d#0" % (G, B, R2)
            ]
        )

    def test_process_play(self, get_step_classes):
        step = PlaySelectStep(0)
        game = self.get_game([
            Card(get_card_id("honow"), 0),
            Card(get_card_id("funka"), 1),
            Card(get_card_id("hoshikuzu"), 2),
        ])
        game.choice = "0:playset:%d" % get_card_id("honow")
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [
            PlayCardSelectStep,
            PlayStep
        ]

    def test_process_no_hand(self, get_step_classes):
        step = PlaySelectStep(0)
        game = self.get_game([])
        game.choice = ""
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [OrbitAdvanceStep]

    def test_process_over_orbit(self, get_step_classes):
        step = PlaySelectStep(0)
        game = self.get_game([
            Card(get_card_id("honow"), 0),
            Card(get_card_id("funka"), 1),
            Card(get_card_id("hoshikuzu"), 2),
        ])
        game.players[0].orbit = 35
        game.choice = "0:playset:9"
        game.players[0].tmp_orbit = 35
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [OrbitAdvanceStep]

    def test_process_created(self, get_step_classes):
        step = PlaySelectStep(0)
        game = self.get_game([
            Card(get_card_id("honow"), 0),
            Card(get_card_id("funka"), 1),
            Card(get_card_id("hoshikuzu"), 2),
        ])
        game.created = True
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [OrbitAdvanceStep]


class TestPlayCardSelectStep:
    def test_str(self):
        step = PlayCardSelectStep(0)
        assert str(step) == "0:playcardselect:0"

    def get_game(self, field_list):
        game = Game()
        game.set_players([Player(0), Player(1)])
        game.set_supply([n for n in range(8, 17)])
        game.turn = Turn(1, 0, 0, TurnType.NORMAL)
        game.players[0].pile[PileName.FIELD] = Pile(
            PileType.LISTLIST, card_list=field_list)
        return game

    def test_process_1(self, get_step_classes, is_equal_candidates):
        step = PlayCardSelectStep(0)
        game = self.get_game([[
            Card(get_card_id("honow"), 0),
            Card(get_card_id("funka"), 1),
            Card(get_card_id("hoshikuzu"), 2),
        ]])
        game.choice = ""
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [
            PlayCardSelectStep
        ]
        assert is_equal_candidates(
            step.get_candidates(game),
            [
                "0:play:%d#0" % get_card_id("hoshikuzu"),
                "0:play:%d#0" % get_card_id("funka"),
                "0:play:%d#0" % get_card_id("honow")
            ]
        )

    def test_process_2(self, get_step_classes, is_equal_candidates):
        R1 = get_card_id("honow")
        R2 = get_card_id("funka")
        N = get_card_id("hoshikuzu")
        step = PlayCardSelectStep(0)
        step.played_ids_and_uniq_ids = [
            [R1, 0], [R2, 1], [N, 2]
        ]
        game = self.get_game([[
            Card(R1, 0),
            Card(R2, 1),
            Card(N, 2),
        ]])
        game.choice = ""
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [
            PlayContinueStep
        ]

    def test_process_3(self, get_step_classes, is_equal_candidates):
        R1 = get_card_id("honow")
        R2 = get_card_id("funka")
        N = get_card_id("hoshikuzu")
        step = PlayCardSelectStep(0)
        step.played_ids_and_uniq_ids = [
            [R1, 0], [R2, 1]
        ]
        game = self.get_game([[
            Card(R1, 0),
            Card(R2, 1),
            Card(N, 2),
        ]])
        game.choice = ""
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [
            PlayCardSelectStep, PlayStep
        ]
        assert next_steps[1].card_ids == [N]


class TestPlayContinueStep:
    def test_str(self):
        step = PlayContinueStep(0)
        assert str(step) == "0:playcontinue:0"

    def test_process_1(self, get_step_classes):
        step = PlayContinueStep(0)
        game = Game()
        game.set_players([Player(0)])
        game.set_supply([])
        game.players[0].pile[PileName.HAND] = Pile(
            PileType.LIST, card_list=[
                Card(1, 1), Card(1, 2)
            ]
        )
        game.players[0].pile[PileName.FIELD] = Pile(
            PileType.LISTLIST, card_list=[
                [Card(1, 3)]
            ]
        )
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [
            PlaySelectStep, DrawStep
        ]
        assert next_steps[1].count == 2

    def test_process_2(self, get_step_classes):
        step = PlayContinueStep(0)
        game = Game()
        game.set_players([Player(0)])
        game.set_supply([])
        game.players[0].pile[PileName.HAND] = Pile(
            PileType.LIST, card_list=[
                Card(1, 1), Card(1, 2), Card(1, 3), Card(2, 4)
            ]
        )
        game.players[0].pile[PileName.FIELD] = Pile(
            PileType.LISTLIST, card_list=[
                [Card(1, 5)]
            ]
        )
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [
            PlaySelectStep
        ]

    def test_process_3(self, get_step_classes):
        step = PlayContinueStep(0)
        game = Game()
        game.set_players([Player(0)])
        game.set_supply([])
        game.players[0].pile[PileName.HAND] = Pile(
            PileType.LIST, card_list=[
                Card(1, 1), Card(1, 2), Card(1, 3), Card(2, 4)
            ]
        )
        game.players[0].pile[PileName.FIELD] = Pile(
            PileType.LISTLIST, card_list=[
                [Card(3, 5)]
            ]
        )
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [
            OrbitAdvanceStep
        ]

    def test_process_4(self, get_step_classes):
        step = PlayContinueStep(0)
        game = Game()
        game.set_players([Player(0)])
        game.set_supply([])
        game.players[0].orbit = 34
        game.players[0].pile[PileName.HAND] = Pile(
            PileType.LIST, card_list=[
                Card(1, 1), Card(1, 2), Card(1, 3), Card(2, 4)
            ]
        )
        game.players[0].pile[PileName.FIELD] = Pile(
            PileType.LISTLIST, card_list=[
                [Card(3, 5)]
            ]
        )
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [
            OrbitAdvanceStep
        ]


class TestOrbitAdvanceStep:
    def test_str(self):
        step = OrbitAdvanceStep(0)
        assert str(step) == "0:orbitadvance:0"

    def test_process_1(self, get_step_classes):
        step = OrbitAdvanceStep(0)
        game = Game()
        game.phase = Phase.PLAY
        game.set_players([Player(0), Player(1)])
        game.set_supply([])
        game.players[0].orbit = 15
        game.players[1].orbit = 17
        game.players[0].tmp_orbit = 17
        game.players[0].pile[PileName.FIELD] = Pile(
            PileType.LISTLIST, card_list=[
                [Card(1, 1)],
                [Card(1, 2)]
            ]
        )
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [GenerateSelectStep]
        assert game.players[0].orbit == 17.1
        assert game.phase == Phase.ORBIT

    def test_process_2(self, get_step_classes):
        step = OrbitAdvanceStep(0)
        game = Game()
        game.phase = Phase.PLAY
        game.set_players([Player(0), Player(1), Player(2), Player(3)])
        game.set_supply([])
        game.players[0].orbit = 33
        game.players[1].orbit = 24.1
        game.players[2].orbit = 18.2
        game.players[3].orbit = 24
        game.players[0].tmp_orbit = 35
        game.players[0].pile[PileName.FIELD] = Pile(
            PileType.LISTLIST, card_list=[
                [Card(1, 1)],
                [Card(1, 2)]
            ]
        )
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [GenerateSelectStep]
        assert game.players[0].orbit == 35
        assert game.players[1].orbit == 25.1
        assert game.players[2].orbit == 19
        assert game.players[3].orbit == 25
        assert game.phase == Phase.ORBIT


class TestGenerateSelectStep:
    def test_str(self):
        step = GenerateSelectStep(0)
        assert str(step) == "0:generateselect:0"

    def test_process_1(self, get_step_classes, is_equal_candidates):
        step = GenerateSelectStep(0)
        game = Game()
        game.phase = Phase.ORBIT
        game.set_players([Player(0), Player(1)])
        game.set_supply([])
        game.players[0].pile[PileName.FIELD] = Pile(
            PileType.LISTLIST, card_list=[
                [Card(1, 1), Card(2, 2), Card(2, 3), Card(7, 4)]
            ]
        )
        next_steps = step.process(game)
        assert game.starflake == 8
        assert get_step_classes(next_steps) == [GenerateSelectStep]
        assert game.phase == Phase.GENERATE
        assert is_equal_candidates(
            next_steps[0].get_candidates(game),
            [
                "0:generate:3#0",
                "0:generate:4#0",
                "0:generate:0#0",
            ]
        )

    def test_process_2(self, get_step_classes, is_equal_candidates):
        step = GenerateSelectStep(0)
        game = Game()
        game.phase = Phase.ORBIT
        game.set_players([Player(0), Player(1)])
        game.set_supply([])
        game.players[0].pile[PileName.FIELD] = Pile(
            PileType.LISTLIST, card_list=[
                [Card(1, 1), Card(2, 2), Card(2, 3), Card(7, 4)]
            ]
        )
        game.choice = "0:generate:4"
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [
            CleanupStep, GainStep, AddStarflakeStep
        ]
        assert game.phase == Phase.GENERATE
        assert next_steps[1].card_ids == [4]

    def test_process_3(self, get_step_classes, is_equal_candidates):
        step = GenerateSelectStep(0)
        game = Game()
        game.phase = Phase.ORBIT
        game.set_players([Player(0), Player(1)])
        game.set_supply([])
        game.players[0].pile[PileName.FIELD] = Pile(
            PileType.LISTLIST, card_list=[
                [Card(1, 1), Card(2, 2), Card(2, 3), Card(7, 4)]
            ]
        )
        game.choice = "0:generate:0"
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [CleanupStep]
        assert game.phase == Phase.GENERATE


class TestCleanupStep:
    def test_str(self):
        step = CleanupStep(0)
        assert str(step) == "0:cleanup:0"

    def test_process_1(self, get_step_classes, is_equal_candidates):
        step = CleanupStep(0)
        game = Game()
        game.phase = Phase.GENERATE
        game.set_players([Player(0), Player(1)])
        game.set_supply([])
        game.players[0].pile[PileName.FIELD] = Pile(
            PileType.LISTLIST, card_list=[
                [Card(1, 1)],
                [Card(1, 2), Card(2, 3)]
            ]
        )
        game.players[0].pile[PileName.HAND] = Pile(
            PileType.LIST, card_list=[
                Card(1, 4), Card(2, 5), Card(3, 6)
            ]
        )
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [
            UpdateTurnStep, DrawStep, DiscardStep, DiscardStep
        ]
        next_steps[1].count == 1
        assert game.phase == Phase.CLEAN_UP

    def test_process_2(self, get_step_classes, is_equal_candidates):
        step = CleanupStep(0)
        game = Game()
        game.phase = Phase.GENERATE
        game.set_players([Player(0), Player(1)])
        game.set_supply([])
        game.players[0].pile[PileName.FIELD] = Pile(
            PileType.LISTLIST, card_list=[
                [Card(1, 1)],
                [Card(1, 2), Card(2, 3)]
            ]
        )
        game.players[0].pile[PileName.HAND] = Pile(
            PileType.LIST, card_list=[
                Card(1, 4), Card(2, 5), Card(3, 6),
                Card(1, 7), Card(2, 8)
            ]
        )
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [
            UpdateTurnStep, CleanupDiscardHandStep, DiscardStep, DiscardStep
        ]
        assert game.phase == Phase.CLEAN_UP


class TestCleanupDiscardHandStep:
    def test_str(self):
        step = CleanupDiscardHandStep(0)
        assert str(step) == "0:cleanupdiscardhand:0"

    def test_process_1(self, get_step_classes, is_equal_candidates):
        step = CleanupDiscardHandStep(0)
        game = Game()
        game.set_players([Player(0)])
        game.players[0].pile[PileName.HAND] = Pile(
            PileType.LIST, card_list=[
                Card(1, 1), Card(1, 2), Card(1, 3),
                Card(2, 4), Card(2, 5)
            ]
        )
        game.choice = ""
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [CleanupDiscardHandStep]
        assert is_equal_candidates(
            next_steps[0].get_candidates(game),
            [
                "0:cleanupdiscard:1#0",
                "0:cleanupdiscard:2#0"
            ]
        )

    def test_process_2(self, get_step_classes, is_equal_candidates):
        step = CleanupDiscardHandStep(0)
        game = Game()
        game.set_players([Player(0)])
        game.players[0].pile[PileName.HAND] = Pile(
            PileType.LIST, card_list=[
                Card(1, 1), Card(1, 2), Card(1, 3),
                Card(2, 4), Card(2, 5)
            ]
        )
        game.choice = "0:cleanupdiscard:2"
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [DiscardStep]


class TestUpdateTurnStep:
    def test_str(self):
        step = UpdateTurnStep(0)
        assert str(step) == "0:updateturn:0"

    def test_process_1(self, get_step_classes, is_equal_candidates):
        step = UpdateTurnStep(0)
        game = Game()
        game.phase = Phase.CLEAN_UP
        game.set_players([Player(0), Player(1)])
        game.set_supply([])
        game.players[0].orbit = 14.1
        game.players[1].orbit = 14
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [
            TurnStartStep
        ]
        next_steps[0].player_id == 0
        assert game.phase == Phase.TURN_END

    def test_process_2(self, get_step_classes, is_equal_candidates):
        step = UpdateTurnStep(0)
        game = Game()
        game.phase = Phase.CLEAN_UP
        game.set_players([Player(0), Player(1)])
        game.set_supply([])
        game.turn = Turn(1, 1, 0, TurnType.NORMAL)
        game.players[0].orbit = 13
        game.players[1].orbit = 14
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [
            TurnStartStep
        ]
        next_steps[0].player_id == 1
        assert game.phase == Phase.TURN_END
        assert next_steps[0].turn.turn == 2
        assert next_steps[0].turn.uniq_turn == 2

    def test_process_3(self, get_step_classes, is_equal_candidates):
        step = UpdateTurnStep(0)
        game = Game()
        game.phase = Phase.CLEAN_UP
        game.set_players([Player(0), Player(1)])
        game.set_supply([])
        game.turn = Turn(1, 1, 0, TurnType.NORMAL)
        game.players[0].orbit = 35
        game.players[1].orbit = 35
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == [
            GameFinishStep
        ]


class TestGameFinishStep:
    def test_str(self):
        step = GameFinishStep()
        assert str(step) == "0:gamefinish:"

    def test_process_1(self, get_step_classes, is_equal_candidates):
        game = Game()
        game.set_players([Player(0), Player(1), Player(2)])
        game.set_supply([])
        game.players[0].pile[PileName.HAND] = Pile(
            PileType.LIST, card_list=[
                Card(3, 1), Card(4, 2)
            ]
        )
        game.players[1].pile[PileName.FIELD] = Pile(
            PileType.LISTLIST, card_list=[
                [
                    Card(3, 3), Card(5, 4)
                ]
            ]
        )
        game.players[2].pile[PileName.HAND] = Pile(
            PileType.LIST, card_list=[
                Card(3, 5), Card(4, 6)
            ]
        )
        game.players[0].orbit = 35.2
        game.players[1].orbit = 35.1
        game.players[2].orbit = 35
        step = GameFinishStep()
        next_steps = step.process(game)
        assert get_step_classes(next_steps) == []
        assert game.phase == Phase.FINISH
        assert game.winner_id == 1
        assert game.result == [
            {"point": 5, "rank": 3, "player_id": 0, "cards": [3, 4]},
            {"point": 9, "rank": 1, "player_id": 1, "cards": [3, 5]},
            {"point": 5, "rank": 2, "player_id": 2, "cards": [3, 4]}
        ]
