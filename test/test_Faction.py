from unittest import TestCase

from organization.Faction import Faction


class TestFaction(TestCase):
    def setUp(self) -> None:
        self.faction = Faction("fazione1", 1, True, "Charhollow", 2)

    def test_add_tier(self):
        self.faction.add_tier(4)
        print(self.faction)

        self.assertEqual(5, self.faction.tier)

    def test_add_status(self):
        self.assertEqual(3, self.faction.add_status(2))

    def test_add_status_war(self):
        self.faction.add_status(-5)
        self.assertEqual(-3,
                         self.faction.add_status(-5))

        self.assertEqual(-3, self.faction.status)
