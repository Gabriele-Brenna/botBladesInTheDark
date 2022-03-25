class Action:
    def __init__(self, name: str, rating: int = 0) -> None:
        self.name = name
        self.rating = rating

    def add_dots(self, dots: int) -> bool:
        self.rating += dots
        if self.rating > 4:
            self.rating = 4
            return False
        elif self.rating < 0:
            self.rating = 0
            return False
        return True

    def __str__(self) -> str:
        return """{}: {}""".format(self.name, self.rating)
