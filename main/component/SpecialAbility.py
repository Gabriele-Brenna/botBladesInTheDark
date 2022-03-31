class SpecialAbility:
    def __init__(self, name: str, description: str) -> None:
        self.name = name
        self.description = description

    def __repr__(self) -> str:
        return """{}:
    {}""".format(self.name, self.description)

    def __eq__(self, o: object) -> bool:
        return isinstance(o, self.__class__) and self.name.lower() == o.name.lower() and \
               self.description.lower() == o.description.lower()
