from organization.Organization import Organization
from utility.IDrawable import IDrawable, image_to_bytes
from utility.ISavable import ISavable, pop_dict_items
from utility.imageFactory.CrewFactory import *


class Crew(Organization, ISavable, IDrawable):
    """
    The organization of the playing characters.
    """
    def __init__(self, name: str = "", type: str = "", reputation: str = "", lair: Lair = Lair(),
                 upgrades: List[Upgrade] = None, contact: NPC = NPC(), description: str = "",
                 abilities: List[SpecialAbility] = None, rep: int = 0, tier: int = 0, hold: bool = True,
                 heat: int = 0, wanted_level: int = 0, crew_exp: Playbook = Playbook(10, 0, 0),
                 cohorts: List[Cohort] = None, coins: int = 0, vault_capacity: int = 4, xp_triggers: List[str] = None,
                 prison_claims: List[Claim] = None) -> None:
        """
        Constructor of the Crew.

        :param name: string that represents the name of this Crew.
        :param type: a string value that represents the class of the Crew.
                It is used to extract information from the DB.
        :param reputation: string that represents the reputation of this Crew,
        :param lair: a Lair object that models the headquarters of the Crew
        :param upgrades: a list that contains all the Upgrades acquired by the Crew.
        :param contact: the NPC contact of the Crew.
        :param description: A string that contains a brief description of this crew.
        :param abilities: List of SpecialAbility objects.
        :param rep: an int value that represents the Rep level of the Crew.
        :param tier: an int value that represents the Tier level of the Crew.
        :param hold: a boolean value that represents the hold of the Crew: True if the hold is Strong, False if Weak.
        :param heat: an int value that represents the Heat level of the Crew
        :param wanted_level: an int value that represents the Wanted Level of the Crew
        :param crew_exp: a Playbook object that keeps track of the crew advancement.
        :param cohorts: a list that contains the Crew's cohorts.
        :param coins: an int value that represents the coins the Crew owns.
        :param vault_capacity: an int value that represents the capacity of the Crew's vault.
        :param xp_triggers: a list of strings that contains all the Crew's Xp triggers.
        :param prison_claims: a list of Claim oblects that represents the Prison Claims of the Crew
        """
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
        self.crew_exp = crew_exp
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
        if xp_triggers is None and type != "":
            xp_triggers = query_xp_triggers(type)
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
        if self.wanted_level < 0:
            self.wanted_level = 0

    def add_heat(self, heat: int) -> int:
        """
        Increases the heat of the crew.
        If the amount is greater than 9 it will add one wanted level every time the limit of 9 heat is crossed.

        :param heat: is the amount of heat to add.
        :return: the wanted level
        """
        self.heat += heat
        if self.heat >= 9:
            self.add_wanted_level(int(self.heat/9))
            self.heat %= 9
        return self.wanted_level

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
        Increases the crew's tier and calls self.update_cohorts().

        :param n: is the amount of level the crew's tier will increase.
        :return: True if the hold of the crew is True, False otherwise (and the crew's tier remains the same)
        """
        if self.hold is True:
            self.change_hold()
            self.tier += n
            self.update_cohorts()
            return True
        return False

    def upgrade_vault(self, increase: bool = True) -> int:
        """
        Increase the capacity of the vault by doubling its size.
        """
        if increase:
            self.vault_capacity *= 2
        else:
            self.vault_capacity = int(self.vault_capacity / 2)
        return self.vault_capacity

    def add_upgrade(self, upgrade: str) -> Upgrade:
        """
        Adds a new upgrade to the upgrade's list or change its quality if the upgrade is already present.

        :param upgrade: is the name of the upgrade to create/modify
        :return: the created/modified upgrade
        """
        if upgrade.lower() == "vault":
            self.upgrade_vault()
        for u in self.upgrades:
            if u.name.lower() == upgrade.lower():
                u.quality += 1
                return u
        new_upgrade = query_upgrades(upgrade, as_dict=False)[0]
        new_upgrade.quality = 1
        self.upgrades.append(new_upgrade)
        return self.upgrades[-1]

    def remove_upgrade(self, upgrade: str) -> Upgrade:
        """
        Removes an upgrade from the upgrade's list.

        :param upgrade: is the name of the upgrade to remove
        :return: the removed upgrade
        """
        if upgrade.lower() == "vault":
            self.upgrade_vault(False)
        for u in self.upgrades:
            if u.name.lower() == upgrade.lower():
                u.quality -= 1
                if u.quality == 0:
                    self.upgrades.remove(u)
                return u

    def add_cohort(self, cohort: Cohort):
        """
        Adds the given cohort to self.cohorts, then calls self.update_cohorts().
        :param cohort: the Cohort to add
        """
        self.cohorts.append(cohort)
        self.update_cohorts()

    def update_cohorts(self):
        """
        Updates all the cohort of the crew: sets the cohorts' scale and quality accordingly to the game rules.
        """
        for cohort in self.cohorts:
            if cohort.expert:
                cohort.scale = 0
                cohort.quality = self.tier + 1
            else:
                cohort.scale = self.tier
                cohort.quality = self.tier

    def change_crew_type(self, new_type: str) -> bool:
        """
        Method used to change the type of the Crew.

        :param new_type: is the new crew sheet representing the new selected type
        """
        if exists_crew(new_type):
            self.type = new_type
            self.xp_triggers = query_xp_triggers(new_type)
            return True
        return False

    @classmethod
    def from_json(cls, data: dict):
        """
        Method used to create an instance of this object given a dictionary. All the complex object that are attribute
        of this class will call their from_json class method

        :param data: dictionary of the object
        :return: Crew
        """
        dictionary = {}

        lair = Lair.from_json(data["lair"])

        if "upgrades" in data:
            dictionary["upgrades"] = list(map(Upgrade.from_json, data["upgrades"]))

        contact = NPC.from_json(data["contact"])

        abilities = list(map(SpecialAbility.from_json, data["abilities"]))

        if "cohorts" in data:
            dictionary["cohorts"] = list(map(Cohort.from_json, data["cohorts"]))

        if "crew_exp" in data:
            dictionary["crew_exp"] = Playbook.from_json(data["crew_exp"])

        if "prison_claims" in data:
            dictionary["prison_claims"] = list(map(Claim.from_json, data["prison_claims"]))

        items = list(dictionary.keys())
        items.extend(["lair", "contact", "abilities"])
        pop_dict_items(data, items)
        return cls(**data, lair=lair, contact=contact, abilities=abilities, **dictionary)

    def save_to_dict(self) -> dict:
        """
        Reimplement save_to_dict method of ISavable by changing the value of the item "contact" using the save_to_dict
        method in the NPC class

        :return: dictionary of the object
        """
        temp = super().save_to_dict()
        temp["contact"] = self.contact.save_to_dict()
        return temp

    def draw_image(self, **kwargs) -> bytes:
        """
        Reimplement draw_image method of IDrawable. It opens the blank sheet of the crew and calls the methods
        to paste this class' peculiar attributes.

        :param kwargs: keyword arguments.
        :return: the bytes array of the produced image.
        """
        sheet = Image.open(path_finder("images/CrewBlank.png"))

        paste_crew_name(self.name, sheet)
        paste_crew_reputation(self.reputation, sheet)
        paste_lair(self.lair, sheet)
        paste_crew_description(self.description, sheet)

        paste_rep(self.rep, len(self.lair.claims), sheet)
        paste_hold(self.hold, sheet)
        paste_tier(self.tier, sheet)
        paste_heat(self.heat, sheet)
        paste_wanted_level(self.wanted_level, sheet)
        paste_vault(self.coins, self.vault_capacity, sheet)

        paste_crew_type(self.type, sheet)
        paste_crew_type_description(self.type, sheet)
        paste_special_abilities(self.abilities, sheet)
        paste_xp_triggers(self.xp_triggers, sheet)
        paste_contact(self.contact, self.type, sheet)
        paste_crew_exp(self.crew_exp, sheet)
        paste_crew_upgrades(self.upgrades, self.type, sheet)
        paste_cohorts(self.cohorts, sheet)

        paste_hunting_grounds(self.type, sheet)

        paste_prison_claims(self.prison_claims, sheet)

        return image_to_bytes(sheet)

    def __repr__(self) -> str:
        return str(self.__dict__)

    def __eq__(self, o: object) -> bool:
        return isinstance(o, self.__class__) and o.__dict__ == self.__dict__
