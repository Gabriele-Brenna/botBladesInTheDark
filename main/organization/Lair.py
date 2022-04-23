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

    @classmethod
    def from_json(cls, data):
        """
        Method used to create an instance of this object given a dictionary. For the list of Claims, that are a complex
        object, class the class method from_json in the Claim

        :param data: dictionary of the object
        :return: Lair
        """
        claims = list(map(Claim.from_json, data["claims"]))
        data.pop("claims")
        return cls(**data, claims=claims)

    def __repr__(self) -> str:
        return """Location: {}
    Description: {}""".format(self.location, self.description)

    def __eq__(self, o: object) -> bool:
        return isinstance(o, self.__class__) and o.__dict__ == self.__dict__