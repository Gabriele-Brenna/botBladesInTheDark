from Character import *
from Clock import Clock
from Crew import Crew
from Item import Item
from Organization import Organization
from Playbook import Playbook
from SpecialAbility import SpecialAbility
from Vice import Vice


class Ghost(Character):
    def __init__(self, name: str = "", faction: Organization = Crew(), role: str = "", alias: str = "", look: str = "",
                 heritage: str = "", background: str = "", stress_level: int = 0, stress_limit: int = 9,
                 traumas: List[str] = None, items: List[Item] = None, harms: List[List[str]] = None,
                 healing: Clock = None, armors: List[bool] = None, abilities: List[SpecialAbility] = None,
                 playbook: Playbook = Playbook(8), insight: Attribute = None, prowess: Attribute = None,
                 resolve: Attribute = None, load: int = 0, xp_triggers: List[str] = None, notes: str = "",
                 downtime_activities: List[str] = None,
                 enemies_rivals: List[str] = None,
                 migrating_character: Character = None) -> None:

        if migrating_character is not None:
            self.migrate(migrating_character)

        else:
            super().__init__(name, faction, role, alias, look, heritage, background, stress_level, stress_limit, traumas,
                             items, harms, healing, armors, abilities, playbook, insight, prowess, resolve, load,
                             xp_triggers, notes, downtime_activities)
        if enemies_rivals is None:
            enemies_rivals = []

        self.enemies_rivals = enemies_rivals
        self.need = Vice("Life Essence", """Feeding: Use a downtime activity to Hunt prey and indulge 
                             your vice. Also, when you feed,mark four ticks on your healing clock. 
                             This is the only way you can heal.""", "consumed from a living human")

    def migrate(self, mc: super.__class__):
        ghost_abilities = get_ghost_abilities(mc.abilities)

        # TODO : fetch "Ghost Form" ability from DB
        ghost_abilities.append(SpecialAbility("Ghost Form", ""))

        ghost_xp_triggers = mc.xp_triggers[:1]
        # TODO : ghost_xp_triggers.append( FETCH FROM DB )

        super().__init__(mc.name, mc.faction, mc.role, mc.alias, mc.look, mc.heritage, mc.background, 0,
                         9, None, None, None, None, None, ghost_abilities,
                         mc.playbook, mc.insight, mc.prowess, mc.resolve, 0, ghost_xp_triggers, mc.notes,
                         None)
        self.insight.action_dots("hunt", 1)
        self.prowess.action_dots("prowl", 1)
        self.resolve.action_dots("attune", 1)

    def __repr__(self) -> str:
        return str(self.__dict__)

    def __eq__(self, o: object) -> bool:
        return isinstance(o, self.__class__) and o.__dict__ == self.__dict__
