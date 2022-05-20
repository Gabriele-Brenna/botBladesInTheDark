from unittest import TestCase

from character.PC import PC
from component.Clock import Clock
from game.Game import Game
from game.Score import Score


class TestGame(TestCase):
    def setUp(self) -> None:
        self.game = Game()

    def test_create_clock(self):
        self.assertEqual(Clock("Clock101", 4, 0), self.game.create_clock())
        self.assertEqual(Clock("Clock102", 7, 0), self.game.create_clock(segments=7))
        self.assertEqual([Clock("Clock101", 4, 0), Clock("Clock102", 7, 0)], self.game.clocks)

    def test_get_project_clocks(self):
        c1 = Clock("Project: discover", 7, 3)
        c2 = Clock("Kill", 10, 8)
        c3 = Clock("proJect: seek", 4, 3)

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
