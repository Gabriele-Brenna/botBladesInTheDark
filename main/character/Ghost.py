from character.PC import *
from component.Clock import Clock
from controller.DBreader import *
from character.Item import Item
from character.Playbook import Playbook
from component.SpecialAbility import SpecialAbility
from utility.FilesManager import path_finder
from utility.IDrawable import image_to_bytes


class Ghost(PC, ISavable):
    """
    Represents the ghost PC of the game
    """
    def __init__(self, name: str = "", alias: str = "", look: str = "",
                 heritage: str = "", background: str = "", stress_level: int = 0, stress_limit: int = 9,
                 traumas: List[str] = None, items: List[Item] = None, harms: List[List[str]] = None,
                 healing: Clock = None, armors: List[bool] = None, abilities: List[SpecialAbility] = None,
                 playbook: Playbook = Playbook(8), attributes: List[Attribute] = None,
                 load: int = 0, xp_triggers: List[str] = None, description: str = "",
                 downtime_activities: List[str] = None,
                 enemies_rivals: List[str] = None,
                 migrating_character: PC = None) -> None:
        """
        Constructor of the Ghost. It takes as parameters all the common attributes of the superclass PC and the peculiar
        attributes of this class, that are the enemies_rivals.
        It is also possible to pass only a PC object: in this case the PC will be transformed into a Ghost; all the
        attributes in common between the PC's class and this class are maintained.

        :param name: string that represents the name of this Ghost.
        :param alias: string that represents the alias of this Ghost,
        :param look: string that string that describes the appearance of this Ghost.
        :param heritage: string that represents the heritage of this Ghost.
        :param background: string that represents the background of this Ghost.
        :param stress_level: int number that keeps track of the level of the stress of this Ghost.
        :param stress_limit: int number that the limit of the level of stress.
        :param traumas: List of strings that contains all the trauma of this Ghost.
        :param items: List of Items carried by this Ghost.
        :param harms: List of list of strings, each one representing a level of harm.
        :param healing: Clock object used to keep track of the healing progress of this Ghost.
        :param armors: List of boolean values that keeps track of the used armors.
        :param abilities: List of SpecialAbility objects.
        :param playbook: Playbook object to model the personal progression of this Ghost.
        :param attributes: List of Attribute objects used to model the attributes progression of this Ghost.
        :param load: int number that represents the total carried weight.
        :param xp_triggers: List of strings that represents the Xp triggers of the Ghost
        :param description: A string that contains a brief description of this character.
        :param downtime_activities: List that contains the downtime activities completed by this Ghost
        :param enemies_rivals: List of this Ghost's enemies.
        :param migrating_character: PC object that needs to be converted into a Ghost.
        """

        if migrating_character is not None:
            self.migrate(migrating_character)

        else:
            if xp_triggers is None:
                xp_triggers = query_xp_triggers(self.__class__.__name__)

            super().__init__(name, alias, look, heritage, background, stress_level, stress_limit,
                             traumas, items, harms, healing, armors, abilities, playbook, attributes,
                             load, xp_triggers, description, downtime_activities)
        if enemies_rivals is None:
            enemies_rivals = []

        self.enemies_rivals = enemies_rivals
        self.need = query_vice(character_class=self.__class__.__name__)[0]

    def migrate(self, mc: super.__class__):
        """
        Method used to migrate a PC subclass object and convert it into a Ghost object.
        All the common attributes of the previous object are maintained and the stress level, the traumas' list
        the Items' list, the harms' list, the armors' list and the load are cleared and set to default values.
        The Special Abilities' list maintains only the abilities that are ghost related
        (i.e. that contains the "Ghost" word) and the xp_trigger list is changed according to the new triggers.
        Furthermore, the base action dot of the Ghost are added.

        :param mc: represents the migrating PC
        """

        super().__init__(mc.name, mc.alias, mc.look, mc.heritage, mc.background, 0,
                         9, None, None, None, None, None, get_class_abilities(mc.abilities, self.__class__.__name__),
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
        :return: Ghost
        """
        temp = pc_from_json(data)
        return cls(**data, **temp)

    def save_to_dict(self) -> dict:
        """
        Reimplement save_to_dict method of ISavable by adding the item "Class" at the dictionary of the object

        :return: dictionary of the object
        """
        return {**{"Class": "Ghost"}, **super().save_to_dict()}

    def draw_image(self, **kwargs) -> bytes:
        """
        Reimplement draw_image method of IDrawable. It opens the blank sheet of this class, calls the
        paste_common_items method and finally calls the methods to paste this class' peculiar attributes.

        :param kwargs: keyword arguments.
        :return: the bytes array of the produced image.
        """
        sheet = Image.open(path_finder("images/GhostBlank.png"))

        paste_common_attributes(self, sheet, **kwargs)

        paste_pc_class(self.__class__.__name__, sheet)
        paste_class_description(self.__class__.__name__, sheet)

        paste_vice(self.need, sheet)
        paste_description(self.description, sheet)
        paste_ghost_enemies(self.enemies_rivals, sheet)

        return image_to_bytes(sheet)

    def __repr__(self) -> str:
        return str(self.__dict__)

    def __eq__(self, o: object) -> bool:
        return isinstance(o, self.__class__) and o.__dict__ == self.__dict__
