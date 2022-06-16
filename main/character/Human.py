from typing import List

from character.Attribute import Attribute
from character.PC import pc_from_json, paste_common_attributes
from component.Clock import Clock
from controller.DBreader import query_xp_triggers
from character.Item import Item
from character.NPC import NPC
from character.Owner import Owner
from character.Playbook import Playbook
from component.SpecialAbility import SpecialAbility
from character.Vice import Vice
from utility.FilesManager import path_finder
from utility.IDrawable import image_to_bytes
from utility.ISavable import ISavable, pop_dict_items
from PIL import Image

from utility.imageFactory.PCfactory import paste_vice, paste_description, paste_strange_friends, paste_coin, \
    paste_stash, paste_pc_class, paste_class_description, paste_items


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
        """
        Constructor of the Human. It takes all the necessary parameters It takes as parameters all the common attributes
        of the superclass Owner and the peculiar attributes of this class, that are the pc_class, the friend and the
        enemy.

        :param name: string that represents the name of this Human.
        :param alias: string that represents the alias of this Human,
        :param look: string that string that describes the appearance of this Human.
        :param heritage: string that represents the heritage of this Human.
        :param background: string that represents the background of this Human.
        :param stress_level: int number that keeps track of the level of the stress of this Human.
        :param stress_limit: int number that the limit of the level of stress.
        :param traumas: List of strings that contains all the trauma of this Human.
        :param items: List of Items carried by this Human.
        :param harms: List of list of strings, each one representing a level of harm.
        :param healing: Clock object used to keep track of the healing progress of this Human.
        :param armors: List of boolean values that keeps track of the used armors.
        :param abilities: List of SpecialAbility objects.
        :param playbook: Playbook object to model the personal progression of this Human.
        :param attributes: List of Attribute objects used to model the attributes progression of this Human.
        :param load: int number that represents the total carried weight.
        :param xp_triggers: List of strings that represents the Xp triggers of the Human
        :param description: A string that contains a brief description of this character.
        :param downtime_activities: List that contains the downtime activities completed by this Human
        :param coin: integer value that represents the coins carried in the satchel.
        :param stash: integer value that represents the coins stored in the stash.
        :param vice: Vice object that contains all the information about the vice of this Human.
        :param pc_class: a string value that represents the class of the Human.
                It is used to extract information from the DB.
        :param friend: an NPC object that represents the friend of this Human.
        :param enemy: an NPC object that represents the friend of this Human.
        """
        if xp_triggers is None and pc_class != "":
            xp_triggers = query_xp_triggers(pc_class)

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

    def draw_image(self, **kwargs) -> bytes:
        """
        Reimplement draw_image method of IDrawable. It opens the blank sheet of this class, calls the
        paste_common_items method and finally calls the methods to paste this class' peculiar attributes.

        :param kwargs: keyword arguments.
        :return: the bytes array of the produced image.
        """
        sheet = Image.open(path_finder("images/HumanBlank.png"))

        paste_common_attributes(self, sheet, **kwargs)

        paste_pc_class(self.pc_class, sheet)
        paste_class_description(self.pc_class, sheet)

        paste_vice(self.vice, sheet)
        paste_description(self.description, sheet)
        paste_strange_friends(self.friend, self.enemy, self.pc_class, sheet)

        paste_coin(self.coin, sheet)
        paste_stash(self.stash, sheet)

        paste_items(self.items, self.pc_class, sheet)

        return image_to_bytes(sheet)

    def __repr__(self) -> str:
        return str(self.__dict__)

    def __eq__(self, o: object) -> bool:
        return isinstance(o, self.__class__) and o.__dict__ == self.__dict__
