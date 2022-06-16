from typing import List

from character.Item import Item
from character.Owner import Owner
from character.PC import PC
from component.Clock import Clock
from controller.DBreader import query_last_game_id
from game.Journal import Journal
from character.NPC import NPC
from game.Player import Player
from game.Score import Score
from organization.Crew import Crew
from organization.Faction import Faction

INIT, FREE_PLAY, SCORE_PHASE, DOWNTIME_PHASE = range(4)


class Game:
    """
    Represents an instance of a game and keeps track of the participants and their roles
    """
    def __init__(self, identifier: int = None, title: str = None,
                 users: List[Player] = None, NPCs: List[NPC] = None, crew: Crew = None,
                 factions: List[Faction] = None, clocks: List[Clock] = None, scores: List[Score] = None,
                 crafted_items: List[Item] = None, journal: Journal = Journal(), state: int = INIT,
                 chat_id: int = None) -> None:
        """
        Constructor of the Game.

        :param identifier: id of this Game instance. If None it is automatically set to the last game id in the DB +1.
        :param title: title of the Game. If None it is set to "Game[ID]".
        :param users: list of Players that have joined the Game.
        :param NPCs: list of NPCs that have been loaded during the Game.
        :param crew: the Crew of the characters in this Game.
        :param factions: list of Factions that have been loaded during the Game.
        :param clocks: list of Clocks that have been started during the Game.
        :param scores: list of the active Scores.
        :param crafted_items: list of Items that have been created during the Game.
        :param journal: Journal of this Game.
        :param state: is the current state of this Game. When the game is created the state is set to INIT.
                      (The possible states are INIT, FREE_PLAY, SCORE_PHASE, DOWNTIME_PHASE).
        :param chat_id: id of the telegram chat that has started the game
        """
        if identifier is None:
            identifier = query_last_game_id()+1
        self.identifier = identifier
        if title is None:
            title = "Game" + str(query_last_game_id()+1)
        self.title = title
        if users is None:
            users = []
        self.users = users
        if NPCs is None:
            NPCs = []
        self.NPCs = NPCs
        self.crew = crew
        if factions is None:
            factions = []
        self.factions = factions
        if clocks is None:
            clocks = []
        self.clocks = clocks
        if scores is None:
            scores = []
        self.scores = scores
        if crafted_items is None:
            crafted_items = []
        self.crafted_items = crafted_items
        self.journal = journal
        self.n_clock = 100 * identifier
        if state < 0 or state > 2:
            state = FREE_PLAY
        self.state = state
        self.chat_id = chat_id

    def get_project_clocks(self) -> List[Clock]:
        """
        Retrieves the list of Project Clocks (i.e. Clocks that contains the "Project" word)

        :return: the list of all Project Clock
        """
        clock = []
        for c in self.clocks:
            if c.name.lower().startswith("[project]"):
                clock.append(c)
        return clock

    def create_clock(self, name: str = None, segments: int = 4) -> Clock:
        """
        Creates a new Clock and adds it in the clocks list

        :param name: is the name of the Clock
        :param segments: is the number of segments that composes the clock
        :return: the new created Clock
        """
        if name is None:
            self.n_clock += 1
            name = "Clock" + str(self.n_clock)
        self.clocks.append(Clock(name, segments))
        return self.clocks[-1]

    def tick_clock(self, clock: Clock, ticks: int) -> Clock:
        """
        Ticks the given Clock by the specified number of ticks.
        If the clock is completed it removes it from the clocks list

        :param clock: the clock that needs to be ticked.
        :param ticks: is the number of ticks
        :return: the Clock ticked if found, None otherwise
        """
        for c in self.clocks:
            if c == clock:
                if c.tick(ticks):
                    self.clocks.remove(c)
                return c

    def see_clocks(self, names: List[str] = None) -> List[Clock]:
        """
        Retrieves the list of Clocks, given their names.

        :param names: the names of the Clocks to retrieve
        :return: the list of matching Clocks or the clocks list if no name is specified
        """
        if names is None:
            return self.clocks
        else:
            clocks = []
            for c in self.clocks:
                for n in names:
                    if n.casefold() in c.name.casefold():
                        clocks.append(c)
            return clocks

    def get_main_score(self) -> Score:
        """
        Finds the score with the highest number of participants in the scores list

        :return: the first Score that matches the search
        """
        return max(self.scores, key=lambda score: len(score.participants))

    def get_master(self) -> Player:
        """
        Searches the list of users and gets the one who is master.

        :return: a Player with the attribute is_master = True
        """
        for p in self.users:
            if p.is_master:
                return p

    def get_pcs_list(self, user_id: int = None) -> List[PC]:
        """
        Gets the list of all the PCs of all users that participate in this game or only the specified user's list.

        :param user_id: represents the id of the target user.
        :return: a list of PCs. (Empty list if no PCs are in the game)
        """
        pcs = []
        for player in self.users:
            if user_id is not None and player.player_id == user_id:
                pcs += player.characters
            elif user_id is None:
                pcs += player.characters
        return pcs

    def get_owners_list(self, user_id: int = None) -> List[Owner]:
        """
        Gets the list of all the PCs that are Owner of all users that participate in this game
        or only the specified user's list.

        :param user_id: represents the id of the target user.
        :return: a list of PCs. (Empty list if no PCs are in the game)
        """
        owners = []
        for player in self.users:
            if user_id is not None and player.player_id == user_id:
                for pc in player.characters:
                    if isinstance(pc, Owner):
                        owners += player.characters
            elif user_id is None:
                for pc in player.characters:
                    if isinstance(pc, Owner):
                        owners += player.characters
        return owners

    def get_player_by_id(self, user_id: int) -> Player:
        """
        Returns the Player with the passed ID.

        :param user_id: is the ID to search
        :return: a Player object.
        """
        for player in self.users:
            if player.player_id == user_id:
                return player

    def get_faction_by_name(self, name: str) -> Faction:
        """
        Returns the Faction with the passed name.

        :param name: is the name to search.
        :return: a Faction object.
        """
        for elem in self.factions:
            if elem.name.lower() == name.lower():
                return elem

    def get_npc_by_name_and_role(self, name: str, role: str) -> NPC:
        """
        Returns the NPC with the passed name and role.

        :param name: is the name to search.
        :param role: is the role to search.
        :return: a NPC object.
        """
        for npc in self.NPCs:
            if npc.name.lower() == name.lower() and npc.role.lower() == role.lower():
                return npc

    def __eq__(self, o: object) -> bool:
        return isinstance(o, self.__class__) and o.__dict__ == self.__dict__

    def __repr__(self) -> str:
        return str(self.__dict__)

