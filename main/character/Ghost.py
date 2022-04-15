from character.PC import *
from component.Clock import Clock
from controller.DBreader import *
from character.Item import Item
from character.Playbook import Playbook
from component.SpecialAbility import SpecialAbility


class Ghost(PC):
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
        self.need = query_vice("Need of Life Essence")[0]

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
        self.add_action_dots("hunt", 1)
        self.add_action_dots("prowl", 1)
        self.add_action_dots("attune", 1)

    def change_pc_class(self, new_class: str):
        pass

    def __repr__(self) -> str:
        return str(self.__dict__)

    def __eq__(self, o: object) -> bool:
        return isinstance(o, self.__class__) and o.__dict__ == self.__dict__
