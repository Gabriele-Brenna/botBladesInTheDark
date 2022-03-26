from typing import List

from Claim import Claim


class Lair:
    def __init__(self, location: str = "", description: str = "", claims: List[Claim] = None) -> None:
        self.location = location
        self.description = description
        if claims is None:
            claims = []
        self.claims = claims

    def __repr__(self) -> str:
        return """Location: {}
    Description: {}""".format(self.location, self.description)
