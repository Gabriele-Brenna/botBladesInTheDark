from unittest import TestCase

import game.Journal
from component.Clock import Clock
from game.Journal import Journal


class TestJournal(TestCase):
    def test_read_journal(self):
        game.Journal.index = 1
        temp = Journal()
        temp.write_title("The Knives of Doskvol")
        temp.write_phase(1)
        temp.write_phase(2)
        temp.write_phase(3)
        temp.write_general_notes("General note title", "This is a general note")
        temp.write_fortune_roll("User", "quality of the Item: Sword", "Will it kill the monster", 6, "Extra notes")
        temp.write_action("user", "goal", "action", "position", "effect", 5, "notes", assistants=["user2", "user3"], push=True, devil_bargain="devil bargain")
        temp.write_score("scoring", "plan type", "detail", [("user1", 5), ("user2", 2)], "controlled", "extra notes")
        temp.write_action("user", "goal", "action", "position", "effect", 5, "notes", assistants=["user2", "user3"], push=True, devil_bargain="devil bargain")
        temp.write_score("scoring", "plan type", "detail", [("user1", 5), ("user2", 2)], "controlled", "extra notes")
        temp.write_action("user", "goal", "action", "position", "effect", 5, "notes", assistants=["user2", "user3"], push=True, devil_bargain="devil bargain")
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
        temp.write_resistance_roll("User1", "description of the resistance roll", "avoided", "Skirmish", 10, "notes", 0)
        temp.write_resistance_roll("User1", "description of the resistance roll", "reduced", "Skirmish", 1, "notes", 10)
        temp.write_resistance_roll("User1", "description of the resistance roll", "avoided", "Skirmish", 1, "notes", -3)
        temp.write_clock("User1", Clock("project clock", 2, 0))
        temp.write_clock("User1", Clock("project clock", 6, 6), Clock("project clock", 4, 0))
        temp.write_action("User1", "goal of the action", "Skirmish", "controlled", "effect of the action", 5,
                          "extra notes", [{"name": "user2", "push": True, "outcome": 5},
                                          {"name": "user3", "push": True, "devil_bargain": "a general bargain", "outcome": 4},
                                          {"name": "user4", "push": False, "devil_bargain": "another bargain", "outcome": 3}],
                          assistants=["user5", "user6"], push=True)
        temp.write_action("User1", "goal of the action", "Skirmish", "controlled", "effect of the action", 5,
                          "extra notes", cohort="Thugs", assistants=["user5", "user6"], push=True)

        with open("resources_test/journalTest.html", 'w+') as f:
            f.write(temp.get_log_string())
