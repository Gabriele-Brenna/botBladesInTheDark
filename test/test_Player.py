from unittest import TestCase

from character.Ghost import Ghost
from character.Hull import Hull
from character.Human import Human
from character.Vice import Vice
from game.Player import Player
from component.SpecialAbility import SpecialAbility
from character.Vampire import Vampire


class TestPlayer(TestCase):
    def setUp(self) -> None:
        self.human = Human("Marg", stress_level=420, harms=[[], ["black hole sun burn"], []])
        self.human.add_action_dots("attune", 2)
        self.human.add_action_dots("hunt", 1)
        self.ghost = Ghost("Casper", abilities=[SpecialAbility("Ghost Form", ""),
                                                SpecialAbility("ghost mind",
                                                               "You’re always aware of supernatural entities in your " +
                                                               "presence. Take +1d when you gather info about the " +
                                                               "supernatural."),
                                                SpecialAbility("Calculating", "")])
        self.player = Player("p1", 1, False, [self.human, self.ghost])

    def test_migrate_character_type(self):
        # TODO : check Xp_Triggers from DB
        self.player.migrate_character_type("marg", "Ghost")
        self.assertIsInstance(self.player.characters[0], Ghost)
        self.assertEqual(Vice("Need of Life Essence", "You have an intense need: life essence. To satisfy this need, "
                                                      "possess a living victim and consume their spirit energy (this "
                                                      "may be a downtime action). When you do so, clear half your "
                                                      "drain (round down)."), self.player.characters[0].need)

        self.player.migrate_character_type("marg", "HULL")
        self.assertIsInstance(self.player.characters[0], Hull)

        self.player.migrate_character_type("marg", "vampire")
        self.assertIsInstance(self.player.characters[0], Vampire)

        self.assertEqual(4, self.player.characters[0].get_action_rating("attune"))
        self.assertEqual(3, self.player.characters[0].get_action_rating("hunt"))
        self.assertEqual(0, self.player.characters[0].stress_level)
        self.assertEqual([[], [], []], self.player.characters[0].harms)

        self.player.migrate_character_type("casper", "vampire")
        self.assertIsInstance(self.player.characters[1], Vampire)

        self.assertEqual([SpecialAbility("undead",
                                         "You are a spirit which animates an undead body. Your trauma is maxed out. "
                                         "Choose four trauma conditions which reflect your vampiric nature. Arcane "
                                         "attacks are potent against you. If you suffer fatal harm or trauma, "
                                         "your undead spirit is overwhelmed. You take level 3 harm: \"Incapacitated\" "
                                         "until you feed enough to recover. If you suffer arcane harm while in this "
                                         "state, you are destroyed utterly. Your XP tracks are longer (you now "
                                         "advance more slowly). You have more stress boxes. "),
                          SpecialAbility("Ghost mind",
                                         "You’re always aware of supernatural entities in your presence. Take +1d "
                                         "when you gather info about the supernatural.")],
                         self.player.characters[1].abilities)
