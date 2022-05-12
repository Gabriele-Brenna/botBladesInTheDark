import unittest
from unittest import TestCase

import game.Journal
from game.Journal import Journal


class TestJournal(TestCase):
    def test_read_journal(self):
        game.Journal.index = 1
        temp = Journal()
        temp.write_heading()
        temp.write_title("The Knives of Doskvol")
        temp.write_free_play()
        temp.write_score_phase()
        temp.write_downtime_phase()
        temp.write_general_notes("General note title", "This is a general note")
        temp.write_fortune_roll("User", "quality of the Item: Sword", "Will it kill the monster", 6, "Extra notes")
        temp.write_action_roll("user", "goal", "action", "position", "effect", 5, "notes", "User2", True, "notes")
        temp.write_score("scoring", "plan type", "detail", [("user1", 5), ("user2", 2)], "controlled", "extra notes")
        temp.write_action_roll("user", "goal", "action", "position", "effect", 5, "notes", "Tizio2", True, "notes")
        temp.write_score("scoring", "plan type", "detail", [("user1", 5), ("user2", 2)], "controlled", "extra notes")
        temp.write_action_roll("user", "goal", "action", "position", "effect", 5, "notes", "User2", True, "notes")
        temp.write_end_score("best outcome", "extra notes")
        temp.write_payoff(10, True, "extra notes")
        temp.write_end_score("best outcome", "extra notes")
        temp.write_payoff(10, True, "extra notes")
        temp.write_heat("heat type", "dead meat", True, True, True, True, 4, 5)
        temp.write_entanglement("reprisal of the dead", "very very long description")
        temp.write_secret_entanglement("reprisal of the dead", "super long description")
        temp.write_activity("temp", "crafting", "Bow and arrow", 6, 6)
        temp.write_activity("temp", "acquire_assets", "Huge apartment", 6, 6)
        temp.write_activity("temp", "long_term_project", "Long project", 5, 5, notes="extra notes")
        temp.write_activity("temp", "recover", "Stomachache", 5, 5)
        temp.write_activity("temp", "reduce_heat", "Wanted", 5, 5)
        temp.write_activity("temp", "train", "Tinker", 5, 5)
        temp.write_activity("temp", "help_cohort", "Thugs", 5, 5)
        temp.write_activity("temp", "replace_cohort", "Thugs", 6, "New cohort")
        temp.write_activity("temp", "indulge_vice", "Vice", 6, 3, "Brag", "Joker")
        temp.write_activity("temp", "indulge_vice", "Vice", 6, 3, "Lost", "Joker")
        temp.write_activity("temp", "indulge_vice", "Vice", 6, 3, "Tapped", "Joker")
        temp.write_activity("temp", "indulge_vice", "Vice", 6, 3, "Attracted trouble", "Joker", "extra information")
        temp.write_add_claim(True, "LAIR CLAIM")
        temp.write_add_claim(False, "PRISON CLAIM")
        temp.write_incarceration("User1", 2, "Extra information", "Extra notes")
        temp.write_incarceration("User1", 10, "Extra information", "Extra notes")
        temp.write_flashback("User1", "what happened during the flashback", 6, "stretching", True)
        temp.write_resistance_roll("User1", "description of the resistance roll", "Skirmish", 10, 0)
        temp.write_resistance_roll("User1", "description of the resistance roll", "Skirmish", 1, 10)
        temp.write_resistance_roll("User1", "description of the resistance roll", "Skirmish", 1, -3)
        temp.write_group_action("User1", "Goal of the group action", "Tinker", 5,
                                position="Unstable", effect="What will be the effect", notes="Extra notes",
                                players=["User2", "User3"], helper="User4", push=True,
                                devils="Devil's bargain conditions")
        temp.write_group_action("User1", "Goal of group action", "Tinker", 5, notes="extra notes", position="Secure",
                                effect="particular effect", cohort="Type of the cohort that will help")
        temp.read_journal()

    @unittest.skip("default")
    def test_default(self):
        for i in range(5):
            self.default = Journal()
