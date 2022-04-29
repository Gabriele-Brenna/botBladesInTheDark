from typing import List

from character.Item import Item
from component.Clock import Clock
from controller.DBreader import query_last_game_id
from game.Journal import Journal
from character.NPC import NPC
from game.Player import Player
from game.Score import Score
from organization.Crew import Crew
from organization.Faction import Faction

FREE_PLAY, SCORE_PHASE, DOWNTIME_PHASE = range(3)


class Game:
    """
    Represents an instance of a game and keeps track of the participants and their roles
    """
    def __init__(self, identifier: int = query_last_game_id()+1, title: str = "Game" + str(query_last_game_id()+1),
                 users: List[Player] = None, NPCs: List[NPC] = None, crew: Crew = Crew(),
                 factions: List[Faction] = None, clocks: List[Clock] = None, scores: List[Score] = None,
                 crafted_items: List[Item] = None, journal: Journal = Journal(), state: int = FREE_PLAY) -> None:
        self.identifier = identifier
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

    def get_project_clocks(self) -> List[Clock]:
        """
        Retrieves the list of Project Clocks (i.e. Clocks that contains the "Project" word)

        :return: the list of all Project Clock
        """
        clock = []
        for c in self.clocks:
            if c.name.lower().startswith("project"):
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

    def tick_clock(self, name: str, ticks: int) -> Clock:
        """
        Ticks a Clock given its name by the specified number of ticks.
        If the clock is completed it removes it from the clocks list

        :param name: is the name of the clock that needs to be ticked
        :param ticks: is the number of ticks
        :return: the Clock ticked if found, None otherwise
        """
        for c in self.clocks:
            if c.name.lower() == name.lower():
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
