from organization.Organization import Organization


class Faction(Organization):
    """
    The organization of the NPC's
    """
    def __init__(self, name: str = "", tier: int = 1, hold: bool = True, district: str = "", status: int = 0) -> None:
        super().__init__(name, tier, hold)
        self.district = district
        self.status = status

    def add_tier(self, n: int):
        """
        Adds the specified number of tier

        :param n: the number of tier to add
        """
        self.tier += n

    def add_status(self, n: int) -> int:
        """
        Adds the selected status level

        :param n: the status to add
        :return: the new reached status
        """
        self.status += n
        if self.status > 3:
            self.status = 3
        if self.status < -3:
            self.status = -3
        return self.status

    @classmethod
    def from_json(cls, data):
        return cls(**data)

    def __repr__(self) -> str:
        return super().__repr__() + """
    District: {}
    Status: {}
        """.format(self.district, self.status)

    def __eq__(self, o: object) -> bool:
        return isinstance(o, self.__class__) and o.__dict__ == self.__dict__
