class Claim:
    def __init__(self, name: str = "Turf", description: str = "") -> None:
        self.name = name
        self.description = description

    def __repr__(self) -> str:
        return """{}:
    {}""".format(self.name, self.description)

    def __eq__(self, o: object) -> bool:
        return isinstance(o, self.__class__) and o.__dict__ == self.__dict__
