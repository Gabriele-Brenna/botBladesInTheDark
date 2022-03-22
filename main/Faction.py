from Organization import Organization


class Faction(Organization):
    def __init__(self, name: str, tier: int, hold: bool, district: str, status: int):
        super().__init__(name, tier, hold)
        self.district = district
        self.status = status

    def add_tier(self, n: int):
        self.tier += n

    def add_status(self, n: int):
        self.status += n
        if self.status == -3:
            return "You are in war with {}, you reached {} status".format(self.name, self.status)
