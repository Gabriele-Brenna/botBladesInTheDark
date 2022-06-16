from typing import List, Union

from organization.Faction import Faction
from character.NPC import NPC
from utility.ISavable import ISavable


class Score(ISavable):
    """
    Models the score activity of the game
    """
    def __init__(self, title: str = "Score", participants: List[str] = None, target_tier: int = 0,
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

    @classmethod
    def from_json(cls, data):
        """
        Method used to create an instance of this object given a dictionary

        :param data: dictionary of the object
        :return: Score
        """
        return cls(**data)

    def save_to_dict(self) -> dict:
        """
        Reimplement save_to_dict method of ISavable by removing setting the value of the item "target" in the object
        dictionary only to the name of the attribute target

        :return: dictionary of the object
        """
        temp = super().save_to_dict()
        temp["target"] = self.target.name if isinstance(self.target, NPC) or isinstance(self.target,
                                                                                        Faction) else self.target
        return temp

    def __eq__(self, o: object) -> bool:
        return isinstance(o, self.__class__) and o.__dict__ == self.__dict__
