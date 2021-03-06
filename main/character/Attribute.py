from typing import List

from character.Action import Action
from character.Playbook import Playbook
from utility.ISavable import pop_dict_items


class Attribute(Playbook):
    """
    Models the player's characteristics. Allows the player to resist bad consequences
    """
    def __init__(self, name: str, actions: List[Action], exp_limit: int = 6, exp: int = 0,
                 points: int = 0) -> None:
        super().__init__(exp_limit, exp, points)
        self.name = name
        self.actions = actions

    def attribute_level(self) -> int:
        """
        Compute the level of this attribute based on how many of its actions have a rating greater than 0.

        :return: this attribute's level
        """
        level = 0
        for a in self.actions:
            if a.rating > 0:
                level += 1
        return level

    def action_dots(self, action: str, dots: int) -> bool:
        """
        Adds a given amount of action dots to a specific action, increasing  or decreasing its action rating.
        If the action is not present it raises and exception.

        :param action: the name of the action whose rating will be changed
        :param dots: the amount of dots to add or remove
        :return: True if the action rating has been changed, False otherwise
        """
        for a in self.actions:
            if a.name.lower() == action.lower():
                return a.add_dots(dots)

    def action_rating(self, action: str) -> int:
        """
        Gets a given action from the list of this attribute's actions.
        If the action is not present it raises an exception.

        :param action: the name of the action to find in the attribute
        :return: the action rating of the found action
        """
        for a in self.actions:
            if a.name.lower() == action.lower():
                return a.rating
        raise Exception("{} doesn't exit".format(action))

    @classmethod
    def from_json(cls, data):
        """
        Method used to create an instance of this object given a dictionary. Since it has a list of Actions as an
        attribute it will call the from_json method of the class Action

        :param data: dictionary of the object
        :return: Attribute
        """
        actions = list(map(Action.from_json, data["actions"]))
        pop_dict_items(data, ["actions"])
        return cls(**data, actions=actions)

    def __repr__(self) -> str:
        return str(self.__dict__)

    def __eq__(self, o: object) -> bool:
        return isinstance(o, self.__class__) and o.__dict__ == self.__dict__
