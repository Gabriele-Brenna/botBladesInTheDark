from unittest import TestCase

from HarmBox import HarmBox


class TestHarmBox(TestCase):

    def setUp(self) -> None:
        self.empty = HarmBox()
        self.one_full = HarmBox([["Battered", "Drained"], [], []])
        self.two_full = HarmBox([[], ["Exhausted", "Concussion"], []])
        self.three_full = HarmBox([[], [], ["Impaled"]])
        self.all_full = HarmBox([["Scared", "Battered"], ["Seduced", "Exhausted"], ["Terrified"]])

    def test_insert_harm(self):
        self.empty.insert_harm(3, "Broken Leg")
        self.assertEqual(["Broken Leg"], self.empty.harms[2])
        self.empty.insert_harm(1, "Distracted")
        self.assertEqual(["Distracted"], self.empty.harms[0])
        self.empty.insert_harm(2, "Deep Cut to Arm")
        self.assertEqual(["Deep Cut to Arm"], self.empty.harms[1])
        self.assertEqual([["Distracted"], ["Deep Cut to Arm"], ["Broken Leg"]], self.empty.harms)

    def test_insert_harm_full_level(self):
        lvl = self.one_full.insert_harm(1, "Distracted")
        self.assertEqual(2, lvl)
        self.assertEqual(["Distracted"], self.one_full.harms[1])
        self.assertEqual(["Battered", "Drained"], self.one_full.harms[0])
        lvl = self.two_full.insert_harm(2, "Deep Cut to Arm")
        self.assertEqual(3, lvl)
        self.assertEqual(["Deep Cut to Arm"], self.two_full.harms[2])
        self.assertEqual(["Exhausted", "Concussion"], self.two_full.harms[1])
        lvl = self.three_full.insert_harm(3, "Broken Leg")
        self.assertEqual(4, lvl)
        self.assertEqual(["Impaled"], self.three_full.harms[2])

    def test_insert_harm_all_full(self):
        lvl = self.all_full.insert_harm(1, "Distracted")
        self.assertEqual(4, lvl)
        self.assertEqual([["Scared", "Battered"], ["Seduced", "Exhausted"], ["Terrified"]], self.all_full.harms)

    def test_single_heal_harm(self):
        self.empty.heal_harm()
        self.assertEqual([[], [], []], self.empty.harms)
        self.one_full.heal_harm()
        self.assertEqual([[], [], []], self.one_full.harms)
        self.two_full.heal_harm()
        self.assertEqual([["Exhausted", "Concussion"], [], []], self.two_full.harms)
        self.three_full.heal_harm()
        self.assertEqual([[], ["Impaled"], []], self.three_full.harms)

    def test_heal_all_harms(self):
        for i in range(3):
            self.all_full.heal_harm()
        self.assertEqual([[], [], []], self.all_full.harms)

    def test_count_harm(self):
        for i in range(3):
            count = self.empty.count_harm(i+1)
            self.assertEqual(0, count)
        count = self.all_full.count_harm(1)
        self.assertEqual(2, count)
        count = self.all_full.count_harm(2)
        self.assertEqual(2, count)
        count = self.all_full.count_harm(3)
        self.assertEqual(1, count)
