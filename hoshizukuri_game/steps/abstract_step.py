"""
Abstract base class of many steps
"""
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..models.game import Game
import uuid
from ..models.activate import TargetActivate


class AbstractStep:
    """
    This is AbstractStep.

    Attributes:
        candidates (List[int]): Legal moves when player selection arises.
        step_id (int): Unique step ID.
        depth (int): Expected log hierarchy.
    """
    def __init__(self):
        self.candidates = []
        self.step_id = str(uuid.uuid4()).replace("-", "")
        self.depth = 0

    def __str__(self):
        return "%d:abstract" % self.depth

    def process(self, game: Game):
        """
        Take the game and perform this step.

        Args:
            game (Game): Now game.

        Returns:
            List[AbstractStep]: Next steps.
        """
        return []

    def get_victory(self, game: Game):
        """
        Get victory point of this card when game finish.
        This is for Card Step.

        Args:
            game (game): Now game.

        Returns:
            int: Victory points.
        """
        return 0

    def get_victory_detail(self, game: Game):
        """
        Get victory detail of this card when game finish.
        This is for Card Step.

        Args:
            game (game): Now game.

        Returns:
            str: Victory details.
        """
        return ""

    def get_candidates(self, game: Game):
        """
        Get candidates from this step.

        Args:
            game (Game): Now game.

        Returns:
            List[str]: Legal moves.  levalmove#choice_player_id
        """
        if len(self.candidates) <= 0:
            return []
        candidates = list(self.candidates)
        choice_player_id = int(candidates[0].split(":")[0])
        for i in range(len(candidates)):
            candidates[i] = "%s#%d" % (
                candidates[i], choice_player_id
            )
        return candidates

    def can_play_trigger(self, game: Game, activate: TargetActivate):
        """
        This is for Trigger Step.
        This will be used for final check when Trigger Step will be activated.
        Normally, a trigger step is set to trigger and fires
        when its activate condition is satisfied.
        This function adds more condition to it.

        Args:
            game (Game): Now game.
            target_activate (TargetActivate): Which activate calls this step.

        Returns:
            bool: Finally, check whether can process trigger step.
                Default is True.
        """
        return True
