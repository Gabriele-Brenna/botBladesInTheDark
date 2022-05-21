from character.PC import *
from component.Clock import Clock
from controller.DBreader import query_xp_triggers
from character.Item import Item
from character.Playbook import Playbook
from component.SpecialAbility import SpecialAbility
from utility.IDrawable import image_to_bytes
from utility.ISavable import pop_dict_items


class Hull(PC, ISavable):
    """
    Represents the hull PC of the game
    """

    def __init__(self, name: str = "", alias: str = "", look: str = "",
                 heritage: str = "", background: str = "", stress_level: int = 0, stress_limit: int = 10,
                 traumas: List[str] = None, items: List[Item] = None, harms: List[List[str]] = None,
                 healing: Clock = None, armors: List[bool] = None, abilities: List[SpecialAbility] = None,
                 playbook: Playbook = Playbook(8), attributes: List[Attribute] = None, load: int = 0,
                 xp_triggers: List[str] = None, description: str = "",
                 downtime_activities: List[str] = None, functions: List[str] = None, frame: str = "small",
                 frame_features: List[SpecialAbility] = None, migrating_character: PC = None) -> None:

        if migrating_character is not None:
            self.migrate(migrating_character)

        else:
            if xp_triggers is None:
                xp_triggers = query_xp_triggers(self.__class__.__name__)

            super().__init__(name, alias, look, heritage, background, stress_level, stress_limit,
                             traumas,
                             items, harms, healing, armors, abilities, playbook, attributes, load,
                             xp_triggers, description, downtime_activities)

        if functions is None:
            functions = []
        self.functions = functions
        self.frame = frame
        if frame_features is None:
            frame_features = []
        self.frame_features = frame_features

    def migrate(self, mc: super.__class__):
        """
        Method used to migrate a PC subclass object and convert it into a Hull object.
        All the common attributes of the previous object are maintained and the stress level, the traumas' list
        the Items' list, the harms' list, the armors' list and the load are cleared and set to default values.
        The Special Abilities' list maintains only the abilities that are ghost related
        (i.e. that contains the "Ghost" word, except for "Ghost Form")
        and the xp_trigger list is changed according to the new triggers.
        Furthermore, the base action dot of the Hull are added.

        :param mc: represents the migrating PC
        """

        super().__init__(mc.name, mc.alias, mc.look, mc.heritage, mc.background, 0,
                         10, None, None, None, None, None, get_class_abilities(mc.abilities, self.__class__.__name__),
                         mc.playbook, mc.attributes, 0, query_xp_triggers(self.__class__.__name__),
                         mc.description, None)
        add_initial_dots(self, self.__class__.__name__)

    def change_pc_class(self, new_class: str):
        pass

    def select_frame(self, frame_type: str) -> bool:
        """
        Allows the selection of the frame for your Hull.

        :param frame_type: is the selected type of frame
        :return: True if a correct frame type was given, False otherwise
        """
        if frame_type.lower() == "small" or "medium" or "large" or "s" or "m" or "l":
            self.frame = frame_type
            return True
        return False

    @classmethod
    def from_json(cls, data: dict):
        """
        Method used to create an instance of this object given a dictionary. All the complex object that are attribute
        of this class will call their from_json class method

        :param data: dictionary of the object
        :return: Hull
        """
        temp = pc_from_json(data)
        frame_features = list(map(SpecialAbility.from_json, data["frame_features"]))
        pop_dict_items(data, ["frame_features"])
        return cls(**data, **temp, frame_features=frame_features)

    def save_to_dict(self) -> dict:
        """
        Reimplement save_to_dict method of ISavable by adding the item "Class" at the dictionary of the object

        :return: dictionary of the object
        """
        return {**{"Class": "Hull"}, **super().save_to_dict()}

    def draw_image(self, **kwargs) -> bytes:
        """
        Reimplement draw_image method of IDrawable. It opens the blank sheet of this class, calls the
        paste_common_items method and finally calls the methods to paste this class' peculiar attributes.

        :param kwargs: keyword arguments.
        :return: the bytes array of the produced image.
        """
        sheet = Image.open(path_finder("images/HullBlank.png"))

        paste_common_attributes(self, sheet, **kwargs)

        paste_pc_class(self.__class__.__name__, sheet)
        paste_class_description(self.__class__.__name__, sheet)

        paste_hull_functions(self.functions, sheet)
        paste_description(self.description, sheet, 360)
        paste_hull_frame(self.frame, sheet)
        paste_hull_frame_features(self.frame_features, sheet)

        return image_to_bytes(sheet)

    def __repr__(self) -> str:
        return str(self.__dict__)

    def __eq__(self, o: object) -> bool:
        return isinstance(o, self.__class__) and o.__dict__ == self.__dict__
