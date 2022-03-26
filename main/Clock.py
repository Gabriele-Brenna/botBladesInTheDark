class Clock:

    def __init__(self, name: str = "", segments: int = 4, progress: int = 0) -> None:
        self.name = name
        self.segments = segments
        self.progress = progress

    def tick(self, ticks: int) -> bool:
        self.progress += ticks
        if self.progress < 0:
            self.progress = 0
        return self.progress >= self.segments

    def edit(self, name: str = None, segments: int = None):
        if name is not None:
            self.name = name
        if segments is not None:
            self.segments = segments

    def __repr__(self) -> str:
        return """{}: 
    segments: {}
    progress: {}""".format(self.name, self.segments, self.progress)


