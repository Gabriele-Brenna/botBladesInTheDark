import json
from unittest import TestCase

from character.Action import Action
from character.Attribute import Attribute
from character.Human import Human
from character.Item import Item
from character.NPC import NPC
from character.Playbook import Playbook
from character.Vice import Vice
from component.Clock import Clock
from component.SpecialAbility import SpecialAbility


class TestHuman(TestCase):
    def setUp(self) -> None:
        self.geralt = Human("Geralt", "White Wolf", items=[Item("Aerondight", "Silver Sword"),
                                                           Item("Ekhidna Decoction", "More stamina, more life")],
                            healing=Clock("Healing"), abilities=[SpecialAbility("Alchemist", "Great at making potions"),
                                                                 SpecialAbility("Venomous", "Immune to poison")],
                            playbook=Playbook(5), attributes=[Attribute("Insight", [Action("Hunt", 3)]),
                                                              Attribute("Prowess", [Action("Skirmish", 3)]),
                                                              Attribute("Resolve", [Action("Attune", 3)])],
                            vice=Vice("Pleasure", "Sometimes it gets lonely", "Passiflora"), pc_class="Whisper",
                            friend=NPC("Dandelion", "The bard"), enemy=NPC("Dijkstra", "Redanian Intelligence"))

    def test_save_and_load_json(self):
        temp_str = json.dumps(self.geralt.save_to_dict(), indent=5)
        temp_dict = json.loads(temp_str)
        temp_dict.pop("Class")
        temp_obj = Human.from_json(temp_dict)
        self.assertEqual(self.geralt, temp_obj)
