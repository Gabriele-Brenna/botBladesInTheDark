class Character:
    """
    Generic character of the game.
    """
    def __init__(self, name: str = "", description: str = "") -> None:
        self.name = name
        self.description = description

    def __repr__(self) -> str:
        return str(self.__dict__)

    def __eq__(self, o: object) -> bool:
        return isinstance(o, self.__class__) and o.__dict__ == self.__dict__
