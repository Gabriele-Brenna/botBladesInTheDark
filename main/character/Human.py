import copy
from typing import List

from character.Attribute import Attribute
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
        items = list(map(Item.from_json, data["items"]))
        healing = Clock.from_json(data["healing"])
        abilities = list(map(SpecialAbility.from_json, data["abilities"]))
        playbook = Playbook.from_json(data["playbook"])
        attributes = list(map(Attribute.from_json, data["attributes"]))
        vice = Vice.from_json(data["vice"])
        friend = NPC.from_json(data["friend"])
        enemy = NPC.from_json(data["enemy"])
        pop_dict_items(data, ["items", "healing", "abilities", "playbook", "attributes", "vice", "friend", "enemy"])
        return cls(**data, items=items, healing=healing, abilities=abilities, playbook=playbook, attributes=attributes,
                   vice=vice, friend=friend, enemy=enemy)

    def save_to_dict(self) -> dict:
        temp = super().save_to_dict()
        temp["friend"] = self.friend.save_to_dict()
        temp["enemy"] = self.enemy.save_to_dict()
        return {**{"Class": "Human"}, **temp}

    def __repr__(self) -> str:
        return str(self.__dict__)

    def __eq__(self, o: object) -> bool:
        return isinstance(o, self.__class__) and o.__dict__ == self.__dict__
