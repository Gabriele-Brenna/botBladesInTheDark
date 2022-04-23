from utility.ISavable import ISavable


class Item(ISavable):
    """
    Models what the player can use during the game.
    """
    def __init__(self, name: str, description: str, weight: int = 0, usages: int = -1, quality: int = 1) -> None:
        self.name = name
        self.description = description
        self.weight = weight
        self.usages = usages
        self.quality = quality

    def use(self) -> bool:
        """
        Allows the use of this item, depending on how many usages it has left.

        :return: True if this item can be used (usages greater than zero or equal to -1), False if it can't be used
        """
        if self.usages > 0:
            self.usages -= 1
            return True
        elif self.usages == 0:
            return False
        elif self.usages == -1:
            return True

    @classmethod
    def from_json(cls, data):
        """
        Method used to create an instance of this object given a dictionary

        :param data: dictionary of the object
        :return: Item
        """
        return cls(**data)

    def __eq__(self, o: object) -> bool:
        return isinstance(o, self.__class__) and o.__dict__ == self.__dict__
