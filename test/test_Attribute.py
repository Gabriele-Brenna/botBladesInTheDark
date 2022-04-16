from unittest import TestCase

from character.Action import Action
from character.Attribute import Attribute


class TestAttribute(TestCase):

    def setUp(self) -> None:
        self.insight = Attribute("Insight", [Action( "Hunt", 1), Action("Study", 2),
                                             Action("Survey", 1), Action("Tinker", 0)], 6)
        self.prowess = Attribute("Prowess", [Action("Finesse", 0), Action("Prowl", 4),
                                             Action("Skirmish", 4), Action("Wreck", 2)], 6)
        self.resolve = Attribute("Resolve", [Action("Attune", 0), Action("Command", 0),
                                             Action("Consort", 0), Action("Sway", 0)], 6)

    def test_attribute_level(self):
        self.assertEqual(3, self.insight.attribute_level())
        self.assertEqual(0, self.resolve.attribute_level())

    def test_action_dots(self):
        self.insight.action_dots("study", 1)
        self.assertEqual(3, self.insight.actions[1].rating)

        self.assertIsNone(self.prowess.action_dots("Sneak", 1))

    def test_action_rating(self):
        self.assertEqual(4, self.prowess.action_rating("PROWL"))

        self.assertRaises(Exception, lambda: self.resolve.action_rating("ProWl"))

