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

    def test_add_type(self):
        self.gang.add_type("Rooks")
        self.assertEqual(self.gang.type, ["Thugs", "Rooks"])

    def test_add_flaw(self):
        self.expert.add_flaw("Wild")
        self.assertEqual(["Principled", "Savage", "Wild"], self.expert.flaws)

    def test_add_edge(self):
        self.expert.add_edge("Independent")
        self.assertEqual(self.expert.edges, ["Loyal", "Tenacious", "Independent"])
