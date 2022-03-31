from typing import List

from Attribute import Attribute
from Character import Character
from Clock import Clock
from Crew import Crew
from Item import Item
from Organization import Organization
from Playbook import Playbook
from SpecialAbility import SpecialAbility


class Hull(Character):

    def __init__(self, name: str = "", faction: Organization = Crew(), role: str = "", alias: str = "", look: str = "",
                 heritage: str = "", background: str = "", stress_level: int = 0, stress_limit: int = 9,
                 traumas: List[str] = None, items: List[Item] = None, harms: List[List[str]] = None,
                 healing: Clock = None, armors: List[bool] = None, abilities: List[SpecialAbility] = None,
                 playbook: Playbook = Playbook(8), insight: Attribute = None, prowess: Attribute = None,
                 resolve: Attribute = None, load: int = 0, xp_triggers: List[str] = None, notes: str = "",
                 downtime_activities: List[str] = None, functions: List[str] = None, frame : str = "small") -> None:
        super().__init__(name, faction, role, alias, look, heritage, background, stress_level, stress_limit, traumas,
                         items, harms, healing, armors, abilities, playbook, insight, prowess, resolve, load,
                         xp_triggers, notes, downtime_activities)
        if functions is None:
            functions = []
        self.functions = functions
        self.frame = frame

    def select_frame(self, frame_type : str):
        if frame_type.lower() == "small" or "medium" or "large" or "s" or "m" or "l":
            self.frame = frame_type

    def __eq__(self, o: object) -> bool:
        return isinstance(o, self.__class__) and o.__dict__ == self.__dict__
