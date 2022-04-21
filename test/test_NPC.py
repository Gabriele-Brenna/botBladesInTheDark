import json
from unittest import TestCase

from character.NPC import NPC
from organization.Faction import Faction


class TestNPC(TestCase):
    def setUp(self) -> None:
        self.rail_jacks = Faction("Rail Jacks", 2, False, "Labor & Trade")
        self.bob = NPC("Bob", "The Builder", self.rail_jacks, "Can we fix it? Yes we can")

    def test_save_and_load_json(self):
        temp_str = json.dumps(self.bob.save_to_dict(), indent=5)
        temp_dict = json.loads(temp_str)
        temp_obj = NPC.from_json(temp_dict)
        self.assertEqual(self.bob.faction.name, temp_obj.faction)
        temp_obj.faction = self.rail_jacks
        self.assertEqual(self.bob, temp_obj)
