class Upgrade:
    def __init__(self, name: str, quality: int) -> None:
        self.name = name
        self.quality = quality

    def __str__(self) -> str:
        return """Upgrade name: {}
        Quality: {}""".format(self.name, self.quality)
