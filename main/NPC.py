from Organization import Organization


class NPC:
    def __init__(self, name: str, role: str, faction: Organization) -> None:
        self.name = name
        self.role = role
        self.faction = faction

