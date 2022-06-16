from character.PC import *
from component.Clock import Clock
from controller.DBreader import *
from character.Item import Item
from character.NPC import NPC
from character.Owner import Owner
from character.Playbook import Playbook
from component.SpecialAbility import SpecialAbility
from utility.FilesManager import path_finder
from utility.IDrawable import image_to_bytes
from utility.ISavable import pop_dict_items


class Vampire(Owner, ISavable):
    """
    Represents the vampire PC of the game
    """

    def __init__(self, name: str = "", alias: str = "", look: str = "",
                 heritage: str = "", background: str = "", stress_level: int = 0, stress_limit: int = 12,
                 traumas: List[str] = None, items: List[Item] = None, harms: List[List[str]] = None,
                 healing: Clock = None, armors: List[bool] = None, abilities: List[SpecialAbility] = None,
                 playbook: Playbook = Playbook(8), attributes: List[Attribute] = None,
                 load: int = 0, xp_triggers: List[str] = None, description: str = "",
                 downtime_activities: List[str] = None, coin: int = 0, stash: int = 0,
                 strictures: List[SpecialAbility] = None, dark_servants: List[NPC] = None,
                 migrating_character: PC = None) -> None:
        """
        Constructor of the Vampire. It takes as parameters all the common attributes of the superclass Owner and the
        peculiar attributes of this class, that are the strictures and the dark_servants.
        It is also possible to pass only a PC object: in this case the PC will be transformed into a Vampire; all the
        attributes in common between the PC's class and this class are maintained.

        :param name: string that represents the name of this Vampire.
        :param alias: string that represents the alias of this Vampire,
        :param look: string that string that describes the appearance of this Vampire.
        :param heritage: string that represents the heritage of this Vampire.
        :param background: string that represents the background of this Vampire.
        :param stress_level: int number that keeps track of the level of the stress of this Vampire.
        :param stress_limit: int number that the limit of the level of stress.
        :param traumas: List of strings that contains all the trauma of this Vampire.
        :param items: List of Items carried by this Vampire.
        :param harms: List of list of strings, each one representing a level of harm.
        :param healing: Clock object used to keep track of the healing progress of this Vampire.
        :param armors: List of boolean values that keeps track of the used armors.
        :param abilities: List of SpecialAbility objects.
        :param playbook: Playbook object to model the personal progression of this Vampire.
        :param attributes: List of Attribute objects used to model the attributes progression of this Vampire.
        :param load: int number that represents the total carried weight.
        :param xp_triggers: List of strings that represents the Xp triggers of the Vampire
        :param description: A string that contains a brief description of this character.
        :param downtime_activities: List that contains the downtime activities completed by this Vampire
        :param coin: integer value that represents the coins carried in the satchel.
        :param stash: integer value that represents the coins stored in the stash.
        :param strictures: List of SpecialAbility object representing the Vampir's strictures.
        :param dark_servants: List of NPC containing all the servants of this Vampire.
        :param migrating_character: PC object that needs to be converted into a Ghost.
        """

        if migrating_character is not None:
            self.migrate(migrating_character)

        else:
            if xp_triggers is None:
                xp_triggers = query_xp_triggers(self.__class__.__name__)

            super().__init__(name, alias, look, heritage, background, stress_level, stress_limit,
                             traumas,
                             items, harms, healing, armors, abilities, playbook, attributes, load,
                             xp_triggers, description, downtime_activities, coin, stash,
                             vice=query_vice(character_class=self.__class__.__name__)[0])
        self.playbook.exp_limit = 10
        for attr in self.attributes:
            attr.exp_limit = 8

        for attr in self.attributes:
            for action in attr.actions:
                action.limit = 5

        if traumas is not None:
            self.traumas = traumas

        if strictures is None:
            strictures = []
        self.strictures = strictures
        if dark_servants is None:
            dark_servants = [NPC(), NPC()]
        self.dark_servants = dark_servants

    def migrate(self, mc: super.__class__):
        """
        Method used to migrate a PC subclass object and convert it into a Vampire object.
        All the common attributes of the previous object are maintained and the stress level, the traumas' list
        the Items' list, the harms' list, the armors' list and the load are cleared and set to default values.
        The Special Abilities' list maintains only the abilities that are ghost related
        (i.e. that contains the "Ghost" word, except for "Ghost Form")
        and the xp_trigger list is changed according to the new triggers.
        Furthermore, the base action dot of the Vampire are added.

        :param mc: represents the migrating PC
        """

        super().__init__(mc.name, mc.alias, mc.look, mc.heritage, mc.background, 0,
                         12, None, None, None, None, None, get_class_abilities(mc.abilities, self.__class__.__name__),
                         mc.playbook, mc.attributes, 0, query_xp_triggers(self.__class__.__name__),
                         mc.description, None)
        add_initial_dots(self, self.__class__.__name__)

    def change_pc_class(self, new_class: str):
        pass

    @classmethod
    def from_json(cls, data: dict):
        """
        Method used to create an instance of this object given a dictionary. All the complex object that are attribute
        of this class will call their from_json class method

        :param data: dictionary of the object
        :return: Vampire
        """
        temp = pc_from_json(data)
        dark_servants = list(map(NPC.from_json, data["dark_servants"]))
        strictures = list(map(SpecialAbility.from_json, data["strictures"]))
        pop_dict_items(data, ["vice", "dark_servants", "strictures"])
        return cls(**data, **temp, dark_servants=dark_servants, strictures=strictures)

    def save_to_dict(self) -> dict:
        """
        Reimplement save_to_dict method of ISavable by adding the item "Class" at the dictionary of the object and
        removing the Faction from the dictionary of the NPCs contained in the attribute dark_servants.

        :return: dictionary of the object
        """
        temp = super().save_to_dict()
        temp["dark_servants"] = []
        for i in self.dark_servants:
            temp["dark_servants"].append(i.save_to_dict())
        return {**{"Class": "Vampire"}, **temp}

    def draw_image(self, **kwargs) -> bytes:
        """
        Reimplement draw_image method of IDrawable. It opens the blank sheet of this class, calls the
        paste_common_items method and finally calls the methods to paste this class' peculiar attributes.

        :param kwargs: keyword arguments.
        :return: the bytes array of the produced image.
        """
        sheet = Image.open(path_finder("images/VampireBlank.png"))

        paste_common_attributes(self, sheet, **kwargs)

        paste_pc_class(self.__class__.__name__, sheet)
        paste_class_description(self.__class__.__name__, sheet)

        paste_vice(self.vice, sheet)
        paste_description(self.description, sheet, 320)
        paste_vampire_servants(self.dark_servants, sheet)
        paste_vampire_strictures(self.strictures, sheet)

        paste_coin(self.coin, sheet)
        paste_stash(self.stash, sheet)

        paste_items(self.items, self.__class__.__name__, sheet)

        return image_to_bytes(sheet)

    def __repr__(self) -> str:
        return str(self.__dict__)

    def __eq__(self, o: object) -> bool:
        return isinstance(o, self.__class__) and o.__dict__ == self.__dict__
