class Upgrade:
    """
    Improvements of the crew
    """
    def __init__(self, name: str, quality: int, tot_quality: int) -> None:
        self.name = name
        self.quality = quality
        self.tot_quality = tot_quality

    @classmethod
    def from_json(cls, data):
        """
        Method used to create an instance of this object given a dictionary

        :param data: dictionary of the object
        :return: Upgrade
        """
        return cls(**data)

    def __eq__(self, o: object) -> bool:
        return isinstance(o, self.__class__) and o.__dict__ == self.__dict__

    def __repr__(self) -> str:
        return """Upgrade name: {}
Quality: {}""".format(self.name, self.quality)
