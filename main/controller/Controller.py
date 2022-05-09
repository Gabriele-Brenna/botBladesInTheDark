import threading

from character.Human import Human
from controller.DBreader import *
from controller.DBwriter import *
from game.Game import Game
from game.Player import Player
from utility.FilesLoader import load_games
from utility.ISavable import save_to_json


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

    def update_user_in_game(self, player_id: int, chat_id: int, game_title: str,
                            is_master: bool = False, pc: dict = None):
        """
        Adds a new user to the specified Game's list of player. If the user was already present, is updated with the new
        information or changes. In any case the Data Base is updated too.

        :param player_id: telegram id of the user to update.
        :param chat_id: identifier of the origin chat of the Game
        :param game_title: name of the Game where the player is/needs to be added
        :param is_master: bool that state if the player should be set to master. If True the old master is removed from
                        his role and eventually removed from the list if he had no characters.
        :param pc: dict containing all the information about a pc. If None, no pc is added to the player.
        """
        game_id = query_game_ids(chat_id, game_title)[0]
        human = None
        if pc is not None:
            action_dots = pc.pop("action_dots")
            human = Human.from_json(pc)

            # Transforming the dict into a list of tuples
            action_dots = list(action_dots.items())
            for action in action_dots:
                human.add_action_dots(*action)

        for game in self.games:
            if game.identifier == game_id:

                # Old master
                if is_master:
                    master = game.get_master()
                    if master is not None:
                        master.is_master = False
                        if not master.characters:
                            game.users.remove(master)
                            delete_user_game(player_id, chat_id)

                # User already present
                for user in game.users:
                    if user.player_id == player_id:

                        if is_master:
                            user.is_master = is_master
                        if human is not None:
                            user.characters.append(human)

                        insert_user_game(player_id, game_id, save_to_json(user.characters), user.is_master)
                        return

                # New user
                """human = None
                if pc is not None:
                    human = [Human.from_json(pc)]"""
                new_player = Player(query_users_names(player_id)[0], player_id, is_master, human)
                game.users.append(new_player)

                insert_user_game(player_id, game_id, save_to_json(new_player.characters), is_master)

    def __repr__(self) -> str:
        return str(self.games)


