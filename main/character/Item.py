class Item:
    def __init__(self, name: str, description: str, weight: int = 0, usages: int = -1, quality: int = 1) -> None:
        self.name = name
        self.description = description
        self.weight = weight
        self.usages = usages
        self.quality = quality

    def use(self) -> bool:
        if self.usages > 0:
            self.usages -= 1
            return True
        elif self.usages == 0:
            return False
        elif self.usages == -1:
            return True

    def __eq__(self, o: object) -> bool:
        return isinstance(o, self.__class__) and o.__dict__ == self.__dict__
