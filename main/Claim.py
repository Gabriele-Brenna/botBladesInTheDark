class Claim:
    def __init__(self, name: str = "Turf", description: str = "") -> None:
        self.name = name
        self.description = description

    def __repr__(self) -> str:
        return """{}:
    {}""".format(self.name, self.description)
