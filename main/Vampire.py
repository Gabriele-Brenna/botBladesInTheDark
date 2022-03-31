from typing import List

from Attribute import Attribute
from Clock import Clock
from Crew import Crew
from Item import Item
from NPC import NPC
from Organization import Organization
from Owner import Owner
from Playbook import Playbook
from SpecialAbility import SpecialAbility
from Vice import Vice


class Vampire(Owner):

    def __init__(self, name: str = "", faction: Organization = Crew(), role: str = "", alias: str = "", look: str = "",
                 heritage: str = "", background: str = "", stress_level: int = 0, stress_limit: int = 9,
                 traumas: List[str] = None, items: List[Item] = None, harms: List[List[str]] = None,
                 healing: Clock = None, armors: List[bool] = None, abilities: List[SpecialAbility] = None,
                 playbook: Playbook = Playbook(8), insight: Attribute = None, prowess: Attribute = None,
                 resolve: Attribute = None, load: int = 0, xp_triggers: List[str] = None, notes: str = "",
                 downtime_activities: List[str] = None, coin: int = 0, stash: int = 0,
                 strictures: List[str] = None, dark_servants: List[NPC] = None) -> None:
        super().__init__(name, faction, role, alias, look, heritage, background, stress_level, stress_limit, traumas,
                         items, harms, healing, armors, abilities, playbook, insight, prowess, resolve, load,
                         xp_triggers, notes, downtime_activities, coin, stash,
                         vice=Vice("Life Essence", """Feeding: Use a downtime activity to Hunt prey and indulge 
                         your vice. Also, when you feed,mark four ticks on your healing clock. 
                         This is the only way you can heal.""", "consumed from a living human"))
        if strictures is None:
            strictures = []
        self.strictures = strictures
        if dark_servants is None:
            dark_servants = [NPC(), NPC()]
        self.dark_servants = dark_servants

    def __eq__(self, o: object) -> bool:
        return isinstance(o, self.__class__) and o.__dict__ == self.__dict__
