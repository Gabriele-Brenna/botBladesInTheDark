import os
import pathlib
from pathlib import Path


class Journal:
    def __init__(self, name: str = "Journal", notes: [] = None) -> None:
        file_name = name + ".txt"
        ROOT_DIR = Path(__file__).parent.parent.resolve()
        ROOT_DIR = os.path.join(ROOT_DIR, "resources")
        self.name = os.path.join(ROOT_DIR, file_name)
        file = open(self.name, 'w')
        file.close()
        if notes is None:
            notes = []
        self.notes = notes

    def delete_note(self, number: int = 1):
        if len(self.notes) > 1:
            if number in range(len(self.notes)+1):
                self.notes.pop(-number)
        elif len(self.notes) == 1:
            self.notes.pop(0)

    def edit_note(self, note: str, number: int = 1):
        if len(self.notes) > 1:
            if number in range(len(self.notes)+1):
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
