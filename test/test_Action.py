from unittest import TestCase

from Action import Action


class TestAction(TestCase):
    def setUp(self) -> None:
        self.action = Action("Hunt", 0)

    def test_add_dots(self):
        self.action.add_dots(2)

        self.assertEqual(2, self.action.rating)

    def test_add_dots_moreThan4(self):
        self.action.add_dots(7)

        self.assertEqual(4, self.action.rating)

    def test_add_dots_lessThan0(self):
        self.action.add_dots(-2)

        self.assertEqual(0, self.action.rating)
