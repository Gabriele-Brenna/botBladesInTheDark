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


class Owner(Character):

    def __init__(self, name: str = "", faction: Organization = Crew(), role: str = "", alias: str = "", look: str = "",
                 heritage: str = "", background: str = "", stress_level: int = 0, stress_limit: int = 9,
                 traumas: List[str] = None, items: List[Item] = None, harms: List[List[str]] = None,
                 healing: Clock = None, armors: List[bool] = None, abilities: List[SpecialAbility] = None,
                 playbook: Playbook = Playbook(8), insight: Attribute = None, prowess: Attribute = None,
                 resolve: Attribute = None, load: int = 0, xp_triggers: List[str] = None, notes: str = "",
                 downtime_activities: List[str] = None,
                 coin: int = 0, stash: int = 0, vice: Vice = Vice()) -> None:
        super().__init__(name, faction, role, alias, look, heritage, background, stress_level, stress_limit, traumas,
                         items, harms, healing, armors, abilities, playbook, insight, prowess, resolve, load,
                         xp_triggers, notes, downtime_activities)
        self.coin = coin
        self.stash = stash
        self.vice = vice

    def can_have_coins(self, coins: int) -> bool:
        return self.coin + coins <= 4

    def can_stash_coins(self, coins: int) -> bool:
        return self.stash + coins <= 40

    def add_coins(self, coins: int) -> bool:
        if self.can_have_coins(coins):
            self.coin += coins
            return True
        return False

    def stash_coins(self, coins: int) -> bool:
        if self.can_stash_coins(coins):
            self.stash += coins
            return True
        return False

    def __eq__(self, o: object) -> bool:
        return isinstance(o, self.__class__) and o.__dict__ == self.__dict__
