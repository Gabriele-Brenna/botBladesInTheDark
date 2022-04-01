from typing import List

from organization.Claim import Claim


class Lair:
    """
    Is the crew hideout with all its claims
    """
    def __init__(self, location: str = "", description: str = "", claims: List[Claim] = None) -> None:
        self.location = location
        self.description = description
        if claims is None:
            claims = []
        self.claims = claims

    def __repr__(self) -> str:
        return """Location: {}
    Description: {}""".format(self.location, self.description)

    def __eq__(self, o: object) -> bool:
        return isinstance(o, self.__class__) and o.__dict__ == self.__dict__
