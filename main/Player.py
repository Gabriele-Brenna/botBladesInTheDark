from typing import List

from Character import Character


class Player:
    def __init__(self, name: str, player_id: int, is_master: bool = False, characters: List[Character] = None) -> None:
        self.name = name
        self.player_id = player_id
        self.is_master = is_master
        if characters is None:
            characters = []
        self.characters = characters

    def __repr__(self) -> str:
        out = """{}:
    ID: {}
    is the GM? {}
    Characters: """.format(self.name, self.player_id, self.is_master)
        for c in self.characters:
            out += c.name + "; "
        return out
