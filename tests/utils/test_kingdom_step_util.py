from hoshizukuri_game.utils.kingdom_step_util import get_kingdom_steps
from hoshizukuri_game.utils.card_util import get_card_id
from hoshizukuri_game.steps.common_card_steps import (
    HoshikuzuStep
)
from hoshizukuri_game.steps.abstract_step import AbstractStep


class TestKingdomStepUtil():
    def test_get_kingdom_steps1(self):
        step = get_kingdom_steps(0, 1, get_card_id("hoshikuzu"), 3, 0)
        assert isinstance(step, HoshikuzuStep)
        assert step.player_id == 0
        assert step.depth == 1
        assert step.uniq_id == 3

    def test_get_kingdom_steps_error(self):
        step = get_kingdom_steps(1, 2, 0, 3, 0)
        assert isinstance(step, AbstractStep)
