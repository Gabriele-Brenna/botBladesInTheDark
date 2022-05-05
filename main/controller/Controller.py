import threading

from controller.DBwriter import insert_game
from game.Game import Game
from utility.FilesLoader import load_games


class Controller:

    def __init__(self) -> None:
        self.games = load_games()
        self.lock_add_game = threading.Lock()

    def add_game(self, chat_id: int, title: str = None) -> int:
        """
        Creates a new Game and adds it to self.games

        :param title: the title of the new Game
        :param chat_id: the id of the telegram chat where the game is created.
        :return: the id of the game in the Data Base
        """
        self.lock_add_game.acquire()
        new_game = Game(title=title, chat_id=chat_id)

        insert_game(new_game.identifier, new_game.title, new_game.chat_id)

        self.games.append(new_game)

        self.lock_add_game.release()
        return new_game.identifier
