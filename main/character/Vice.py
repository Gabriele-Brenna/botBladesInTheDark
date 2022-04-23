class Vice:
    """
    Describe what vice/need the player's character has.
    """
    def __init__(self, name: str = "", description: str = "", purveyor: str = None) -> None:
        self.name = name
        self.description = description
        self.purveyor = purveyor

    def add_purveyor(self, purveyor: str):
        """
        Adds a purveyor to the vice.

        :param purveyor: is the name of the new purveyor
        """
        self.purveyor = purveyor

    def remove_purveyor(self):
        """
        Removes the purveyor for the vice.
        """
        self.purveyor = None

    @classmethod
    def from_json(cls, data):
        """
        Method used to create an instance of this object given a dictionary

        :param data: dictionary of the object
        :return: Vice
        """
        return cls(**data)

    def __repr__(self) -> str:
        return str(self.__dict__)

    def __eq__(self, o: object) -> bool:
        return isinstance(o, self.__class__) and o.__dict__ == self.__dict__