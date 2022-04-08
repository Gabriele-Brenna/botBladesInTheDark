from unittest import TestCase

from component.Clock import Clock


class TestClock(TestCase):

    def setUp(self) -> None:
        self.default_clock = Clock()
        self.big_clock = Clock("big clock", 8, 4)

    def test_tick(self):
        self.assertFalse(self.default_clock.tick(-4))
        self.assertEqual(0, self.default_clock.progress)

        self.assertFalse(self.default_clock.tick(3))
        self.assertTrue(self.default_clock.tick(2))
        self.assertEqual(5, self.default_clock.progress)

    def test_edit(self):
        self.default_clock.edit("big clock", 8)
        self.assertNotEqual(self.big_clock, self.default_clock)
        self.default_clock.progress = 4
        self.assertEqual(self.big_clock, self.default_clock)
