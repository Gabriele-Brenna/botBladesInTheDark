from typing import List, Union

from Character import Character
from Faction import Faction
from NPC import NPC


class Score:
    def __init__(self, title: str = "Score", participants: List[Character] = None, target_tier: int = 0,
                 target: Union[NPC, Faction] = NPC()) -> None:
        self.title = title
        self.participants = participants
        self.target_tier = target_tier
        self.target = target

    def calc_target_tier(self):
        if isinstance(self.target, Faction):
            self.target_tier = self.target.tier
        elif isinstance(self.target, NPC):
            if self.target.faction is not None:
                self.target_tier = self.target.faction.tier
        else:
            self.target_tier = 1
