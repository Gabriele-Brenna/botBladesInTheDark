from unittest import TestCase

from character.Character import Character
from character.Item import Item


class TestCharacter(TestCase):
    def setUp(self) -> None:
        self.character = Character(items=[Item("knife", "miracle blade", 1),
                                          Item("grenade", "art is an explosion", 2, 2)],
                                   load=4, armors=[True, True, False],
                                   description="first")
        self.deadManWalking = Character(harms=[["Scared", "Battered"], ["Seduced", "Exhausted"], ["Terrified"]],
                                        stress_level=9,
                                        traumas=["cold", "haunted", "soft", "paranoid"])

    def test_add_stress(self):
        self.character.add_stress(5)
        self.assertEqual(5, self.character.stress_level)

        self.assertEqual(1, self.character.add_stress(5))
        self.assertEqual(1, self.character.stress_level)

        self.assertEqual(2, self.deadManWalking.add_stress(12))
        self.assertEqual(3, self.deadManWalking.stress_level)

    def test_clear_stress(self):
        self.assertFalse(self.deadManWalking.clear_stress(7))
        self.assertEqual(2, self.deadManWalking.stress_level)

        self.assertTrue(self.deadManWalking.clear_stress(3))
        self.assertEqual(0, self.deadManWalking.stress_level)

    def test_add_trauma(self):
        self.assertTrue(self.character.add_trauma("cold"))
        self.assertTrue(self.character.add_trauma("reckless"))
        self.assertEqual(["cold", "reckless"], self.character.traumas)

        self.assertFalse(self.deadManWalking.add_trauma("unstable"))

    def test_add_harm(self):
        self.assertEqual(3, self.character.add_harm(3, "Broken Leg"))
        self.assertEqual(["Broken Leg"], self.character.harms[2])
        self.character.add_harm(1, "Distracted")
        self.assertEqual(["Distracted"], self.character.harms[0])
        self.character.add_harm(2, "Deep Cut to Arm")
        self.assertEqual(["Deep Cut to Arm"], self.character.harms[1])
        self.assertEqual([["Distracted"], ["Deep Cut to Arm"], ["Broken Leg"]], self.character.harms)

    def test_add_harm_full_level(self):

        self.character.harms = [["Scared", "Battered"], ["Seduced"], []]

        self.assertEqual(2, self.character.add_harm(1, "Broken leg"))
        self.assertEqual([["Scared", "Battered"], ["Seduced", "Broken leg"], []], self.character.harms)

        self.assertEqual(3, self.character.add_harm(1, "Twisted ankle"))
        self.assertEqual([["Scared", "Battered"], ["Seduced", "Broken leg"], ["Twisted ankle"]], self.character.harms)

        self.assertEqual(4, self.character.add_harm(1, "sneeze"))

    def test_heal_harms(self):
        self.character.heal_harms()
        self.assertEqual([[], [], []], self.character.harms)

        self.deadManWalking.heal_harms()
        self.assertEqual([["Seduced", "Exhausted"], ["Terrified"], []], self.deadManWalking.harms)

    def test_count_harms(self):
        for i in range(3):
            count = self.character.count_harms(i + 1)
            self.assertEqual(0, count)
        count = self.deadManWalking.count_harms(1)
        self.assertEqual(2, count)
        count = self.deadManWalking.count_harms(2)
        self.assertEqual(2, count)
        count = self.deadManWalking.count_harms(3)
        self.assertEqual(1, count)

    def test_recover(self):
        self.deadManWalking.recover()
        self.assertEqual([[], [], []], self.deadManWalking.harms)

    def test_clear_consumable(self):
        self.character.clear_consumable()

        self.assertEqual(0, self.character.load)
        self.assertEqual([], self.character.items)
        self.assertEqual([False, False, False], self.character.armors)

    def test_use_armor(self):
        self.assertFalse(self.character.use_armor("underwear"))
        self.assertFalse(self.character.use_armor("standard"))

        self.assertTrue(self.character.use_armor("Special"))

    def test_has_item(self):
        self.assertEqual(0, self.character.has_item(Item("knife", "miracle blade", 1)))
        self.assertIsNone(self.deadManWalking.has_item(Item("Luck Charm", "")))

    def test_carried_load(self):
        self.assertEqual(3, self.character.carried_load())

        self.assertEqual(0, self.deadManWalking.carried_load())

    def test_use_item(self):
        self.assertTrue(self.character.use_item(Item("burglary gear", "", 1)))
        self.assertFalse(self.character.use_item(Item("pistol", "", 1)))

        self.assertTrue(self.character.use_item(Item("grenade", "art is an explosion", 2, 2)))
        self.assertTrue(self.character.use_item(Item("grenade", "art is an explosion", 2, 2)))
        self.assertFalse(self.character.use_item(Item("grenade", "art is an explosion", 2, 2)))

        self.assertTrue(self.deadManWalking.use_item(Item("Luck Charm", "")))

        self.assertEqual([Item("knife", "miracle blade", 1), Item("grenade", "art is an explosion", 2, 0),
                          Item("burglary gear", "", 1)], self.character.items)
        self.assertEqual([Item("Luck Charm", "")], self.deadManWalking.items)

    def test_add_notes(self):
        self.character.add_notes("second")

        self.assertEqual("first\nsecond", self.character.description)

    def test_tick_healing_clock(self):
        self.assertEqual(0, self.deadManWalking.tick_healing_clock(3))

        self.assertEqual(1, self.deadManWalking.tick_healing_clock(2))
        self.assertEqual(1, self.deadManWalking.healing.progress)
        self.assertEqual([["Seduced", "Exhausted"], ["Terrified"], []], self.deadManWalking.harms)

        self.assertEqual(2, self.deadManWalking.tick_healing_clock(7))
        self.assertEqual(0, self.deadManWalking.healing.progress)
        self.assertEqual([[], [], []], self.deadManWalking.harms)
