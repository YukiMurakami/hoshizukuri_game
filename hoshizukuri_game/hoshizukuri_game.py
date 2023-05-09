"""
Simulator module of the Hoshizukuri.
"""
from .models.game import Game


class HoshizukuriGame:
    """
    This is HoshizukuriGame class.
    """
    def __init__(self):
        pass

    def simulate(self, game: Game, choice: str = "", debug: bool = False):
        """
        Simulate transition of game status with choice.

        Args:
            game (Game): now game.
            choice (str): simulate with this choice.
            debug (bool): True is for show game status.

        Returns:
            List[str]: The candidate of choices are need
                to move the game status,
                If game is finished, this is empty list.
        """
        steps = []
        candidates = []
        game.choice = choice
        while len(game.stack) > 0:
            step = game.stack.pop()
            next_steps = step.process(game)
            steps.append(str(step))
            if len(next_steps) > 0:
                game.stack += next_steps
            candidates = step.get_candidates(game)
            if len(candidates) > 0:
                break
        return {
            "steps": steps,
            "candidates": candidates
        }
