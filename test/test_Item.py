from unittest import TestCase

from Item import Item


class TestItem(TestCase):

    def setUp(self) -> None:
        self.infty_item = Item("A blade or two", "1/2 small knives, just in case", 1, quality=2)
        self.consum_item = Item("Grenade", "a small but efficient explosive", 1, 1, 1)

    def test_use_inftyItem(self):
        self.assertTrue(self.infty_item.use())

        self.assertTrue(self.infty_item.use())

    def test_use_consumItem(self):
        self.assertTrue(self.consum_item.use())

        self.assertFalse(self.consum_item.use())
