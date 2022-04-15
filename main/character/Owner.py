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
        return self.coin + coins <= 4

    def can_stash_coins(self, coins: int) -> bool:
        """
        Check if a given amount of coins can be added to this Owner's stash.

        :param coins: is the amount of coins
        :return: True if the coin can be added, False otherwise
        """
        return self.stash + coins <= 40

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

    @abstractmethod
    def migrate(self, mc: super.__class__):
        pass

    @abstractmethod
    def change_pc_class(self, new_class: str):
        pass

    def __eq__(self, o: object) -> bool:
        return isinstance(o, self.__class__) and o.__dict__ == self.__dict__
