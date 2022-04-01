import os
from pathlib import Path
from typing import List

index = 1


class Journal:
    """
    Keeps track of what happens in the game by writing it in a text file.
    """
    def __init__(self, name: str = None, notes: List[str] = None) -> None:
        if name is None:
            global index
            file_name = "Journal{}.txt".format(str(index))
            index += 1
            # TODO: path finder
            root_dir = Path(__file__).parent.parent.parent.resolve()
            root_dir = os.path.join(root_dir, "resources")
            self.name = os.path.join(root_dir, file_name)
        else:
            self.name = name
        file = open(self.name, 'w')
        file.close()
        if notes is None:
            notes = []
        self.notes = notes

    def delete_note(self, number: int = 1):
        """
        Allows to delete a specified note, depending on its position inside the list of notes.

        :param number: is the position of the note. It's given starting from the most recent to the oldest one,
        meaning the note 1 is the last note written
        """
        if len(self.notes) > 1:
            if number in range(len(self.notes) + 1):
                self.notes.pop(-number)
        elif len(self.notes) == 1:
            self.notes.pop(0)

    def edit_note(self, note: str, number: int = 1):
        """
        Allows to change a specified note, depending on its position inside the list of notes.

        :param note: is the new note that will be written
        :param number: is the position of the note. It's given starting from the most recent to the oldest one,
        meaning the note 1 is the last note written
        """
        if len(self.notes) > 1:
            if number in range(len(self.notes) + 1):
                self.notes[-number] = note
        else:
            self.notes[0] = note

    def read_journal(self) -> str:
        """
        Allows the read everything that has been written so far.

        :return: a string containing all that it is written in the text file plus all the notes added after it
        """
        with open(self.name, 'r') as f:
            out = f.read()
        for s in self.notes:
            out = out + s + '.\n'
        return out

    def append(self, new_note: str):
        """
        Adds a new note at the end of the notes' list. If the total amount of notes in the list
        is greater than 5 after adding the new note,
        the oldest note (the first of the list) is written in the text file and removed from the list.

        :param new_note: it's the new note
        """
        self.notes.append(new_note)
        if len(self.notes) > 5:
            with open(self.name, "a") as f:
                f.write(self.notes[0] + '.\n')
            self.notes.pop(0)

    def save_notes(self):
        """
        Writes all the notes of the notes' list in the text file, then clears the list.
        """
        for s in self.notes:
            with open(self.name, 'a') as f:
                f.write(s + '.\n')
        self.notes.clear()

    def rewrite_file(self, new_file: str = ""):
        """
        Rewrites the text file with new content.

        :param new_file: is a string containing the content that will be written in the text file
        """
        with open(self.name, 'w') as f:
            f.write(new_file)

    def __eq__(self, o: object) -> bool:
        return isinstance(o, self.__class__) and o.__dict__ == self.__dict__
