from unittest import TestCase

from character.Owner import Owner
from character.Vice import Vice


class TestOwner(TestCase):

    def setUp(self) -> None:
        self.owner = Owner(coin=2, stash=22, vice=Vice("Gambling", "not cheap", "Arnold, a hound breeder"))

    def test_can_have_coins(self):
        self.assertTrue(self.owner.can_have_coins(1))
        self.assertFalse(self.owner.can_have_coins(4))

    def test_can_stash_coins(self):
        self.assertTrue(self.owner.can_stash_coins(10))
        self.assertFalse(self.owner.can_stash_coins(35))

    def test_add_coins(self):
        self.assertTrue(self.owner.add_coins(2))
        self.assertEqual(4, self.owner.coin)
        self.assertFalse(self.owner.add_coins(1))
        self.assertEqual(4, self.owner.coin)

    def test_stash_coins(self):
        self.assertTrue(self.owner.stash_coins(8))
        self.assertEqual(30, self.owner.stash)
        self.assertFalse(self.owner.stash_coins(32))
        self.assertEqual(30, self.owner.stash)

    def test_can_store_coins(self):
        self.assertTrue(self.owner.can_store_coins(5))
        self.assertFalse(self.owner.can_store_coins(200))
