"""
Simulator module of the Hoshizukuri.
"""
from .models.game import Game
from .models.log import LogManager
from .models.player import Player
from typing import List, Callable
import traceback


class HoshizukuriGame:
    """
    This is HoshizukuriGame class.

    Args:
        callback (Callable, Optional):
            When choice is decided by log, this will be called.
    """
    def __init__(self, choice_callback: Callable[
            [Game, List[str], str], None] = None):
        self.choice_callback = choice_callback

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
        if not hasattr(game, "log_manager"):
            game.log_manager = None
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

    def simulate_with_log(self, log_filename: str, debug: bool = False):
        """
        Simulate transition of game status with log.

        Args:
            log_filename (str): log filename.
            debug (bool, Option): True is for show game status.

        Returns:
            Dict[str, ANY]: Message and Results.

        Note:
            - Result dictionary likes bellow.
            - {"message": MESSAGE, "results": [
                {"game": GAME, "step": STEPNAME, "candidates": []}]}
            - MESSAGE: "ok" or "error message"

        Raises:
            InvalidLogException: Invalid log.
        """
        log_manager = LogManager()
        log_manager.read_log(log_filename)
        players = []
        for i in range(len(log_manager.get_names())):
            players.append(Player(i))
        game = Game()
        game.log_manager = log_manager
        game.set_players(players)
        supplys = log_manager.get_supplies()
        common_supplys = [1, 2, 3, 4, 5]
        for c in common_supplys:
            if c in supplys:
                supplys.remove(c)
        game.set_supply(supplys)
        game.set_initial_step()
        # game.set_choice_callback(self.choice_callback)
        game.choice = ""
        candidates = []
        last_step = None
        try:
            while len(game.stack) > 0:
                step = game.stack.pop()
                next_steps = step.process(game)
                last_step = step
                if debug:
                    print(step)
                    print(game.get_status_json())
                if len(next_steps) > 0:
                    game.stack += next_steps
                candidates = step.get_candidates(game)
                assert len(candidates) <= 0
        except Exception as e:
            if debug:
                print(e)
                traceback.print_exc()
            return {
                "message": str(e),
                "results": []
            }
        if game.log_manager.has_logs():
            # ログが残っているエラー
            return {
                "message": "Logs are still there. (%s)" % (
                    game.log_manager._logs[0]
                ),
                "results": []
            }
        if debug:
            print("Log finish")
        mes = "ok"
        if game.result != []:
            if debug:
                print("Game finish")
            # check result of log.
            mes = game.log_manager.check_result_log(game.result)
        return {
            "message": mes,
            "results": [
                {
                    "game": game,
                    "step": str(last_step),
                    "candidates": []
                }
            ]
        }
