from typing import List

from Attribute import Attribute
from Clock import Clock
from Crew import Crew
from HarmBox import HarmBox
from Item import Item
from Organization import Organization
from Playbook import Playbook
from SpecialAbility import SpecialAbility


class Character:

    def __init__(self, name: str = "", faction: Organization = Crew(), role: str = "", alias: str = "", look: str = "",
                 heritage: str = "", background: str = "", stress_level: int = 0, stress_limit: int = 9,
                 traumas: List[str] = None, items: List[Item] = None, harms: HarmBox = None,
                 healing: Clock = None, armors: List[bool] = List[False, False, False],
                 abilities: List[SpecialAbility] = None, playbook: Playbook = Playbook(8),
                 insight: Attribute = None, prowess: Attribute = None, resolve: Attribute = None,
                 load: int = 0, xp_triggers: List[str] = None, notes: str = "",
                 downtime_activities: List[str] = None) -> None:

        self.name = name
        self.faction = faction
        self.role = role
        self.alias = alias
        self.look = look
        self.heritage = heritage
        self.background = background
        self.stress_level = stress_level
        self.stress_limit = stress_limit
        if traumas is None:
            traumas = []
        self.traumas = traumas
        if items is None:
            items = []
        self.items = items
        if harms is None:
            harms = [[], [], []]
        self.harms = harms
        if healing is None:
            healing = Clock("{}_Healing".format(name))
        self.healing = healing
        self.armors = armors
        if abilities is None:
            abilities = []
        self.abilities = abilities
        self.playbook = playbook
        self.insight = insight
        self.prowess = prowess
        self.resolve = resolve
        self.load = load
        string = "Every time you roll a desperate action, mark xp in that action's attribute"
        if xp_triggers is None:
            xp_triggers = [string]
        elif not xp_triggers.__contains__(string):
            xp_triggers.insert(0, string)
        self.xp_triggers = xp_triggers
        if downtime_activities is None:
            downtime_activities = []
        self.downtime_activities = downtime_activities
        self.notes = notes

    def add_stress(self, stress: int) -> int:
        self.stress_level += stress
        if self.stress_level >= self.stress_limit:
            temp = int(self.stress_level / self.stress_limit)
            self.stress_level %= self.stress_limit
            return temp
        return 0

    def clear_stress(self, n: int) -> bool:
        self.stress_level -= n
        if self.stress_level < 0:
            self.stress_level = 0
            return True
        return False

    def add_trauma(self, trauma: str) -> bool:
        if len(self.traumas) < 4:
            self.traumas.append(trauma)
            return True
        return False

    def add_harm(self, level: int, description: str) -> int:
        if level == len(self.harms):
            if len(self.harms[-1]) == 0:
                self.harms[-1].append(description)
                return level
            else:
                return level + 1
        else:
            if len(self.harms[level - 1]) < 2:
                self.harms[level - 1].append(description)
                return level
            else:
                return self.add_harm(level + 1, description)

    def heal_harms(self):
        self.harms[0].clear()
        for i in range(len(self.harms) - 1):
            for harm in self.harms[i + 1]:
                self.harms[i].append(harm)
            self.harms[i + 1].clear()

    def count_harms(self, level: int) -> int:
        return len(self.harms[level - 1])

    def recover(self):
        for i in range(len(self.harms)):
            self.heal_harms()

    def print_harms(self) -> str:
        out = ""
        for i in range(len(self.harms)):
            out = out + "Level " + str(i + 1) + ": " + str(self.harms[i]) + "\n"
        return out

    def clear_consumable(self):
        self.items.clear()
        self.load = 0
        for i in range(len(self.armors)):
            self.armors[i] = False

    def use_armor(self, armor_type: str) -> bool:
        if armor_type.lower() == "standard":
            i = 0
        elif armor_type.lower() == "heavy":
            i = 1
        elif armor_type.lower() == "special":
            i = 2
        else:
            return False
        if not self.armors[i]:
            self.armors[i] = True
            return True
        return False

    def has_item(self, item: Item) -> int:
        for i in range(len(self.items)):
            if self.items[i].name == item.name:
                return i

    def carried_load(self) -> int:
        carried = 0
        for i in self.items:
            carried += i.weight
        return carried

    def use_item(self, item: Item) -> bool:
        contain = self.has_item(item)
        if contain is not None:
            return self.items[contain].use()
        else:
            if self.carried_load() < self.load:
                item.use()
                self.items.append(item)
                return True
        return False

    def add_notes(self, note: str):
        self.notes += "\n" + note

    def migrate_character_type(self, new_type: str) -> bool:
        if new_type.lower() == "ghost":
            # TODO : migrate to ghost
            return True
        elif new_type.lower() == "vampire":
            # TODO : migrate to vampire
            return True
        elif new_type.lower() == "hull":
            # TODO : migrate to hull
            return True
        return False

    def __repr__(self) -> str:
        return str(self.__dict__)

