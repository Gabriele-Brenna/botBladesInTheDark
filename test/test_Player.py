from unittest import TestCase

from Ghost import Ghost
from Hull import Hull
from Human import Human
from Player import Player
from SpecialAbility import SpecialAbility
from Vampire import Vampire


class TestPlayer(TestCase):
    def setUp(self) -> None:
        self.human = Human("Marg", stress_level=420, harms=[[], ["black hole sun burn"], []])
        self.human.resolve.action_dots("attune", 2)
        self.human.insight.action_dots("hunt", 1)
        self.ghost = Ghost("Casper", abilities=[SpecialAbility("Ghost Form", ""), SpecialAbility("ghost mind", ""),
                                                SpecialAbility("Calculating", "")])
        self.player = Player("p1", 1, False, [self.human, self.ghost])

    def test_migrate_character_type(self):
        self.player.migrate_character_type("marg", "Ghost")
        self.assertIsInstance(self.player.characters[0], Ghost)

        self.player.migrate_character_type("marg", "HULL")
        self.assertIsInstance(self.player.characters[0], Hull)

        self.player.migrate_character_type("marg", "vampire")
        self.assertIsInstance(self.player.characters[0], Vampire)

        self.assertEqual(4, self.player.characters[0].resolve.get_action_rating("attune"))
        self.assertEqual(3, self.player.characters[0].insight.get_action_rating("hunt"))
        self.assertEqual(0, self.player.characters[0].stress_level)
        self.assertEqual([[], [], []], self.player.characters[0].harms)

        self.player.migrate_character_type("casper", "vampire")
        self.assertIsInstance(self.player.characters[1], Vampire)

        self.assertEqual([SpecialAbility("undead", ""), SpecialAbility("Ghost mind", "")],
                         self.player.characters[1].abilities)
