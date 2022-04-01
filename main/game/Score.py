from typing import List, Union

from character.Character import Character
from organization.Faction import Faction
from character.NPC import NPC


class Score:
    """
    Models the score activity of the game
    """
    def __init__(self, title: str = "Score", participants: List[Character] = None, target_tier: int = 0,
                 target: Union[NPC, Faction] = NPC()) -> None:
        self.title = title
        if participants is None:
            participants = []
        self.participants = participants
        self.target_tier = target_tier
        self.target = target

    def calc_target_tier(self):
        """
        Evaluates the tier of the Score's target:

        if the target is a Faction, its tier attribute is used;

        if the target is an NPC and a member of a Faction, the Faction's tier attribute is used;

        if the target is an NPC with no links to any Organization, the default value(1) is used

        """
        if isinstance(self.target, Faction):
            self.target_tier = self.target.tier
        elif isinstance(self.target, NPC):
            if self.target.faction is not None:
                self.target_tier = self.target.faction.tier
        else:
            self.target_tier = 1

    def __eq__(self, o: object) -> bool:
        return isinstance(o, self.__class__) and o.__dict__ == self.__dict__
