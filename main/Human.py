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


class Human(Owner):

    def __init__(self, name: str = "", faction: Organization = Crew(), role: str = "", alias: str = "", look: str = "",
                 heritage: str = "", background: str = "", stress_level: int = 0, stress_limit: int = 9,
                 traumas: List[str] = None, items: List[Item] = None, harms: List[List[str]] = None,
                 healing: Clock = None, armors: List[bool] = None, abilities: List[SpecialAbility] = None,
                 playbook: Playbook = Playbook(8), insight: Attribute = None, prowess: Attribute = None,
                 resolve: Attribute = None, load: int = 0, xp_triggers: List[str] = None, notes: str = "",
                 downtime_activities: List[str] = None, coin: int = 0, stash: int = 0, vice: Vice = Vice(),
                 pc_class: str = "", friend: NPC = NPC(), enemy: NPC = NPC()) -> None:
        super().__init__(name, faction, role, alias, look, heritage, background, stress_level, stress_limit, traumas,
                         items, harms, healing, armors, abilities, playbook, insight, prowess, resolve, load,
                         xp_triggers, notes, downtime_activities, coin, stash, vice)
        self.pc_class = pc_class
        self.friend = friend
        self.enemy = enemy

    def migrate(self, mc: super.__class__):
        pass

    def __repr__(self) -> str:
        return str(self.__dict__)

    def __eq__(self, o: object) -> bool:
        return isinstance(o, self.__class__) and o.__dict__ == self.__dict__
