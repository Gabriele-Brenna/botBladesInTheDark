class Playbook:

    def __init__(self, exp_limit: int, exp: int = 0, points: int = 0) -> None:
        self.exp_limit = exp_limit
        self.points = points
        self.exp = 0
        self.add_exp(exp)

    def add_points(self, points: int) -> bool:
        self.points += points
        if self.points < 0:
            self.points = 0
            return False
        return True

    def add_exp(self, exp: int) -> bool:
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
