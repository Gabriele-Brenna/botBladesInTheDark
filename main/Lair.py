from typing import List

from Claim import Claim


class Lair:
    def __init__(self, location: str, description: str, claims: List[Claim]) -> None:
        self.location = location
        self.description = description
        self.claims = claims

    def __str__(self) -> str:
        return """Location: {}
        Description: {}
        """.format(self.location, self.description)
