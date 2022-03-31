from organization.Organization import Organization


class NPC:
    def __init__(self, name: str = "", role: str = "", faction: Organization = None) -> None:
        self.name = name
        self.role = role
        self.faction = faction

    def __repr__(self) -> str:
        return str(self.__dict__)

    def __eq__(self, o: object) -> bool:
        return isinstance(o, self.__class__) and o.__dict__ == self.__dict__
