class Vice:

    def __init__(self, name: str, description: str, purveyor: str) -> None:
        self.name = name
        self.description = description
        self.purveyor = purveyor

    def add_purveyor(self, purveyor: str):
        self.purveyor = purveyor

    def remove_purveyor(self):
        self.purveyor = None

