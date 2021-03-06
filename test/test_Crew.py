import json
from unittest import TestCase

from organization.Claim import Claim
from organization.Cohort import Cohort
from organization.Crew import Crew
from organization.Lair import Lair
from character.NPC import NPC
from game.Score import Score
from organization.Upgrade import Upgrade


class TestCrew(TestCase):

    def setUp(self) -> None:

        self.shadows = Crew(
            "Ombre",
            "shadows",
            "honorables",
            Lair("crow's foot", "a little barrack behind a pub"),
            tier=1,
            contact=NPC("Larose", "a bluecoat"),
            description="a guild of master spies and saboteurs",
            upgrades=[Upgrade("Boat", 2, 2), Upgrade("Tools", 1, 1)]
        )

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
            upgrades=[Upgrade("Vehicle", 1, 2), Upgrade("Barge", 1, 1), Upgrade("Vault", 1, 2)],
            vault_capacity=8,
            coins=3
        )

    def test_check_mastery(self):
        self.assertFalse(self.shadows.check_mastery())

        self.shadows.upgrades.append(Upgrade("Mastery", 4, 4))
        self.assertTrue(self.shadows.check_mastery())

    def test_add_rep(self):
        self.assertIsNone(self.smugglers.add_rep(22))
        self.assertTrue(self.smugglers.hold)
        self.assertEqual(5, self.smugglers.rep)

        self.assertIsNone(self.shadows.add_rep(11))
        self.assertEqual(11, self.shadows.rep)
        self.assertEqual(16, self.shadows.add_rep(12))
        self.assertEqual(11, self.shadows.rep)

    def test_add_wanted_level(self):
        self.shadows.add_wanted_level(2)
        self.assertEqual(2, self.shadows.wanted_level)
        self.shadows.add_wanted_level(3)
        self.assertEqual(4, self.shadows.wanted_level)
        self.shadows.add_wanted_level(-7)
        self.assertEqual(0, self.shadows.wanted_level)

    def test_add_heat(self):
        self.smugglers.add_heat(17)
        self.assertEqual(2, self.smugglers.heat)
        self.assertEqual(3, self.smugglers.wanted_level)

        self.shadows.add_heat(4)
        self.assertEqual(0, self.shadows.wanted_level)
        self.shadows.add_heat(5)
        self.assertEqual(0, self.shadows.heat)
        self.assertEqual(1, self.shadows.wanted_level)

    def test_clear_heat(self):
        self.shadows.clear_heat()
        self.smugglers.clear_heat()
        self.assertEqual(0, self.shadows.heat)
        self.assertEqual(0, self.smugglers.heat)

    def test_can_store(self):
        self.assertTrue(self.smugglers.can_store(4))
        self.assertTrue(self.shadows.can_store(4))

        self.assertFalse(self.shadows.can_store(8))
        self.assertFalse(self.smugglers.can_store(20))

        self.assertTrue(self.smugglers.can_store(-3))
        self.assertFalse(self.smugglers.can_store(-4))

    def test_check_training(self):
        self.assertFalse(self.shadows.check_training("Insight"))
        self.shadows.upgrades.append(Upgrade("Prowess", 1, 1))
        self.assertTrue(self.shadows.check_training("PROWESS"))

    def test_add_coin(self):
        self.assertTrue(self.smugglers.add_coin(4))
        self.assertEqual(7, self.smugglers.coins)
        self.assertFalse(self.shadows.add_coin(7))
        self.assertEqual(0, self.shadows.coins)

    def test_remove_coin(self):
        self.assertFalse(self.shadows.add_coin(-2))
        self.assertTrue(self.smugglers.add_coin(-3))
        self.assertEqual(0, self.smugglers.coins)

    def test_add_prison_claim(self):
        self.smugglers.add_prison_claim(Claim("Prison Claim"))
        self.assertEqual([Claim("Prison Claim")], self.smugglers.prison_claims)

    def test_add_lair_claim(self):
        self.assertTrue(self.shadows.add_lair_claim(Claim()))

        for i in range(4):
            self.assertTrue(self.smugglers.add_lair_claim(Claim()))
        self.assertFalse(self.smugglers.add_lair_claim(Claim()))

    def test_add_tier(self):
        self.assertTrue(self.shadows.add_tier(2))
        self.assertEqual(3, self.shadows.tier)
        self.assertFalse(self.shadows.hold)

        self.assertFalse(self.smugglers.add_tier())

    def test_upgrade_vault(self):
        self.assertEqual(16, self.smugglers.upgrade_vault())
        self.assertEqual(8, self.smugglers.upgrade_vault(False))

    def test_add_upgrade(self):
        self.assertEqual(Upgrade("Vehicle", 2, 2), self.smugglers.add_upgrade("veHicle"))
        self.assertTrue(self.smugglers.upgrades.__contains__(Upgrade("Vehicle", 2, 2)))

        self.assertEqual(Upgrade("Gear", 1, 1), self.shadows.add_upgrade("Gear"))
        self.assertTrue((self.shadows.upgrades.__contains__(Upgrade("Gear", 1, 1))))

        self.assertEqual(Upgrade("Vault", 1, 2), self.shadows.add_upgrade("Vault"))
        self.assertEqual(self.shadows.vault_capacity, 8)

    def test_remove_upgrade(self):
        self.assertIsNone(self.shadows.remove_upgrade("Workshop"))
        self.assertEqual(Upgrade("Tools", 0, 1), self.shadows.remove_upgrade("Tools"))
        self.assertEqual(Upgrade("Boat", 1, 2), self.shadows.remove_upgrade("boat"))

        self.assertEqual(Upgrade("Vault", 0, 2), self.smugglers.remove_upgrade("Vault"))
        self.assertEqual(self.smugglers.vault_capacity, 4)

    def test_calc_rep(self):
        score1 = Score(target_tier=3)
        score2 = Score(target_tier=0)

        self.assertEqual(3, self.smugglers.calc_rep(score1.target_tier))
        self.assertEqual(4, self.shadows.calc_rep(score1.target_tier))

        self.assertEqual(0, self.smugglers.calc_rep(score2.target_tier))
        self.assertEqual(1, self.shadows.calc_rep(score2.target_tier))

    def test_change_crew_type(self):
        self.assertTrue(self.shadows.change_crew_type("Bravos"))
        self.assertEqual("Bravos", self.shadows.type)
        self.assertFalse(self.shadows.change_crew_type("Witchers"))

    def test_save_and_load_json(self):
        temp_str = json.dumps(self.smugglers.save_to_dict(), indent=5)
        temp_obj = Crew.from_json(json.loads(temp_str))
        self.assertEqual(temp_obj, self.smugglers)

    def test_add_cohort(self):
        self.shadows.add_cohort(Cohort(["Thugs"], expert=False))
        self.shadows.add_cohort(Cohort(["Doctor"], expert=True))

        self.assertEqual(
            Cohort(["Thugs"], expert=False, scale=self.shadows.tier, quality=self.shadows.tier),
            self.shadows.cohorts[0])
        self.assertEqual(
            Cohort(["Doctor"], expert=True, scale=0, quality=self.shadows.tier+1), self.shadows.cohorts[1]
        )
