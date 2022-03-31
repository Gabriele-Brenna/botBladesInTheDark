from typing import List

from character.Action import Action
from character.Playbook import Playbook


class Attribute(Playbook):
    def __init__(self, actions: List[Action], exp_limit: int, exp: int = 0, points: int = 0) -> None:
        super().__init__(exp_limit, exp, points)
        self.actions = actions

    def get_attribute_level(self) -> int:
        level = 0
        for a in self.actions:
            if a.rating > 0:
                level += 1
        return level

    def action_dots(self, action: str, dots: int) -> bool:
        for a in self.actions:
            if a.name.lower() == action.lower():
                return a.add_dots(dots)
        raise Exception("{} doesn't exit".format(action))

    def get_action_rating(self, action: str) -> int:
        for a in self.actions:
            if a.name.lower() == action.lower():
                return a.rating
        raise Exception("{} doesn't exit".format(action))

    def __repr__(self) -> str:
        return str(self.__dict__)

    def __eq__(self, o: object) -> bool:
        return isinstance(o, self.__class__) and o.__dict__ == self.__dict__
