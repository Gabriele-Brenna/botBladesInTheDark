from unittest import TestCase

from organization.Cohort import Cohort


class TestCohort(TestCase):

    def setUp(self) -> None:
        self.gang = Cohort(["Thugs"], 0, False, 1, False, ["Unreliable"], ["Loyal"], 2, 2)
        self.expert = Cohort(["Physician"], 1, False, 0, True, ["Principled", "Savage"], ["Loyal", "Tenacious"], 3, 0)

    def test_add_harm(self):
        self.gang.add_harm(1)
        self.assertEqual(self.gang.harm, 2)

    def test_heal_harm(self):
        self.gang.add_harm(-1)
        self.assertEqual(self.gang.harm, 0)

    def test_add_harm_out_of_bound(self):
        self.gang.add_harm(10)
        self.assertEqual(self.gang.harm, 4)

        self.expert.add_harm(-10)
        self.assertEqual(self.expert.harm, 0)

    def test_add_type(self):
        self.gang.add_type("Rooks")
        self.assertEqual(self.gang.type, ["Thugs", "Rooks"])

    def test_add_flaw(self):
        self.expert.add_flaw("Wild")
        self.assertEqual(["Principled", "Savage", "Wild"], self.expert.flaws)

    def test_add_edge(self):
        self.expert.add_edge("Independent")
        self.assertEqual(self.expert.edges, ["Loyal", "Tenacious", "Independent"])

    def test_add_armor(self):
        self.gang.add_armor(1000)
        self.assertEqual(self.gang.armor, 99)
        self.gang.add_armor(-100)
        self.assertEqual(self.gang.armor, 0)
