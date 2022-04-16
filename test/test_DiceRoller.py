import unittest
from unittest import TestCase

from utility.DiceRoller import roll_dice


class Test(TestCase):
    def test_roll_dice(self):
        temp = roll_dice(0)
        print("Result 0 dice: " + str(temp))
        self.assertEqual(2, len(temp[1]))
        if temp[1].count(6) < 2:
            self.assertEqual(min(temp[1]), temp[0])
        else:
            self.assertEqual("CRIT", temp[0])

        temp = roll_dice()
        print("Result default dice: " + str(temp))
        self.assertEqual(1, len(temp[1]))
        self.assertEqual(max(temp[1]), temp[0])

        temp = roll_dice(2)
        print("Result 2 dice: " + str(temp))
        self.assertEqual(2, len(temp[1]))
        if temp[1].count(6) < 2:
            self.assertEqual(max(temp[1]), temp[0])
        else:
            self.assertEqual("CRIT", temp[0])

        temp = roll_dice(3)
        print("Result 3 dice: " + str(temp))
        self.assertEqual(3, len(temp[1]))
        if temp[1].count(6) < 2:
            self.assertEqual(max(temp[1]), temp[0])
        else:
            self.assertEqual("CRIT", temp[0])

        temp = roll_dice(50)
        print("Result 50 dice: " + str(temp))
        self.assertEqual(50, len(temp[1]))
        if temp[1].count(6) < 2:
            self.assertEqual(max(temp[1]), temp[0])
        else:
            self.assertEqual("CRIT", temp[0])

    @unittest.skip("random_dice_distribution")
    def test_random_dice_distribution(self):
        for i in range(100):
            n_rolls = 1000 * 1000
            lowest = 0.165
            highest = 0.168
            results = list(roll_dice(n_rolls)[1])

            for j in range(6):
                avg = results.count(i + 1) / n_rolls
                print("Testing value {}: ".format(i + 1))
                print(avg)
                self.assertTrue(lowest <= avg <= highest)

    @unittest.skip("important_decision_making")
    def test_important_decision(self):
        #se passa pari, se non passa dispari
        self.assertEqual(roll_dice(1)[0] % 2, 0)
