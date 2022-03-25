from unittest import TestCase

from Playbook import Playbook


class TestPlaybook(TestCase):

    def setUp(self) -> None:
        self.emptyPlaybook = Playbook(8)
        self.standardPlaybook = Playbook(8, 3, 1)
        print("EXP: " + str(self.standardPlaybook.exp))

    def test_add_points(self):
        self.emptyPlaybook.add_points(5)
        self.assertEqual(5, self.emptyPlaybook.points)
        self.standardPlaybook.add_points(3)
        self.assertEqual(4, self.standardPlaybook.points)

    def test_add_exp(self):
        self.emptyPlaybook.add_exp(5)
        self.assertEqual(5, self.emptyPlaybook.exp)

    def test_add_exp_and_earn_point(self):
        self.emptyPlaybook.add_exp(10)
        self.assertEqual(2, self.emptyPlaybook.exp)
        self.assertEqual(1, self.emptyPlaybook.points)

    def test_multiple_points_earned(self):
        self.standardPlaybook.add_exp(22)
        self.assertEqual(1, self.standardPlaybook.exp)
        self.assertEqual(4, self.standardPlaybook.points)
