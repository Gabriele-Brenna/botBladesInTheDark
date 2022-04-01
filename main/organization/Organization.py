from abc import *


class Organization:
    """
    A group of scoundrels
    """
    def __init__(self, name: str, tier: int, hold: bool) -> None:
        self.name = name
        self.tier = tier
        self.hold = hold

    @abstractmethod
    def add_tier(self, n: int):
        pass

    def change_hold(self):
        """
        Switches the hold boolean value
        """
        self.hold = not self.hold

    def __repr__(self) -> str:
        return """{}:
    Tier: {}
    Hold: {}""".format(self.name, self.tier, self.hold)

    def __eq__(self, o: object) -> bool:
        return isinstance(o, self.__class__) and o.__dict__ == self.__dict__
