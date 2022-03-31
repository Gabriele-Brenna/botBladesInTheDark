from typing import List

from component.Clock import Clock
from game.Journal import Journal
from character.NPC import NPC
from game.Player import Player
from game.Score import Score

_id = 1


class Game:
    def __init__(self, identifier: int = _id, title: str = "Game" + str(_id), users: List[Player] = None,
                 NPCs: List[NPC] = None, clocks: List[Clock] = None,
                 scores: List[Score] = None, journal: Journal = Journal()) -> None:
        self.identifier = identifier
        self.title = title
        if users is None:
            users = []
        self.users = users
        if NPCs is None:
            NPCs = []
        self.NPCs = NPCs
        if clocks is None:
            clocks = []
        self.clocks = clocks
        if scores is None:
            scores = []
        self.scores = scores
        self.journal = journal
        global _id
        self.n_clock = 100 * _id
        _id += 1

    def get_project_clocks(self) -> List[Clock]:
        clock = []
        for c in self.clocks:
            if c.name.lower().startswith("project"):
                clock.append(c)
        return clock

    def create_clock(self, name: str = None, segments: int = 4) -> Clock:
        if name is None:
            self.n_clock += 1
            name = "Clock" + str(self.n_clock)
        self.clocks.append(Clock(name, segments))
        return self.clocks[-1]

    def tick_clock(self, name: str, ticks: int) -> Clock:
        for c in self.clocks:
            if c.name.lower() == name.lower():
                if c.tick(ticks):
                    self.clocks.remove(c)
                return c

    def see_clocks(self, names: List[str] = None) -> List[Clock]:
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
        return max(self.scores, key=lambda score: len(score.participants))
