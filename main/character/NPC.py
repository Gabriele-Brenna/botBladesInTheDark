import copy

from character.Character import Character
from organization.Organization import Organization
from utility.ISavable import ISavable


class NPC(Character, ISavable):
    """
    Non-Playable-PC of the game.
    """

    def __init__(self, name: str = "", role: str = "", faction: Organization = None, description: str = "") -> None:
        super().__init__(name, description)
        self.role = role
        self.faction = faction

    @classmethod
    def from_json(cls, data):
        return cls(**data)

    def save_to_dict(self) -> dict:
        temp = super().save_to_dict()
        if self.faction is not None:
            temp["faction"] = self.faction.name
        return temp

    def __repr__(self) -> str:
        return str(self.__dict__)

    def __eq__(self, o: object) -> bool:
        return isinstance(o, self.__class__) and o.__dict__ == self.__dict__
