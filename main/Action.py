class Action:
    def __init__(self, name: str, rating: int = 0, limit: int = 4) -> None:
        self.name = name
        self.rating = rating
        self.limit = limit

    def add_dots(self, dots: int) -> bool:
        self.rating += dots
        if self.rating > self.limit:
            self.rating = self.limit
            return False
        elif self.rating < 0:
            self.rating = 0
            return False
        return True

    def __repr__(self) -> str:
        return """{}: {}""".format(self.name, self.rating)

    def __eq__(self, o: object) -> bool:
        return isinstance(o, self.__class__) and o.__dict__ == self.__dict__