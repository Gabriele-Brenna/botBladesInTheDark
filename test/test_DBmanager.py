from unittest import TestCase

from controller.DBmanager import *
from controller.DBwriter import insert_game


class TestDBmanager(TestCase):
    def setUp(self) -> None:
        self.connection = establish_connection()
        self.cursor = self.connection.cursor()

    def test_exists_character(self):
        self.assertTrue(exists_character("Hound"))
        self.assertFalse(exists_character("Dark Elf"))

    def test_exists_crew(self):
        self.assertTrue(exists_crew("Cult"))
        self.assertFalse(exists_crew("Whalers"))

    def test_exists_game(self):
        insert_game(1, "Game1", 1)

        self.assertTrue(exists_game(1))
        self.assertFalse(exists_game(2))

        self.cursor.execute("DELETE FROM Game WHERE Game_ID = 1")
        self.connection.commit()

    def test_is_json(self):
        self.assertTrue(is_json('{"Assassins": "Hit man"}'))
        self.assertFalse(is_json('Assassins: Hit man'))

    def test_exists_user_in_game(self):
        pass

    def test_exists_upgrade(self):
        self.assertEqual("Assassin's Rigging (2 free load of weapons or gear)", exists_upgrade("assassin's rigging"))

        self.assertIsNone(exists_upgrade("Car"))
