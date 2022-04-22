import json
from unittest import TestCase

from character.Item import Item


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

    def test_save_and_load_json(self):
        temp_str = json.dumps(self.consum_item.save_to_dict(), indent=5)
        temp_dict = json.loads(temp_str)
        temp_obj = Item.from_json(temp_dict)
        self.assertEqual(self.consum_item, temp_obj)
