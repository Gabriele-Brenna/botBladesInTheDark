class Claim:
    """
    Territories, facilities and favours claimed by the Crew
    """
    def __init__(self, name: str = "Turf", description: str = "") -> None:
        self.name = name
        self.description = description

    @classmethod
    def from_json(cls, data):
        """
        Method used to create an instance of this object given a dictionary

        :param data: dictionary of the object
        :return: Claim
        """
        return cls(**data)

    def __repr__(self) -> str:
        return """{}:
    {}""".format(self.name, self.description)

    def __eq__(self, o: object) -> bool:
        return isinstance(o, self.__class__) and o.__dict__ == self.__dict__
