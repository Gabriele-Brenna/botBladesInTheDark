import json
from unittest import TestCase

from character.Action import Action
from character.Attribute import Attribute
from character.NPC import NPC
from character.Playbook import Playbook
from character.Vampire import Vampire
from component.Clock import Clock
from component.SpecialAbility import SpecialAbility
from organization.Faction import Faction


class TestVampire(TestCase):
    def setUp(self) -> None:
        self.unseen = Faction("The Unseen", 4, True, "Underworld", 2)
        self.harry = NPC("Harry", "Court's wizard", self.unseen, "Cool scar")
        self.regis = Vampire("Regis", "Barber-Surgeon", healing=Clock("Healing"),
                             abilities=[SpecialAbility("Undead", "You are not dead"),
                                        SpecialAbility("Bestial", "You transform in your vampire form")],
                             playbook=Playbook(5), attributes=[Attribute("Insight", [Action("Hunt", 3)]),
                                                               Attribute("Prowess", [Action("Skirmish", 3)]),
                                                               Attribute("Resolve", [Action("Attune", 3)])],
                             dark_servants=[NPC("Orianna"), self.harry])

    def test_save_and_load_json(self):
        temp_str = json.dumps(self.regis.save_to_dict(), indent=5)
        temp_dict = json.loads(temp_str)
        temp_dict.pop("Class")
        temp_obj = Vampire.from_json(temp_dict)
        self.assertEqual(self.regis.dark_servants[1].faction.name, temp_obj.dark_servants[1].faction)
        temp_obj.dark_servants[1].faction = self.unseen
        self.assertEqual(self.regis, temp_obj)
