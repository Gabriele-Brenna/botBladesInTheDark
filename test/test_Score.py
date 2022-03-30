from unittest import TestCase

from Faction import Faction
from NPC import NPC
from Score import Score


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

