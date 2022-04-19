class Action:
    """
    Models an action that the player can use to achieve a goal.
    The more dots the action has, the more efficient the PC will be while performing that specific action.
    """
    def __init__(self, name: str, rating: int = 0, limit: int = 4) -> None:
        self.name = name
        self.rating = rating
        self.limit = limit

    def add_dots(self, dots: int) -> bool:
        """
        Adds or removes the specified number of dots to this action, checking that the final dots' number is between
        0 and the action limit value.

        :param dots: the number of dots to add or remove
        :return: True if the addition or removal keeps the dots' number in the limits
        """
        self.rating += dots
        if self.rating > self.limit:
            self.rating = self.limit
            return False
        elif self.rating < 0:
            self.rating = 0
            return False
        return True

    @classmethod
    def from_json(cls, data):
        return cls(**data)

    def __repr__(self) -> str:
        return """{}: {}""".format(self.name, self.rating)

    def __eq__(self, o: object) -> bool:
        return isinstance(o, self.__class__) and o.__dict__ == self.__dict__