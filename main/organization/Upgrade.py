class Upgrade:
    """
    Improvements of the crew
    """
    def __init__(self, name: str, quality: int) -> None:
        self.name = name
        self.quality = quality

    def __eq__(self, o: object) -> bool:
        return isinstance(o, self.__class__) and o.__dict__ == self.__dict__

    def __repr__(self) -> str:
        return """Upgrade name: {}
Quality: {}""".format(self.name, self.quality)
