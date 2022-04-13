from character.PC import *
from component.Clock import Clock
from controller.DBreader import *
from character.Item import Item
from character.NPC import NPC
from character.Owner import Owner
from character.Playbook import Playbook
from component.SpecialAbility import SpecialAbility


class Vampire(Owner):
    """
    Represents the vampire PC of the game
    """

    def __init__(self, name: str = "", alias: str = "", look: str = "",
                 heritage: str = "", background: str = "", stress_level: int = 0, stress_limit: int = 12,
                 traumas: List[str] = None, items: List[Item] = None, harms: List[List[str]] = None,
                 healing: Clock = None, armors: List[bool] = None, abilities: List[SpecialAbility] = None,
                 playbook: Playbook = Playbook(8), insight: Attribute = None, prowess: Attribute = None,
                 resolve: Attribute = None, load: int = 0, xp_triggers: List[str] = None, description: str = "",
                 downtime_activities: List[str] = None, coin: int = 0, stash: int = 0,
                 strictures: List[str] = None, dark_servants: List[NPC] = None,
                 migrating_character: PC = None) -> None:

        if migrating_character is not None:
            self.migrate(migrating_character)

        else:
            if xp_triggers is None:
                xp_triggers = query_xp_triggers(self.__class__.__name__)

            super().__init__(name, alias, look, heritage, background, stress_level, stress_limit,
                             traumas,
                             items, harms, healing, armors, abilities, playbook, insight, prowess, resolve, load,
                             xp_triggers, description, downtime_activities, coin, stash,
                             vice=query_vice("Life Essence")[0])
        self.playbook.exp_limit = 10
        self.prowess.exp_limit = 8
        self.insight.exp_limit = 8
        self.resolve.exp_limit = 8

        for action in (self.insight.actions + self.prowess.actions + self.resolve.actions):
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
                         mc.playbook, mc.insight, mc.prowess, mc.resolve, 0, query_xp_triggers(self.__class__.__name__),
                         mc.description, None)

        self.insight.action_dots("hunt", 1)
        self.prowess.action_dots("prowl", 1)
        self.prowess.action_dots("skirmish", 1)
        self.resolve.action_dots("attune", 1)
        self.resolve.action_dots("command", 1)
        self.resolve.action_dots("sway", 1)

    def change_pc_class(self, new_class: str):
        pass

    def __repr__(self) -> str:
        return str(self.__dict__)

    def __eq__(self, o: object) -> bool:
        return isinstance(o, self.__class__) and o.__dict__ == self.__dict__
