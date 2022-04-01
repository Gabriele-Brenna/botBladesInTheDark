from typing import List

from character.Attribute import Attribute
from component.Clock import Clock
from organization.Crew import Crew
from character.Item import Item
from character.NPC import NPC
from organization.Organization import Organization
from character.Owner import Owner
from character.Playbook import Playbook
from component.SpecialAbility import SpecialAbility
from character.Vice import Vice


class Human(Owner):
    """
    This is the human race of the game.
    """

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
