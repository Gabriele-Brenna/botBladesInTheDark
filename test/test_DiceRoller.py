from unittest import TestCase

from main.DiceRoller import roll_dice


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
