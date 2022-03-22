from abc import *


class Organization:
    def __init__(self, name: str, tier: int, hold: bool):
        self.name = name
        self.tier = tier
        self.hold = hold

    @abstractmethod
    def add_tier(self, n: int):
        pass

    def change_hold(self):
        self.hold = not self.hold

    def __str__(self) -> str:
        return """{}:
        Tier: {}
        Hold: {}""".format(self.name, self.tier, self.hold)
