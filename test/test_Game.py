from unittest import TestCase

from character.Ghost import Ghost
from character.Human import Human
from character.NPC import NPC
from character.PC import PC
from component.Clock import Clock
from game.Game import Game
from game.Player import Player
from game.Score import Score
from organization.Faction import Faction


class TestGame(TestCase):
    def setUp(self) -> None:
        self.game = Game()
        self.game.users.append(Player("A", 1, False))
        self.game.users.append(Player("B", 2, True))
        self.game.users.append(Player("C", 3, False))

    def test_create_clock(self):
        self.assertEqual(Clock("Clock101", 4, 0), self.game.create_clock())
        self.assertEqual(Clock("Clock102", 7, 0), self.game.create_clock(segments=7))
        self.assertEqual([Clock("Clock101", 4, 0), Clock("Clock102", 7, 0)], self.game.clocks)

    def test_get_project_clocks(self):
        c1 = Clock("[Project]: discover", 7, 3)
        c2 = Clock("Kill", 10, 8)
        c3 = Clock("[proJect]: seek", 4, 3)

        self.game.clocks.append(c1)
        self.game.clocks.append(c2)
        self.game.clocks.append(c3)

        self.assertEqual([c1, c3], self.game.get_project_clocks())

    def test_tick_clock(self):
        burn_clock = Clock("Burn", 7, 3)
        kill_clock = Clock("Kill", 10, 3)
        steal_clock = Clock("Steal", 4, 3)
        self.game.clocks.append(burn_clock)
        self.game.clocks.append(kill_clock)
        self.game.clocks.append(steal_clock)

        self.assertEqual(Clock("Burn", 7, 6), self.game.tick_clock(burn_clock, 3))

        self.assertEqual(Clock("Kill", 10, 11), self.game.tick_clock(kill_clock, 8))
        self.assertEqual([Clock("Burn", 7, 6), Clock("Steal", 4, 3)], self.game.clocks)

        self.assertIsNone(self.game.tick_clock(Clock("Demolish"), 69))
        self.assertEqual([Clock("Burn", 7, 6), Clock("Steal", 4, 3)], self.game.clocks)

    def test_see_clocks(self):
        self.game.clocks.append(Clock("Burn the city", 7, 3))
        self.game.clocks.append(Clock("Infiltrate the manor", 10, 3))

        self.assertEqual([Clock("Burn the city", 7, 3), Clock("Infiltrate the manor", 10, 3)], self.game.see_clocks())

        self.game.clocks.append(Clock("Burn the boss", 4, 3))
        self.game.clocks.append(Clock("Steal the goats", 5, 8))

        self.assertEqual([Clock("Infiltrate the manor", 10, 3), Clock("Steal the goats", 5, 8)],
                         self.game.see_clocks(["Infiltrate the manor", "Steal the goats"]))
        self.assertEqual([Clock("Burn the city", 7, 3), Clock("Burn the boss", 4, 3)], self.game.see_clocks(["Burn"]))

    def test_get_main_score(self):
        self.game.scores.append(Score("Score1"))
        self.game.scores.append(Score("Score2", [None]))
        self.game.scores.append(Score("Score3"))
        self.assertEqual(Score("Score2", [None]), self.game.get_main_score())
        self.game.scores[0].participants.append(PC())
        self.assertEqual(Score("Score1", [PC()]), self.game.get_main_score())

    def test_get_master(self):
        self.assertEqual(Player("B", 2, True), self.game.get_master())

        self.game.users.clear()
        self.assertEqual(None, self.game.get_master())

    def test_get_pcs(self):
        self.assertEqual([], self.game.get_pcs_list())
        self.assertEqual([], self.game.get_owners_list())

        self.game.users[0].characters.append(Human("Pippo"))
        self.game.users[1].characters.append(Human("Paperino"))

        self.assertEqual([Human("Pippo"), Human("Paperino")], self.game.get_pcs_list())

        self.game.users[0].characters.append(Ghost("Casper"))
        self.assertEqual([Human("Pippo"), Human("Paperino")], self.game.get_owners_list())

    def test_get_player_by_id(self):
        self.assertEqual(Player("C", 3, False), self.game.get_player_by_id(3))

        self.assertEqual(None, self.game.get_player_by_id(5))

    def test_get_faction_by_name(self):
        self.assertEqual(None, self.game.get_faction_by_name("Red Sashes"))

        self.game.factions.append(Faction("Red Sashes"))
        self.assertEqual(Faction("Red Sashes"), self.game.get_faction_by_name("Red Sashes"))

    def test_get_npc_by_name_and_role(self):
        self.assertEqual(None, self.game.get_npc_by_name_and_role("Irimina", "A vicious noble"))

        self.game.NPCs.append(NPC("Irimina", "A vicious noble"))
        self.assertEqual(NPC("Irimina", "A vicious noble"),
                         self.game.get_npc_by_name_and_role("Irimina", "A vicious noble"))
