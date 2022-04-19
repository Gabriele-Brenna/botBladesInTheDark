from utility.ISavable import ISavable


class Clock(ISavable):
    """
    Represent the clocks of the game used to keep track of complex events
    """

    def __init__(self, name: str = "", segments: int = 4, progress: int = 0) -> None:
        self.name = name
        self.segments = segments
        self.progress = progress

    def tick(self, ticks: int) -> bool:
        """
        Advances the clock progress

        :param ticks: how many ticks need to be added
        :return: True if the clock's segments are all filled, False otherwise
        """
        self.progress += ticks
        if self.progress < 0:
            self.progress = 0
        return self.progress >= self.segments

    def edit(self, name: str = None, segments: int = None):
        """
        Allows to edit the name and/or the number of segments of the clock.

        :param name: the new name of the clock
        :param segments: the new number of segments
        """
        if name is not None:
            self.name = name
        if segments is not None:
            self.segments = segments

    @classmethod
    def from_json(cls, data):
        return cls(**data)

    def __repr__(self) -> str:
        return """{}: 
    segments: {}
    progress: {}""".format(self.name, self.segments, self.progress)

    def __eq__(self, o: object) -> bool:
        return isinstance(o, self.__class__) and o.__dict__ == self.__dict__
