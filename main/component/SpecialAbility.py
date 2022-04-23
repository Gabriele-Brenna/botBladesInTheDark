class SpecialAbility:
    """
    The special abilities of the game
    """
    def __init__(self, name: str, description: str) -> None:
        self.name = name
        self.description = description

    @classmethod
    def from_json(cls, data):
        """
        Method used to create an instance of this object given a dictionary

        :param data: dictionary of the object
        :return: SpecialAbility
        """
        return cls(**data)

    def __repr__(self) -> str:
        return """{}:
    {}""".format(self.name, self.description)

    def __eq__(self, o: object) -> bool:
        return isinstance(o, self.__class__) and self.name.lower() == o.name.lower() and \
               self.description.lower() == o.description.lower()
