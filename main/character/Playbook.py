class Playbook:
    """
    Models the base PC's progression layer.
    When an advance is taken from this track a new special ability can be obtained
    """

    def __init__(self, exp_limit: int, exp: int = 0, points: int = 0) -> None:
        self.exp_limit = exp_limit
        self.points = points
        self.exp = 0
        self.add_exp(exp)

    def add_points(self, points: int) -> bool:
        """
        Adds or removes the specified number of points from this Playbook.
        It also checks that the points do not go below zero.

        :param points: is the number of points to add or remove
        :return: True if the operation can be fulfilled, False otherwise.
        """
        self.points += points
        if self.points < 0:
            self.points = 0
            return False
        return True

    def add_exp(self, exp: int) -> bool:
        """
        Adds the specified number of experience points to this Playbook.
        It also handles the points overflow, by adding as many points to this Playbook as many times the experience
        level crosses the experience limit.

        :param exp: is the number of experience to add
        :return: the return value of add_points method if the experience level crosses the experience limit,
        False otherwise
        """
        self.exp += exp
        if self.exp >= self.exp_limit:
            i = self.exp
            self.exp %= self.exp_limit
            return self.add_points(int(i/self.exp_limit))
        return False

    def __repr__(self) -> str:
        return str(self.__dict__)

    def __eq__(self, o: object) -> bool:
        return isinstance(o, self.__class__) and o.__dict__ == self.__dict__
