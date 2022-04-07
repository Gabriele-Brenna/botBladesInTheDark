from typing import List

from organization.Claim import Claim
from organization.Cohort import Cohort
from organization.Lair import Lair
from character.NPC import NPC
from organization.Organization import Organization
from component.SpecialAbility import SpecialAbility
from organization.Upgrade import Upgrade


class Crew(Organization):
    """
    The organization of the playing characters.
    """
    def __init__(self, name: str = "", type: str = "", reputation: str = "", lair: Lair = Lair(),
                 upgrades: List[Upgrade] = None, contact: NPC = NPC(), description: str = "",
                 abilities: List[SpecialAbility] = None, rep: int = 0, tier: int = 0, hold: bool = True,
                 heat: int = 0, wanted_level: int = 0, exp: int = 0, cohorts: List[Cohort] = None,
                 coins: int = 0, vault_capacity: int = 4, xp_triggers: List[str] = None,
                 prison_claims: List[Claim] = None) -> None:
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
        triggers = ""  # TODO : Fetch from DB
        if xp_triggers is None:
            xp_triggers = [triggers]
        self.xp_triggers = xp_triggers
        self.prison_claims = prison_claims
        self.description = description

    def check_mastery(self) -> bool:
        """
        Checks if the upgrade "mastery" is present and has a quality of 4.

        :return: False if "mastery" is not present or the quality is not 4, True otherwise
        """
        for u in self.upgrades:
            if u.name.lower() == "mastery" and u.quality == 4:
                return True
        return False

    def add_rep(self, rep: int) -> int:
        """
        Adds rep to the crew.

        :param rep: amount of rep to add
        :return: number of coins to pay to increase the crew's tier if the rep limit is reached (12 - #claims),
        None otherwise
        """
        self.rep += rep
        if self.rep >= (12 - len(self.lair.claims)):
            self.rep %= (12 - len(self.lair.claims))
            if not self.hold:
                self.change_hold()
            else:
                return (self.tier + 1) * 8

    def calc_rep(self, score_target_tier: int) -> int:
        """
        Calculates the rep obtained after a score as follows: 2 + the target's tier - your crew's tier.

        :param score_target_tier: is the tier of the target in the score
        :return: the total amount of rep
        """
        return 2 + (score_target_tier - self.tier)

    def add_wanted_level(self, wanted_level: int):
        """
        Increases the wanted level of the crew to a maximum of four.

        :param wanted_level: is the amount of level the wanted level will be increased
        """
        self.wanted_level += wanted_level
        if self.wanted_level > 4:
            self.wanted_level = 4

    def add_heat(self, heat: int):
        """
        Increases the heat of the crew.
        If the amount is greater than 9 it will add one wanted level every time the limit of 9 heat is crossed.

        :param heat: is the amount of heat to add.
        """
        self.heat += heat
        if self.heat >= 9:
            self.add_wanted_level(int(self.heat/9))
            self.heat %= 9

    def clear_heat(self):
        """
        Clears the heat level.
        """
        self.heat = 0

    def can_store(self, coins: int) -> bool:
        """
        Checks if there is enough space in the crew's vault.

        :param coins: is the amount of coin to add.
        :return: True if there is enough space in the vault.
        """
        return 0 <= self.coins + coins <= self.vault_capacity

    def check_training(self, attribute: str) -> bool:
        """
        Check if the crew's upgrades list contains the specified training upgrade.

        :param attribute: is the name of the attribute to search the upgrade
        :return: True if the upgrade is in the list, false otherwise
        """
        for u in self.upgrades:
            if u.name.lower() == attribute.lower() and u.quality >= 1:
                return True
        return False

    def add_coin(self, coins: int) -> bool:
        """
        Adds a specified amount of coins to the vault.

        :param coins: is the amount of coins to add
        :return: True if the coins are added, False otherwise.
        """
        if self.can_store(coins):
            self.coins += coins
            return True
        return False

    def add_prison_claim(self, claim: Claim):
        """
        Adds a new Claim to the prison claims list.

        :param claim: is the new claim to add.
        """
        self.prison_claims.append(claim)

    def add_lair_claim(self, claim: Claim) -> bool:
        """
        Adds a new Claim to the lair claims list.

        :param claim: if the new claim to add
        :return: True if the claim can be added, False otherwise
        """
        if len(self.lair.claims) < 6:
            self.lair.claims.append(claim)
            return True
        return False

    def add_tier(self, n: int = 1) -> bool:
        """
        Increases the crew's tier.

        :param n: is the amount of level the crew's tier will increase.
        :return: True if the hold of the crew is True, False otherwise (and the crew's tier remains the same)
        """
        if self.hold is True:
            self.change_hold()
            self.tier += n
            return True
        return False

    def upgrade_vault(self) -> int:
        """
        Increase the capacity of the vault by doubling its size.
        """
        self.vault_capacity *= 2
        return self.vault_capacity

    def add_upgrade(self, upgrade: str) -> Upgrade:
        """
        Adds a new upgrade to the upgrade's list or change its quality if the upgrade is already present.

        :param upgrade: is the name of the upgrade to create/modify
        :return: the created/modified upgrade
        """
        for u in self.upgrades:
            if u.name.lower() == upgrade.lower():
                u.quality += 1
                return u
        self.upgrades.append(Upgrade(upgrade, 1))
        return self.upgrades[-1]

    def remove_upgrade(self, upgrade: str) -> Upgrade:
        """
        Removes an upgrade from the upgrade's list.

        :param upgrade: is the name of the upgrade to remove
        :return: the removed upgrade
        """
        for u in self.upgrades:
            if u.name.lower() == upgrade.lower():
                self.upgrades.remove(u)
                return u

    def __eq__(self, o: object) -> bool:
        return isinstance(o, self.__class__) and o.__dict__ == self.__dict__
