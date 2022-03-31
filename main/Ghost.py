from typing import List

from Attribute import Attribute
from Character import Character
from Clock import Clock
from Crew import Crew
from Item import Item
from Organization import Organization
from Playbook import Playbook
from SpecialAbility import SpecialAbility
from Vice import Vice


class Ghost(Character):
    def __init__(self, name: str = "", faction: Organization = Crew(), role: str = "", alias: str = "", look: str = "",
                 heritage: str = "", background: str = "", stress_level: int = 0, stress_limit: int = 9,
                 traumas: List[str] = None, items: List[Item] = None, harms: List[List[str]] = None,
                 healing: Clock = None, armors: List[bool] = None, abilities: List[SpecialAbility] = None,
                 playbook: Playbook = Playbook(8), insight: Attribute = None, prowess: Attribute = None,
                 resolve: Attribute = None, load: int = 0, xp_triggers: List[str] = None, notes: str = "",
                 downtime_activities: List[str] = None,
                 enemies_rivals: List[str] = None) -> None:
        super().__init__(name, faction, role, alias, look, heritage, background, stress_level, stress_limit, traumas,
                         items, harms, healing, armors, abilities, playbook, insight, prowess, resolve, load,
                         xp_triggers, notes, downtime_activities)
        if enemies_rivals is None:
            enemies_rivals = []
        self.enemies_rivals = enemies_rivals
        self.need = Vice("Life Essence", """Feeding: Use a downtime activity to Hunt prey and indulge 
                         your vice. Also, when you feed,mark four ticks on your healing clock. 
                         This is the only way you can heal.""", "consumed from a living human")

    def __eq__(self, o: object) -> bool:
        return isinstance(o, self.__class__) and o.__dict__ == self.__dict__
