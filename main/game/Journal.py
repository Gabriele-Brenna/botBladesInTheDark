import os
from pathlib import Path
from typing import List

index = 1


class Journal:
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
        if len(self.notes) > 1:
            if number in range(len(self.notes) + 1):
                self.notes.pop(-number)
        elif len(self.notes) == 1:
            self.notes.pop(0)

    def edit_note(self, note: str, number: int = 1):
        if len(self.notes) > 1:
            if number in range(len(self.notes) + 1):
                self.notes[-number] = note
        else:
            self.notes[0] = note

    def read_journal(self) -> str:
        with open(self.name, 'r') as f:
            out = f.read()
        for s in self.notes:
            out = out + s + '.\n'
        return out

    def append(self, new_note: str):
        self.notes.append(new_note)
        if len(self.notes) > 5:
            with open(self.name, "a") as f:
                f.write(self.notes[0] + '.\n')
            self.notes.pop(0)

    def save_notes(self):
        for s in self.notes:
            with open(self.name, 'a') as f:
                f.write(s + '.\n')
        self.notes.clear()

    def rewrite_file(self, new_file: str = ""):
        with open(self.name, 'w') as f:
            f.write(new_file)

    def __eq__(self, o: object) -> bool:
        return isinstance(o, self.__class__) and o.__dict__ == self.__dict__
