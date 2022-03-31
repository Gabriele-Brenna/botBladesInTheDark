import os
import unittest
from pathlib import Path
from unittest import TestCase

from game.Journal import Journal


class TestJournal(TestCase):
    def setUp(self) -> None:
        root_dir = Path(__file__).parent.resolve()
        root_dir = os.path.join(root_dir, "resources_test")
        name = os.path.join(root_dir, "test.txt")
        self.file = Journal(name, ["Hello", "everybody"])

    def test_delete_note(self):
        self.file.delete_note(2)
        self.file.delete_note()
        self.assertEqual([], self.file.notes)
        self.file.delete_note()
        self.assertEqual([], self.file.notes)

    def test_edit_note(self):
        self.file.edit_note("world", 1)
        self.file.edit_note("Bye", 2)
        self.assertEqual(["Bye", "world"], self.file.notes)

    def test_append(self):
        self.file.append("and")
        self.file.append("welcome")
        self.file.append("to")
        self.assertEqual(["Hello", "everybody", "and", "welcome", "to"], self.file.notes)
        self.file.append("Blades in the Dark")
        self.assertEqual(["everybody", "and", "welcome", "to", "Blades in the Dark"], self.file.notes)
        with open(self.file.name, 'r') as f:
            self.assertEqual("Hello.\n", f.read())
        self.file.append("the best")
        self.assertEqual(["and", "welcome", "to", "Blades in the Dark", "the best"], self.file.notes)
        with open(self.file.name, 'r') as f:
            self.assertEqual("Hello.\neverybody.\n", f.read())
        self.assertEqual(5, len(self.file.notes))

    def test_read_journal(self):
        self.file.append("and")
        self.file.append("welcome")
        self.file.append("to")
        self.assertEqual("Hello.\neverybody.\nand.\nwelcome.\nto.\n", self.file.read_journal())
        self.file.append("Blades in the Dark")
        self.assertEqual("Hello.\neverybody.\nand.\nwelcome.\nto.\nBlades in the Dark.\n", self.file.read_journal())

    def test_save_notes(self):
        self.file.append("and welcome to Blades in the dark")
        self.assertEqual(["Hello", "everybody", "and welcome to Blades in the dark"], self.file.notes)
        self.file.save_notes()
        with open(self.file.name, 'r') as f:
            self.assertEqual("Hello.\neverybody.\nand welcome to Blades in the dark.\n", f.read())
        self.assertEqual([], self.file.notes)
        self.file.save_notes()
        with open(self.file.name, 'r') as f:
            self.assertEqual("Hello.\neverybody.\nand welcome to Blades in the dark.\n", f.read())

    def test_rewrite_file(self):
        self.file.save_notes()
        self.file.rewrite_file("Welcome to Blades in the dark.\n")
        with open(self.file.name, 'r') as f:
            self.assertEqual("Welcome to Blades in the dark.\n", f.read())

    @unittest.skip("default")
    def test_default(self):
        for i in range(5):
            self.default = Journal()
