from unittest import TestCase

from character.Action import Action
from character.Attribute import Attribute
from character.Ghost import Ghost
from character.Hull import Hull
from character.Human import Human
from character.Item import Item
from character.NPC import NPC
from character.Playbook import Playbook
from character.Vampire import Vampire
from character.Vice import Vice
from component.Clock import Clock
from component.SpecialAbility import SpecialAbility
from game.Score import Score
from organization.Claim import Claim
from organization.Crew import Crew
from organization.Faction import Faction
from organization.Lair import Lair
from organization.Upgrade import Upgrade
from utility.ISavable import save_to_json
from utility.Json_Save import crew_from_json, factions_from_json, clocks_from_json, characters_from_json, \
    score_from_json, npcs_from_json


class Test(TestCase):
    def setUp(self) -> None:
        self.smugglers = Crew(
            "Contrabbandieri",
            "smugglers",
            "honorables",
            Lair("crow's foot", "a little barrack behind a pub", [Claim("Turf", "a turf"), Claim("Tavern", "Hound "
                                                                                                           "Pits "
                                                                                                           "Pub")]),
            tier=2,
            hold=False,
            rep=3,
            heat=3,
            wanted_level=1,
            contact=NPC("Rolan", "a drug-dealer"),
            description="a guild of smugglers",
            upgrades=[Upgrade("Vehicle", 1), Upgrade("Barge", 1)],
            vault_capacity=8,
            coins=3
        )

        self.unseen = Faction("The Unseen", 4, True, "Underworld", 2)
        self.imperial = Faction("Imperial Army", 6, True, "Institutions")
        self.rail_jacks = Faction("Rail Jacks", 2, False, "Labor & Trade")

        self.factions = [self.unseen, self.imperial, self.rail_jacks]

        self.caesar = NPC("Caesar", "The Emperor", self.imperial, "Hates knives")
        self.harry = NPC("Harry", "Court's wizard", self.unseen, "Cool scar")
        self.bob = NPC("Bob", "The Builder", self.rail_jacks, "Can we fix it? Yes we can")

        self.npcs = [self.caesar, self.harry, self.bob]

        self.geralt = Human("Geralt", "White Wolf", items=[Item("Aerondight", "Silver Sword"),
                                                           Item("Ekhidna Decoction", "More stamina, more life")],
                            healing=Clock("Healing"), abilities=[SpecialAbility("Alchemist", "Great at making potions"),
                                                                 SpecialAbility("Venomous", "Immune to poison")],
                            playbook=Playbook(5), attributes=[Attribute("Insight", [Action("Hunt", 3)]),
                                                              Attribute("Prowess", [Action("Skirmish", 3)]),
                                                              Attribute("Resolve", [Action("Attune", 3)])],
                            vice=Vice("Pleasure", "Sometimes it gets lonely", "Passiflora"), pc_class="Whisper",
                            friend=NPC("Dandelion", "The bard"), enemy=NPC("Dijkstra", "Redanian Intelligence"))
        self.regis = Vampire("Regis", "Barber-Surgeon", healing=Clock("Healing"),
                             abilities=[SpecialAbility("Undead", "You are not dead"),
                                        SpecialAbility("Bestial", "You transform in your vampire form")],
                             playbook=Playbook(5), attributes=[Attribute("Insight", [Action("Hunt", 3)]),
                                                               Attribute("Prowess", [Action("Skirmish", 3)]),
                                                               Attribute("Resolve", [Action("Attune", 3)])],
                             dark_servants=[NPC("Orianna"), self.harry])
        self.jeeg = Hull("Jeeg", "Robot d'acciaio", healing=Clock("Healing"),
                         abilities=[SpecialAbility("Automaton", "Spirit animating clock")],
                         playbook=Playbook(5), attributes=[Attribute("Insight", [Action("Hunt", 3)]),
                                                           Attribute("Prowess", [Action("Skirmish", 3)]),
                                                           Attribute("Resolve", [Action("Attune", 3)])])
        self.longlocks = Ghost("Longlocks", "A princess", healing=Clock("Healing"),
                               abilities=[SpecialAbility("Ghost Form", "Electroplasmic vapor")],
                               playbook=Playbook(5), attributes=[Attribute("Insight", [Action("Hunt", 3)]),
                                                                 Attribute("Prowess", [Action("Skirmish", 3)]),
                                                                 Attribute("Resolve", [Action("Attune", 3)])]
                               )

        self.characters = [self.geralt, self.regis, self.jeeg, self.longlocks]

        self.clocks = [Clock("Project elephant"), Clock("Killing Dettlaff")]

        self.score_npc = Score("Steal Benny", ["Geralt", "Regis"], 2, self.bob)
        self.score_faction = Score("Brake the air conditioning", ["Jeeg", "Longlocks"], 6, self.imperial)

    def test_crew_from_json(self):
        crew_str = save_to_json([self.smugglers])
        crew = crew_from_json(crew_str)
        self.assertEqual(self.smugglers, crew)

    def test_factions_from_json(self):
        factions_str = save_to_json(self.factions)
        factions = factions_from_json(factions_str)
        self.assertEqual(self.factions, factions)

    def test_clocks_from_json(self):
        clocks_str = save_to_json(self.clocks)
        clocks = clocks_from_json(clocks_str)
        self.assertEqual(self.clocks, clocks)

    def test_characters_from_json(self):
        characters_str = save_to_json(self.characters)
        characters = characters_from_json(characters_str)
        characters[1].dark_servants[1].faction = self.unseen
        self.assertEqual(self.characters, characters)

    def test_score_from_json(self):
        score_npc_str = save_to_json([self.score_npc])
        score_npc = score_from_json(score_npc_str)
        score_npc.target = self.bob
        self.assertEqual(self.score_npc, score_npc)

        score_faction_str = save_to_json([self.score_faction])
        score_faction = score_from_json(score_faction_str)
        score_faction.target = self.imperial
        self.assertEqual(self.score_faction, score_faction)

    def test_npcs_from_json(self):
        npcs_str = save_to_json(self.npcs)
        npcs = npcs_from_json(npcs_str)
        npcs[0].faction = self.imperial
        npcs[1].faction = self.unseen
        npcs[2].faction = self.rail_jacks
        self.assertEqual(self.npcs, npcs)
