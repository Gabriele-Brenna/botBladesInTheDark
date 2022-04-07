from character.Character import *
from component.Clock import Clock
from controller.DBreader import get_xp_triggers
from organization.Crew import Crew
from character.Item import Item
from organization.Organization import Organization
from character.Playbook import Playbook
from component.SpecialAbility import SpecialAbility
from character.Vice import Vice


class Ghost(Character):
    """
    Represents the ghost Character of the game
    """
    def __init__(self, name: str = "", faction: Organization = Crew(), role: str = "", alias: str = "", look: str = "",
                 heritage: str = "", background: str = "", stress_level: int = 0, stress_limit: int = 9,
                 traumas: List[str] = None, items: List[Item] = None, harms: List[List[str]] = None,
                 healing: Clock = None, armors: List[bool] = None, abilities: List[SpecialAbility] = None,
                 playbook: Playbook = Playbook(8), insight: Attribute = None, prowess: Attribute = None,
                 resolve: Attribute = None, load: int = 0, xp_triggers: List[str] = None, description: str = "",
                 downtime_activities: List[str] = None,
                 enemies_rivals: List[str] = None,
                 migrating_character: Character = None) -> None:

        if migrating_character is not None:
            self.migrate(migrating_character)

        else:
            super().__init__(name, faction, role, alias, look, heritage, background, stress_level, stress_limit, traumas,
                             items, harms, healing, armors, abilities, playbook, insight, prowess, resolve, load,
                             xp_triggers, description, downtime_activities)
        if enemies_rivals is None:
            enemies_rivals = []

        self.enemies_rivals = enemies_rivals
        self.need = Vice("Life Essence", """Feeding: Use a downtime activity to Hunt prey and indulge 
                             your vice. Also, when you feed,mark four ticks on your healing clock. 
                             This is the only way you can heal.""", "consumed from a living human")

    def migrate(self, mc: super.__class__):
        """
        Method used to migrate a Character subclass object and convert it into a Ghost object.
        All the common attributes of the previous object are maintained and the stress level, the traumas' list
        the Items' list, the harms' list, the armors' list and the load are cleared and set to default values.
        The Special Abilities' list maintains only the abilities that are ghost related
        (i.e. that contains the "Ghost" word) and the xp_trigger list is changed according to the new triggers.
        Furthermore, the base action dot of the Ghost are added.

        :param mc: represents the migrating Character
        """

        super().__init__(mc.name, mc.faction, mc.role, mc.alias, mc.look, mc.heritage, mc.background, 0,
                         9, None, None, None, None, None, get_class_abilities(mc.abilities, self.__class__.__name__),
                         mc.playbook, mc.insight, mc.prowess, mc.resolve, 0, get_xp_triggers(self.__class__.__name__),
                         mc.description, None)
        self.insight.action_dots("hunt", 1)
        self.prowess.action_dots("prowl", 1)
        self.resolve.action_dots("attune", 1)

    def change_pc_class(self, new_class: str):
        pass

    def __repr__(self) -> str:
        return str(self.__dict__)

    def __eq__(self, o: object) -> bool:
        return isinstance(o, self.__class__) and o.__dict__ == self.__dict__
