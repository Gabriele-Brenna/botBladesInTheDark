class SpecialAbility:
    def __init__(self, name: str, description: str) -> None:
        self.name = name
        self.description = description

    def __str__(self) -> str:
        return """{}:
        {}""".format(self.name, self.description)
