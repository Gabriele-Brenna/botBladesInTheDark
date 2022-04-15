from abc import abstractmethod
from typing import List

from character.Action import Action
from character.Attribute import Attribute
from character.Character import Character
from component.Clock import Clock
from controller.DBreader import query_special_abilities, query_attributes
from character.Item import Item
from character.Playbook import Playbook
from component.SpecialAbility import SpecialAbility


def get_ghost_abilities(abilities: List[SpecialAbility]) -> List[SpecialAbility]:
    """
    Filters the abilities that only contain "ghost" in them except "ghost form"

    :param abilities: list of abilities to filter
    :return: a list of only "ghost" abilities
    """
    ghost_abilities = []
    for ability in abilities:
        if "ghost" in ability.name.lower() and ability.name.lower() != "ghost form":
            ghost_abilities.append(ability)
    return ghost_abilities


def get_class_abilities(abilities: List[SpecialAbility], sheet: str) -> List[SpecialAbility]:
    """
    Method used during the migration to a "Spirit PC".
    Calls get_ghost_abilities and fetch the peculiar ability of the destination Spirit PC.

    :param abilities: list of SpecialAbility to filter
    :param sheet: the specified Spirit PC
    :return: a list of SpecialAbility containing all the "ghost" abilities and the peculiar SpecialAbility of
            the specified sheet
    """
    class_abilities = get_ghost_abilities(abilities)
    class_abilities.insert(0, query_special_abilities(sheet, True)[0])
    return class_abilities


class PC(Character):
    """
    Represent each type of playable character
    """

    def __init__(self, name: str = "", alias: str = "", look: str = "",
                 heritage: str = "", background: str = "", stress_level: int = 0, stress_limit: int = 9,
                 traumas: List[str] = None, items: List[Item] = None, harms: List[List[str]] = None,
                 healing: Clock = None, armors: List[bool] = None,
                 abilities: List[SpecialAbility] = None, playbook: Playbook = Playbook(8),
                 attributes: List[Attribute] = None,
                 load: int = 0, xp_triggers: List[str] = None, description: str = "",
                 downtime_activities: List[str] = None) -> None:
        super().__init__(name, description)
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
        if armors is None:
            armors = [False, False, False]
        self.armors = armors
        if abilities is None:
            abilities = []
        self.abilities = abilities
        self.playbook = playbook
        if attributes is None:
            attributes = query_attributes()
        self.attributes = attributes
        self.load = load
        if xp_triggers is None:
            xp_triggers = []
        self.xp_triggers = xp_triggers
        if downtime_activities is None:
            downtime_activities = []
        self.downtime_activities = downtime_activities

    def add_stress(self, stress: int) -> int:
        """
        Adds the specified stress to the stress level of the PC, keeping the exceeding stress level that
        cross the stress limit.

        :param stress: amount of stress to add
        :return: number of traumas (how many times the stress limit has been exceeded)
        """
        self.stress_level += stress
        if self.stress_level >= self.stress_limit:
            temp = int(self.stress_level / self.stress_limit)
            self.stress_level %= self.stress_limit
            return temp
        return 0

    def clear_stress(self, n: int) -> bool:
        """
        Remove the specified amount of stress.

        :param n: stress to remove
        :return: True if you have cleared more stress than you had, False otherwise
        """
        self.stress_level -= n
        if self.stress_level < 0:
            self.stress_level = 0
            return True
        return False

    def add_trauma(self, trauma: str) -> bool:
        """
        Add the specified trauma if there are less than 4 in traumas' list.

        :param trauma: description of the new trauma
        :return: True if the trauma has been added
        """
        if len(self.traumas) < 4:
            self.traumas.append(trauma)
            return True
        return False

    def add_harm(self, level: int, description: str) -> int:
        """
        Add the harm's description to the harms' list at the specified level.
        If the required level is full the harm is added at the next level.
        If every level is full the harm is not added.

        :param level: level representing the severity of the harm
        :param description: description of the harm
        :return: the level where the harm has been inserted or the last level +1 if all the levels are full
        """
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
        """
        Downgrades each harm in the harms' list, popping the level 1 harms out of it.
        """
        self.harms[0].clear()
        for i in range(len(self.harms) - 1):
            for harm in self.harms[i + 1]:
                self.harms[i].append(harm)
            self.harms[i + 1].clear()

    def tick_healing_clock(self, ticks: int) -> int:
        healed = 0
        for i in range(ticks):
            if self.healing.tick(1):
                healed += 1
                self.healing.progress = 0
        for j in range(healed):
            self.heal_harms()
        return healed

    def count_harms(self, level: int) -> int:
        """
        Count the number of harms at the specified level.

        :param level: the level to check
        :return: the number of harms
        """
        return len(self.harms[level - 1])

    def recover(self):
        """
        Clears the harms' list.
        """
        for i in range(len(self.harms)):
            self.heal_harms()

    def clear_consumable(self):
        """
        Clear all the 'consumable' of the PC (items, load, armors and downtime_activities ).
        """
        self.downtime_activities.clear()
        self.items.clear()
        self.load = 0
        for i in range(len(self.armors)):
            self.armors[i] = False

    def use_armor(self, armor_type: str) -> bool:
        """
        Set to True(used) the specified armor.

        :param armor_type: the armor to ise
        :return: True if the armor is used correctly, False if it was already used
        """
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
        """
        Checks if the character has the specified item

        :param item: the item to check
        :return: the position of the item in the list items (None if it is not present)
        """
        for i in range(len(self.items)):
            if self.items[i].name == item.name:
                return i

    def carried_load(self) -> int:
        """
        Calculate the carried load of the character.

        :return: the sum of the weight of the currently used items
        """
        carried = 0
        for i in self.items:
            carried += i.weight
        return carried

    def use_item(self, item: Item) -> bool:
        """
        Adds the specified item to the items' list if not already present and not exceed the load, use it otherwise.

        :param item: the item to use
        :return: True if has been used, False otherwise
        """
        contain = self.has_item(item)
        if contain is not None:
            return self.items[contain].use()
        else:
            if self.carried_load() < self.load or item.weight == 0:
                item.use()
                self.items.append(item)
                return True
        return False

    def add_notes(self, note: str):
        """
        Adds the specified note to the description.

        :param note: the note to add
        """
        self.description += "\n" + note

    def get_attribute_by_name(self, attribute: str) -> Attribute:
        for attr in self.attributes:
            if attr.name.lower() == attribute.lower():
                return attr

    def get_action_by_name(self, action: str) -> Action:
        for attr in self.attributes:
            for act in attr.actions:
                if act.name.lower() == action.lower():
                    return act

    def get_attribute_level(self, attribute: str) -> int:
        attr = self.get_attribute_by_name(attribute)
        if attr is not None:
            return attr.attribute_level()

    def get_action_rating(self, action: str) -> int:
        act = self.get_action_by_name(action)
        if act is not None:
            return act.rating

    def add_action_dots(self, action: str, dots: int) -> bool:
        act = self.get_action_by_name(action)
        if act is not None:
            return act.add_dots(dots)

    @abstractmethod
    def migrate(self, mc: super.__class__):
        pass

    @abstractmethod
    def change_pc_class(self, new_class: str):
        pass

    def __repr__(self) -> str:
        return str(self.__dict__)

    def __eq__(self, o: object) -> bool:
        return isinstance(o, self.__class__) and o.__dict__ == self.__dict__
