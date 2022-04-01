from typing import List

from character.Character import Character
from character.Ghost import Ghost
from character.Hull import Hull
from character.Vampire import Vampire


class Player:
    """
    Represents the human user.
    """
    def __init__(self, name: str, player_id: int, is_master: bool = False, characters: List[Character] = None) -> None:
        self.name = name
        self.player_id = player_id
        self.is_master = is_master
        if characters is None:
            characters = []
        self.characters = characters

    def migrate_character_type(self, name: str, new_type: str) -> bool:
        """
        Allows to change the specified character into the selected new type

        :param name: the name of the character to change
        :param new_type: the type you want to transform into (ghost, vampire, hull)
        :return: True if the new type and the character's name selected exist, False otherwise
        """
        for c in self.characters:
            if c.name.lower() == name.lower():
                new_c = None
                if new_type.lower() == "ghost":
                    new_c = Ghost(migrating_character=c)
                if new_type.lower() == "vampire":
                    new_c = Vampire(migrating_character=c)
                if new_type.lower() == "hull":
                    new_c = Hull(migrating_character=c)
                self.characters[self.characters.index(c)] = new_c
                return True
        return False

    def get_character_by_name(self, name: str) -> Character:
        """
        Gets the character with the selected name.

        :param name: the name of the character
        :return: the selected character, None otherwise
        """
        for c in self.characters:
            if c.name.lower() == name.lower():
                return c

    def __repr__(self) -> str:
        out = """{}:
    ID: {}
    is the GM? {}
    Characters: """.format(self.name, self.player_id, self.is_master)
        for c in self.characters:
            out += c.name + "; "
        return out

    def __eq__(self, o: object) -> bool:
        return isinstance(o, self.__class__) and o.__dict__ == self.__dict__
