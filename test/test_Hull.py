import json
from unittest import TestCase

from character.Action import Action
from character.Attribute import Attribute
from character.Hull import Hull
from character.Playbook import Playbook
from component.Clock import Clock
from component.SpecialAbility import SpecialAbility


class TestHull(TestCase):
    def setUp(self) -> None:
        self.jeeg = Hull("Jeeg", "Robot d'acciaio", healing=Clock("Healing"),
                         abilities=[SpecialAbility("Automaton", "Spirit animating clock")],
                         playbook=Playbook(5), attributes=[Attribute("Insight", [Action("Hunt", 3)]),
                                                           Attribute("Prowess", [Action("Skirmish", 3)]),
                                                           Attribute("Resolve", [Action("Attune", 3)])],
                         frame_features=[SpecialAbility("Spider-Climb", "You climb as a spider")])

    def test_save_and_load_json(self):
        temp_str = json.dumps(self.jeeg.save_to_dict(), indent=5)
        temp_dict = json.loads(temp_str)
        temp_dict.pop("Class")
        temp_obj = Hull.from_json(temp_dict)
        self.assertEqual(self.jeeg, temp_obj)
        print(temp_obj)
        print(temp_str)

    def test_select_frame(self):
        self.assertTrue(self.jeeg.select_frame("H"))
        self.assertFalse(self.jeeg.select_frame("l"))
