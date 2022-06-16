import json
from unittest import TestCase

from organization.Faction import Faction
from character.NPC import NPC
from game.Score import Score


class TestScore(TestCase):

    def setUp(self) -> None:
        self.NPC_target = NPC("Lord Helker", "Politician")
        self.NPC_faction = Faction("City Council", 5, True, )

        self.faction_target = Faction("The Hive", 4, True, "Six Towers", -1)

        self.robbery = Score("Robbery")

    def test_calc_target_tier_faction_target(self):
        self.robbery.target = self.faction_target

        self.robbery.calc_target_tier()
        self.assertEqual(4, self.robbery.target_tier)

    def test_calc_target_tier_NPC_target_without_faction(self):
        self.robbery.target = self.NPC_target

        self.robbery.calc_target_tier()
        self.assertEqual(0, self.robbery.target_tier)

    def test_calc_target_tier_NPC_target_with_faction(self):
        self.NPC_target.faction = self.NPC_faction
        self.robbery.target = self.NPC_target

        self.robbery.calc_target_tier()
        self.assertEqual(5, self.robbery.target_tier)

    def test_calc_target_tier_no_NPC_nor_faction(self):
        self.robbery.target = "Kingsman"

        self.robbery.calc_target_tier()
        self.assertEqual(1, self.robbery.target_tier)

    def test_save_and_load_json(self):
        self.score_npc = Score("Scoring", target=self.NPC_target)
        temp_str = json.dumps(self.score_npc.save_to_dict(), indent=5)
        temp_dict = json.loads(temp_str)
        temp_obj = Score.from_json(temp_dict)
        self.assertEqual(self.NPC_target.name, temp_obj.target)
        temp_obj.target = self.NPC_target
        self.assertEqual(self.score_npc, temp_obj)

        self.score_faction = Score("Breaking", target=self.faction_target)
        temp_str = json.dumps(self.score_faction.save_to_dict(), indent=5)
        temp_dict = json.loads(temp_str)
        temp_obj = Score.from_json(temp_dict)
        self.assertEqual(self.faction_target.name, temp_obj.target)
        temp_obj.target = self.faction_target
        self.assertEqual(self.score_faction, temp_obj)
