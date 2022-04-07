from character.Character import *
from component.Clock import Clock
from organization.Crew import Crew
from character.Item import Item
from organization.Organization import Organization
from character.Playbook import Playbook
from component.SpecialAbility import SpecialAbility


class Hull(Character):
    """
    Represents the hull Character of the game
    """

    def __init__(self, name: str = "", faction: Organization = Crew(), role: str = "", alias: str = "", look: str = "",
                 heritage: str = "", background: str = "", stress_level: int = 0, stress_limit: int = 10,
                 traumas: List[str] = None, items: List[Item] = None, harms: List[List[str]] = None,
                 healing: Clock = None, armors: List[bool] = None, abilities: List[SpecialAbility] = None,
                 playbook: Playbook = Playbook(8), insight: Attribute = None, prowess: Attribute = None,
                 resolve: Attribute = None, load: int = 0, xp_triggers: List[str] = None, description: str = "",
                 downtime_activities: List[str] = None, functions: List[str] = None, frame: str = "small",
                 migrating_character: Character = None) -> None:

        if migrating_character is not None:
            self.migrate(migrating_character)

        else:
            super().__init__(name, faction, role, alias, look, heritage, background, stress_level, stress_limit,
                             traumas,
                             items, harms, healing, armors, abilities, playbook, insight, prowess, resolve, load,
                             xp_triggers, description, downtime_activities)

        if functions is None:
            functions = []
        self.functions = functions
        self.frame = frame

    def migrate(self, mc: super.__class__):
        """
        Method used to migrate a Character subclass object and convert it into a Hull object.
        All the common attributes of the previous object are maintained and the stress level, the traumas' list
        the Items' list, the harms' list, the armors' list and the load are cleared and set to default values.
        The Special Abilities' list maintains only the abilities that are ghost related
        (i.e. that contains the "Ghost" word, except for "Ghost Form")
        and the xp_trigger list is changed according to the new triggers.
        Furthermore, the base action dot of the Hull are added.

        :param mc: represents the migrating Character
        """
        hull_xp_triggers = mc.xp_triggers[:1]
        # TODO : hull_xp_triggers.append( FETCH FROM DB )

        super().__init__(mc.name, mc.faction, mc.role, mc.alias, mc.look, mc.heritage, mc.background, 0,
                         10, None, None, None, None, None, get_class_abilities(mc.abilities, self.__class__.__name__),
                         mc.playbook, mc.insight, mc.prowess, mc.resolve, 0, hull_xp_triggers, mc.description,
                         None)
        self.prowess.action_dots("skirmish", 1)
        self.resolve.action_dots("attune", 1)

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

    def __repr__(self) -> str:
        return str(self.__dict__)

    def __eq__(self, o: object) -> bool:
        return isinstance(o, self.__class__) and o.__dict__ == self.__dict__
