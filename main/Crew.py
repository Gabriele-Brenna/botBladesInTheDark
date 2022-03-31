from typing import List

from Claim import Claim
from Cohort import Cohort
from Lair import Lair
from NPC import NPC
from Organization import Organization
from SpecialAbility import SpecialAbility
from Upgrade import Upgrade


class Crew(Organization):
    def __init__(self, name: str = "", type: str = "", reputation: str = "", lair: Lair = Lair(),
                 upgrades: List[Upgrade] = None, contact: NPC = NPC(), description: str = "",
                 abilities: List[SpecialAbility] = None, rep: int = 0, tier: int = 0, hold: bool = True,
                 heat: int = 0, wanted_level: int = 0, exp: int = 0, cohorts: List[Cohort] = None,
                 coins: int = 0, vault_capacity: int = 4, prison_claims: List[Claim] = None) -> None:
        super().__init__(name, tier, hold)
        self.type = type
        if abilities is None:
            abilities = []
        self.abilities = abilities
        self.reputation = reputation
        self.lair = lair
        self.rep = rep
        self.heat = heat
        self.wanted_level = wanted_level
        self.exp = exp
        if cohorts is None:
            cohorts = []
        self.cohorts = cohorts
        if upgrades is None:
            upgrades = []
        self.upgrades = upgrades
        self.contact = contact
        self.coins = coins
        self.vault_capacity = vault_capacity
        if prison_claims is None:
            prison_claims = []
        self.prison_claims = prison_claims
        self.description = description

    def check_mastery(self) -> bool:
        for u in self.upgrades:
            if u.name.lower() == "mastery" and u.quality == 4:
                return True
        return False

    def add_rep(self, rep: int) -> int:
        self.rep += rep
        if self.rep >= (12 - len(self.lair.claims)):
            self.rep %= (12 - len(self.lair.claims))
            if not self.hold:
                self.change_hold()
            else:
                return (self.tier + 1) * 8

    # TODO: def calc_rep(self, score: Score)

    def add_wanted_level(self, wanted_level: int):
        self.wanted_level += wanted_level
        if self.wanted_level > 4:
            self.wanted_level = 4

    def add_heat(self, heat: int):
        self.heat += heat
        if self.heat >= 9:
            self.add_wanted_level(int(self.heat/9))
            self.heat %= 9

    def clear_heat(self):
        self.heat = 0

    def can_store(self, coins: int) -> bool:
        return 0 <= self.coins + coins <= self.vault_capacity

    def check_training(self, attribute: str) -> bool:
        for u in self.upgrades:
            if u.name.lower() == attribute.lower() and u.quality >= 1:
                return True
        return False

    def add_coin(self, coins: int) -> bool:
        if self.can_store(coins):
            self.coins += coins
            return True
        return False

    def add_prison_claim(self, claim: Claim):
        self.prison_claims.append(claim)

    def add_lair_claim(self, claim: Claim) -> bool:
        if len(self.lair.claims) < 6:
            self.lair.claims.append(claim)
            return True
        return False

    def add_tier(self, n: int = 1) -> bool:
        if self.hold is True:
            self.change_hold()
            self.tier += n
            return True
        return False

    def upgrade_vault(self) -> int:
        self.vault_capacity *= 2
        return self.vault_capacity

    def add_upgrade(self, upgrade: str) -> Upgrade:
        for u in self.upgrades:
            if u.name.lower() == upgrade.lower():
                u.quality += 1
                return u
        self.upgrades.append(Upgrade(upgrade, 1))
        return self.upgrades[-1]

    def remove_upgrade(self, upgrade: str) -> Upgrade:
        for u in self.upgrades:
            if u.name.lower() == upgrade.lower():
                self.upgrades.remove(u)
                return u

    def __eq__(self, o: object) -> bool:
        return isinstance(o, self.__class__) and o.__dict__ == self.__dict__
