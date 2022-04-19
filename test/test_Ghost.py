import json
from unittest import TestCase

from character.Action import Action
from character.Attribute import Attribute
from character.Ghost import Ghost
from character.Playbook import Playbook
from component.Clock import Clock
from component.SpecialAbility import SpecialAbility


class TestGhost(TestCase):
    def setUp(self) -> None:
        self.longlocks = Ghost("Longlocks", "A princess", healing=Clock("Healing"),
                               abilities=[SpecialAbility("Ghost Form", "Electroplasmic vapor")],
                               playbook=Playbook(5), attributes=[Attribute("Insight", [Action("Hunt", 3)]),
                                                                 Attribute("Prowess", [Action("Skirmish", 3)]),
                                                                 Attribute("Resolve", [Action("Attune", 3)])]
                               )

    def test_save_and_load_json(self):
        temp_s = json.dumps(self.longlocks.save_to_dict(), indent=5)
        temp_dict = json.loads(temp_s)
        temp_dict.pop("Class")
        temp_dict.pop("need")
        temp_o = Ghost.from_json(temp_dict)
        self.assertEqual(temp_o, self.longlocks)
