from character.PC import *
from component.Clock import Clock
from character.Item import Item
from character.Playbook import Playbook
from component.SpecialAbility import SpecialAbility
from character.Vice import Vice


class Owner(PC):
    """
    Represents all the playable races that are able to own and use items.
    """
    def __init__(self, name: str = "", alias: str = "", look: str = "",
                 heritage: str = "", background: str = "", stress_level: int = 0, stress_limit: int = 9,
                 traumas: List[str] = None, items: List[Item] = None, harms: List[List[str]] = None,
                 healing: Clock = None, armors: List[bool] = None, abilities: List[SpecialAbility] = None,
                 playbook: Playbook = Playbook(8), attributes: List[Attribute] = None,
                 load: int = 0, xp_triggers: List[str] = None, description: str = "",
                 downtime_activities: List[str] = None,
                 coin: int = 0, stash: int = 0, vice: Vice = Vice()) -> None:
        """
        Constructor of the Owner class. It takes as parameters all the common attributes of the superclass PC and
        defines a type of PC that can own and handle coins and possessions.

        :param name: string that represents the name of this Owner.
        :param alias: string that represents the alias of this Owner,
        :param look: string that string that describes the appearance of this Owner.
        :param heritage: string that represents the heritage of this Owner.
        :param background: string that represents the background of this Owner.
        :param stress_level: int number that keeps track of the level of the stress of this Owner.
        :param stress_limit: int number that the limit of the level of stress.
        :param traumas: List of strings that contains all the trauma of this Owner.
        :param items: List of Items carried by this Owner.
        :param harms: List of list of strings, each one representing a level of harm.
        :param healing: Clock object used to keep track of the healing progress of this Owner.
        :param armors: List of boolean values that keeps track of the used armors.
        :param abilities: List of SpecialAbility objects.
        :param playbook: Playbook object to model the personal progression of this Owner.
        :param attributes: List of Attribute objects used to model the attributes progression of this Owner.
        :param load: int number that represents the total carried weight.
        :param xp_triggers: List of strings that represents the Xp triggers of the Owner.
        :param description: A string that contains a brief description of this character.
        :param downtime_activities: List that contains the downtime activities completed by this Owner.
        :param coin: integer value that represents the coins carried in the satchel.
        :param stash: integer value that represents the coins stored in the stash.
        :param vice: Vice object that contains all the information about the vice of this Owner.
        """
        super().__init__(name, alias, look, heritage, background, stress_level, stress_limit, traumas,
                         items, harms, healing, armors, abilities, playbook, attributes, load,
                         xp_triggers, description, downtime_activities)
        self.coin = coin
        self.stash = stash
        self.vice = vice

    def can_have_coins(self, coins: int) -> bool:
        """
        Check if a given amount of coins can be added to this Owner.

        :param coins: is the amount of coins
        :return: True if the coin can be added, False otherwise
        """
        return 0 <= self.coin + coins <= 4

    def can_stash_coins(self, coins: int) -> bool:
        """
        Check if a given amount of coins can be added to this Owner's stash.

        :param coins: is the amount of coins
        :return: True if the coin can be added, False otherwise
        """
        return 0 <= self.stash + coins <= 40

    def can_store_coins(self, coins: int) -> bool:
        """
        Check if a given amount of coins can be subdivided into this Owner's coins and stash.

        :param coins: is the amount of coins
        :return: True if the coin can be added, False otherwise
        """
        free_purse_space = 4 - self.coin
        free_stash_space = 40 - self.stash

        return coins <= (free_stash_space + free_purse_space)

    def add_coins(self, coins: int) -> bool:
        """
        Adds a given amount of coins to the Owner.

        :param coins: is the amount of coins
        :return: True if the coins can be added, False otherwise.
        """
        if self.can_have_coins(coins):
            self.coin += coins
            return True
        return False

    def stash_coins(self, coins: int) -> bool:
        """
        Adds a given amount of coins the Owner's stash.

        :param coins: coins: is the amount of coins
        :return: True if the coins can be added, False otherwise.
        """
        if self.can_stash_coins(coins):
            self.stash += coins
            return True
        return False

    def store_coins(self, coins: int) -> bool:
        if not self.can_store_coins(coins):
            return False

        for i in range(coins):
            if not self.add_coins(1):
                self.stash_coins(1)

        return True

    def pay_coins(self, coins: int) -> bool:
        for i in range(coins):
            if not self.add_coins(-1):
                if not self.stash_coins(-2):
                    return False
        return True

    @abstractmethod
    def migrate(self, mc: super.__class__):
        pass

    @abstractmethod
    def change_pc_class(self, new_class: str):
        pass

    def __eq__(self, o: object) -> bool:
        return isinstance(o, self.__class__) and o.__dict__ == self.__dict__
