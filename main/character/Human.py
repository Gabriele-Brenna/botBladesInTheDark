import copy
from typing import List

from character.Attribute import Attribute
from character.PC import pc_from_json
from component.Clock import Clock
from controller.DBreader import query_xp_triggers
from character.Item import Item
from character.NPC import NPC
from character.Owner import Owner
from character.Playbook import Playbook
from component.SpecialAbility import SpecialAbility
from character.Vice import Vice
from utility.ISavable import ISavable, pop_dict_items


class Human(Owner, ISavable):
    """
    This is the human race of the game.
    """

    def __init__(self, name: str = "", alias: str = "", look: str = "",
                 heritage: str = "", background: str = "", stress_level: int = 0, stress_limit: int = 9,
                 traumas: List[str] = None, items: List[Item] = None, harms: List[List[str]] = None,
                 healing: Clock = None, armors: List[bool] = None, abilities: List[SpecialAbility] = None,
                 playbook: Playbook = Playbook(8), attributes: List[Attribute] = None,
                 load: int = 0, xp_triggers: List[str] = None, description: str = "",
                 downtime_activities: List[str] = None, coin: int = 0, stash: int = 0, vice: Vice = Vice(),
                 pc_class: str = "", friend: NPC = NPC(), enemy: NPC = NPC()) -> None:
        if xp_triggers is None and pc_class != "":
            xp_triggers = query_xp_triggers(self.__class__.__name__)

        super().__init__(name, alias, look, heritage, background, stress_level, stress_limit, traumas,
                         items, harms, healing, armors, abilities, playbook, attributes, load,
                         xp_triggers, description, downtime_activities, coin, stash, vice)
        self.pc_class = pc_class
        self.friend = friend
        self.enemy = enemy

    def migrate(self, mc: super.__class__, sheet: str = None):
        pass

    def change_pc_class(self, new_class: str):
        """
        Method used to change the class of a Human PC.

        :param new_class: is the new character sheet representing the new selected class
        """
        self.pc_class = new_class
        self.xp_triggers = query_xp_triggers(new_class)

    @classmethod
    def from_json(cls, data: dict):
        """
        Method used to create an instance of this object given a dictionary. All the complex object that are attribute
        of this class will call their from_json class method

        :param data: dictionary of the object
        :return: Human
        """
        temp = pc_from_json(data)
        vice = Vice.from_json(data["vice"])
        friend = NPC.from_json(data["friend"])
        enemy = NPC.from_json(data["enemy"])
        pop_dict_items(data, ["vice", "friend", "enemy"])
        return cls(**data, **temp, vice=vice, friend=friend, enemy=enemy)

    def save_to_dict(self) -> dict:
        """
        Reimplement save_to_dict method of ISavable by adding the item "Class" at the dictionary of the object and
        removing the Faction from the dictionary of the attributes friend and enemy.

        :return: dictionary of the object
        """
        temp = super().save_to_dict()
        temp["friend"] = self.friend.save_to_dict()
        temp["enemy"] = self.enemy.save_to_dict()
        return {**{"Class": "Human"}, **temp}

    def __repr__(self) -> str:
        return str(self.__dict__)

    def __eq__(self, o: object) -> bool:
        return isinstance(o, self.__class__) and o.__dict__ == self.__dict__
