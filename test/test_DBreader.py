import unittest
from unittest import TestCase

from controller.DBreader import *


class TestDBReader(TestCase):

    def setUp(self) -> None:
        self.connection = establish_connection()
        self.cursor = self.connection.cursor()

    def test_query_special_abilities(self):
        self.cursor.execute("""SELECT COUNT(*) FROM SpecialAbility""")
        query = self.cursor.fetchone()[0]
        self.assertEqual(query, len(query_special_abilities()))

        self.assertEqual([SpecialAbility("Mule", "Your load limits are higher. Light: 5. Normal: 7. Heavy: 8.")],
                         query_special_abilities(special_ability="Mule"))
        self.assertEqual([SpecialAbility("Battleborn", "You may expend your special armor to reduce harm from an "
                                                       "attack in combat or to push yourself during a fight. ")],
                         query_special_abilities("Cutter", True))

        self.assertEqual([SpecialAbility("Deadly", "Each PC may add +1 action rating to Hunt, Prowl, "
                                                   "or Skirmish (up to a max rating of 3).")],
                         query_special_abilities("Assassins", True))

        self.assertFalse(query_special_abilities("AAAAA", True))

    def test_query_xp_triggers(self):
        self.cursor.execute("""SELECT COUNT(*) FROM XpTrigger""")
        query = self.cursor.fetchone()[0]
        self.assertEqual(query, len(query_xp_triggers()))

        self.assertEqual(["You addressed a challenge with knowledge or arcane power."],
                         query_xp_triggers("Whisper", True))

        self.assertEqual(["Bolster your crew's reputation or develop a new one.",
                          "Contend with challenges above your current station.",
                          "Every time you roll a desperate action, mark xp in that action's attribute.",
                          "Express the goals, drives, inner conflict, or essential nature of the crew.",
                          "You expressed your beliefs, drives, heritage, or background.",
                          "You struggled with issues from your vice or traumas (or strictures)/ need or "
                          "glooms / wear during the session."],
                         query_xp_triggers(peculiar=False))

        self.assertEqual(["Contend with challenges above your current station.",
                          "Bolster your crew's reputation or develop a new one.",
                          "Express the goals, drives, inner conflict, or essential nature of the crew."],
                         query_xp_triggers("Cult", peculiar=False))

        self.assertEqual(["Every time you roll a desperate action, mark xp in that action's attribute.",
                          'You struggled with issues from your vice or traumas (or strictures)/ need or '
                          'glooms / wear during the session.',
                          'You exacted vengeance upon those whom you deem deserving.',
                          'You expressed your outrage or anger, or settled scores from your heritage or '
                          'background.'], query_xp_triggers("Ghost"))

    def test_query_action_list(self):
        self.assertEqual([Action("hunt"), Action("study"), Action("survey"), Action("tinker")],
                         query_action_list("Insight"))
        self.assertFalse(query_action_list("Alteration"))

    def test_query_vice(self):
        self.assertEqual([Vice("Weird", "You experiment with strange essences, consort with rogue spirits, observe "
                                        "bizarre rituals or taboos, etc.")],
                         query_vice("Weird"))
        self.assertEqual([Vice("To Guard", None), Vice("To Destroy", None), Vice("To Discover", None),
                          Vice("To Acquire", None), Vice("To Labour at", None)],
                         query_vice(character_class="Hull"))

    def test_query_character_sheets(self):
        self.assertEqual(['Cutter',
                          'Hound',
                          'Leech',
                          'Lurk',
                          'Slide',
                          'Spider',
                          'Whisper',
                          'Ghost',
                          'Hull',
                          'Vampire'], query_character_sheets(canon=True))

        self.assertEqual(['Ghost',
                          'Hull',
                          'Vampire'], query_character_sheets(spirit=True))

        self.assertEqual(['Ghost',
                          'Hull',
                          'Vampire'], query_character_sheets(True, True))

        self.cursor.execute("""SELECT COUNT(*) FROM CharacterSheet""")
        query = self.cursor.fetchone()[0]

        self.assertEqual(query, len(query_character_sheets()))

    def test_query_attributes(self):
        self.assertEqual([Attribute("Insight", query_action_list("Insight")),
                          Attribute("Prowess", query_action_list("Prowess")),
                          Attribute("Resolve", query_action_list("Resolve"))], query_attributes())

    @unittest.skip("test_query_last_game_id")
    def test_query_last_game_id(self):
        self.assertEqual(0, query_last_game_id())

        self.cursor.execute("""
        INSERT INTO Game (Title,Tel_Chat_ID)
        VALUES ("title",1234) 
        """)

        self.assertEqual(1, query_last_game_id())

        self.cursor.execute("""
        DELETE FROM Game
        """)

    def test_query_game_json(self):
        self.cursor.execute("""
        INSERT INTO Game (Game_ID, Title, Tel_Chat_ID, Crew_JSON, Crafted_Item_JSON, NPC_JSON, Faction_JSON, Score_JSON, 
        Clock_JSON, Journal, State)
        VALUES (1, "Game1", 1, '{"Assassins": "Hit man"}', '{"Aerondight": "Magical silver sword"}', 
        '{"Dandelion": "An humble bard"}', '{"The Unseen": "One you see them you can not unsee them"}', 
        '{"Jenny o the Woods": "Love can make you become a nightwraith"}', '{"Healing": "How long will it take?"}',
        'Welcome to Blades in the Dark', 1)""")
        self.connection.commit()

        dict1 = {'Crew_JSON': '{"Assassins": "Hit man"}', 'Crafted_Item_JSON': '{"Aerondight": "Magical silver sword"}',
                 'NPC_JSON': '{"Dandelion": "An humble bard"}',
                 'Faction_JSON': '{"The Unseen": "One you see them you can not unsee them"}',
                 'Score_JSON': '{"Jenny o the Woods": "Love can make you become a nightwraith"}',
                 'Clock_JSON': '{"Healing": "How long will it take?"}', 'Journal': 'Welcome to Blades in the Dark',
                 'State': 1}

        dict2 = {'NPC_JSON': '{"Dandelion": "An humble bard"}',
                 'Faction_JSON': '{"The Unseen": "One you see them you can not unsee them"}',
                 'Score_JSON': '{"Jenny o the Woods": "Love can make you become a nightwraith"}'}

        self.assertEqual(dict1, query_game_json(1))

        self.assertEqual(dict2, query_game_json(1, ['NPC_JSON', 'Faction_JSON', 'Score_JSON']))

        self.cursor.execute("DELETE FROM Game WHERE Game_ID = 1")
        self.connection.commit()

    def test_query_users_from_game(self):
        self.cursor.execute("""
        INSERT INTO User 
        VALUES (1, "Aldo")""")
        self.cursor.execute("""
        INSERT INTO User
        VALUES (2, "Giovanni")""")
        self.cursor.execute("""
        INSERT INTO User
        VALUES (3, "Giacomo")""")
        self.cursor.execute("""
        INSERT INTO Game (Game_ID, Title, Tel_Chat_ID)
        VALUES (1, "Game1", 1)""")
        self.cursor.execute("""
        INSERT INTO Game (Game_ID, Title, Tel_Chat_ID)
        VALUES (2, "Game2", 1)""")
        self.cursor.execute("""
        INSERT INTO User_Game (User_ID, Game_ID, Master)
        VALUES (1, 1, TRUE)""")
        self.cursor.execute("""
        INSERT INTO User_Game (User_ID, Game_ID)
        VALUES (2, 1)""")
        self.cursor.execute("""
        INSERT INTO User_Game (User_ID, Game_ID)
        VALUES (3, 2)""")
        self.connection.commit()

        first_game = [('Aldo', 1, 1), ('Giovanni', 2, None)]
        second_game = [('Giacomo', 3, None)]
        self.assertEqual(first_game, query_users_from_game(1))
        self.assertEqual(second_game, query_users_from_game(2))

        self.cursor.execute("DELETE FROM Game WHERE Game_ID = 1 OR Game_ID = 2")
        self.cursor.execute("DELETE FROM User WHERE Tel_ID = 1 OR Tel_ID = 2 OR Tel_ID = 3")
        self.connection.commit()

    def test_query_pc_json(self):
        self.cursor.execute("""
                INSERT INTO User 
                VALUES (1, "Aldo")""")
        self.cursor.execute("""
                INSERT INTO User
                VALUES (2, "Giovanni")""")
        self.cursor.execute("""
                INSERT INTO Game (Game_ID, Title, Tel_Chat_ID)
                VALUES (1, "Game1", 1)""")
        self.cursor.execute("""
                INSERT INTO User_Game 
                VALUES (1, 1, "{'Character': 'JSON'}", TRUE)""")
        self.cursor.execute("""
                INSERT INTO User_Game 
                VALUES (2, 1, "{'Character': 'JSON'}", TRUE)""")
        self.connection.commit()

        self.assertEqual({1: "{'Character': 'JSON'}", 2: "{'Character': 'JSON'}"}, query_pc_json(1))

        self.cursor.execute("DELETE FROM Game WHERE Game_ID = 1")
        self.cursor.execute("DELETE FROM User WHERE Tel_ID = 1 OR Tel_ID = 2")
        self.connection.commit()

    def test_query_games_info(self):
        self.cursor.execute("""
                INSERT INTO Game (Game_ID, Title, Tel_Chat_ID)
                VALUES (-1, "Game1", 1)""")
        self.cursor.execute("""
                INSERT INTO Game (Game_ID, Title, Tel_Chat_ID)
                VALUES (-2, "Game2", 2)""")
        self.connection.commit()

        self.assertEqual([{"identifier": -2, "title": "Game2", "chat_id": 2},
                          {"identifier": -1, "title": "Game1", "chat_id": 1}], query_games_info())

        self.assertEqual([{"identifier": -1, "title": "Game1", "chat_id": 1}], query_games_info(game_id=-1))

        self.cursor.execute("DELETE FROM Game WHERE Game_ID = -1 OR Game_ID = -2")
        self.connection.commit()

    def test_query_game_ids(self):
        self.cursor.execute("""
                       INSERT INTO Game (Game_ID, Title, Tel_Chat_ID)
                       VALUES (-1, "Game1", 1)""")
        self.cursor.execute("""
                       INSERT INTO Game (Game_ID, Title, Tel_Chat_ID)
                       VALUES (-2, "Game2", 2)""")
        self.connection.commit()

        self.assertEqual([-1], query_game_ids(title="Game1"))
        self.assertEqual([-1], query_game_ids(tel_chat_id=1))
        self.assertEqual([-2], query_game_ids(2, "Game2"))
        self.assertEqual([-2, -1], query_game_ids())

        self.cursor.execute("DELETE FROM Game WHERE Game_ID = -1 OR Game_ID = -2")
        self.connection.commit()

    def test_query_lang(self):
        self.cursor.execute("""
        INSERT INTO Game (Game_ID, Title, Tel_Chat_ID, Language)
        VALUES (-1, "Game1", -1, "ENG")""")
        self.connection.commit()

        self.assertEqual("ENG", query_lang(-1))

        self.cursor.execute("DELETE FROM Game WHERE Game_ID = -1")
        self.connection.commit()

    def test_query_char_strange_friends(self):
        cutter_friends = [{'name': 'Marlane', 'description': '', 'role': 'A pugilist', 'faction': None},
                          {'name': 'Chael', 'description': '', 'role': 'A vicious thug', 'faction': None},
                          {'name': 'Mercy', 'description': '', 'role': 'A cold killer', 'faction': None},
                          {'name': 'Grace', 'description': '', 'role': 'An extortionist', 'faction': None},
                          {'name': 'Sawtooth', 'description': '', 'role': 'A physicker', 'faction': None}]

        friends = []
        for i in range(len(cutter_friends)):
            friends.append(NPC(**cutter_friends[i]))

        self.assertEqual(friends, query_char_strange_friends("cutter"))

    def test_query_crew_contacts(self):
        smugglers_contacts = [{'name': 'Elynn', 'description': '', 'role': 'A dock worker', 'faction': None},
                              {'name': 'Rolan', 'description': '', 'role': 'A drug dealer', 'faction': None},
                              {'name': 'Sera', 'description': '', 'role': 'An arms dealer', 'faction': None},
                              {'name': 'Nyelle', 'description': '', 'role': 'A spirit trafficker', 'faction': None},
                              {'name': 'Decker', 'description': '', 'role': 'An anarchist', 'faction': None},
                              {'name': 'Esme', 'description': '', 'role': 'A tavern owner', 'faction': None}]

        contacts = []
        for i in range(len(smugglers_contacts)):
            contacts.append(NPC(**smugglers_contacts[i]))

        self.assertEqual(contacts, query_crew_contacts("smugglers"))

    def test_query_actions(self):
        self.assertEqual([('Tinker',
                           'When you Tinker, you fiddle with devices and mechanisms. You might create a '
                           + 'new gadget or alter an existing item. You might pick a lock or crack a '
                           + 'safe. You might disable an alarm or trap. You might turn the clockwork and '
                           + 'electroplasmic devices around the city to your advantage. You could try to '
                           + 'use your technical expertise to control a vehicle (but Finessing might be '
                           + 'better).',
                           'Insight')], query_actions("Tinker"))

        names = []
        for result in query_actions(attribute="Insight"):
            names.append(result[0])
        self.assertEqual(["Hunt", "Study", "Survey", "Tinker"], names)

    def test_query_game_of_user(self):
        self.assertIsNone(query_game_of_user(-1, -1))

        self.cursor.execute("""
                INSERT INTO Game (Game_ID, Title, Tel_Chat_ID, Language)
                VALUES (-25, "Game1", -1, "ENG")""")
        self.cursor.execute("""
                        INSERT INTO User (Tel_ID, Name)
                        VALUES (-1, "Pino")""")
        self.cursor.execute("""
                        INSERT INTO User_Game (User_ID, Game_ID)
                        VALUES (-1, -25)""")

        self.connection.commit()

        self.assertEqual(-25, query_game_of_user(-1, -1))

        self.cursor.execute("DELETE FROM Game WHERE Game_ID = -25")
        self.cursor.execute("DELETE FROM User WHERE Tel_ID = -1")
        self.connection.commit()

    def test_query_crew_sheets(self):
        self.assertEqual(['Assassins', 'Bravos', 'Cult', 'Hawkers', 'Shadows', 'Smugglers'], query_crew_sheets(True))

    def test_query_upgrade_groups(self):
        self.assertEqual(["Lair", "Quality", "Specific", "Training"], query_upgrade_groups())

    def test_query_upgrades(self):
        secure_up = {"name": "Secure",
                     "description": "Your lair has locks, alarms, and traps to thwart "
                                    "intruders. A second upgrade improves the defenses to "
                                    "include arcane measures that work against spirits. You "
                                    "might roll your crew’s Tier if these measures are ever "
                                    "put to the test, to see how well they thwart an "
                                    "intruder.",
                     "tot_quality": 2}

        self.assertEqual([secure_up], query_upgrades(upgrade="secure"))

        self.assertEqual(5, len(query_upgrades(crew_sheet="bravos")))

        self.assertEqual(18, len(query_upgrades(common=True)))

        self.assertEqual(38, len(query_upgrades(canon=True)))

        self.assertEqual(6, len(query_upgrades(group="quality")))

        self.assertEqual(20, len(query_upgrades(canon=True, group="specific")))

    def test_query_starting_upgrades_and_cohorts(self):
        self.assertEqual([{"name": "Carriage", "quality": 1}, {"name": "Prowess", "quality": 1}],
                         query_starting_upgrades_and_cohorts("smugglers")[0])

        self.assertEqual(([{"name": "Prowess", "quality": 1}], [{"type": "Thugs", "expert": False}]),
                         query_starting_upgrades_and_cohorts("bravos"))

    def test_query_sheet_description(self):
        self.assertFalse(query_sheet_descriptions("NotExistingSheet"))

        self.assertEqual("An arcane adept and channeler", query_sheet_descriptions("Whisper")[0])
        self.assertEqual("Vice dealers: All of Doskvol craves escape. They can’t go outside... but they can turn to "
                         "you.",
                         query_sheet_descriptions("Hawkers")[0])

        self.assertTrue(len(query_sheet_descriptions()) >= 16)

    def test_query_frame_features(self):
        self.assertFalse(query_frame_features("Calculating"))

        self.assertEqual(SpecialAbility("Reflexes", "You have lightning-fast reaction time. When there's a question "
                                                    "about who acts first, the answer is you (two characters with "
                                                    "Reflexes act simultaneously). "),
                         query_frame_features("Reflexes")[0])
        self.assertEqual(4, len(query_frame_features(group="E")))

    def test_query_items(self):
        self.assertFalse(query_items("NotExistingItem"))

        self.assertEqual([Item("Fine long rifle", "A finely crafted hunting rifle, deadly at long range, unwieldy in "
                                                  "close quarters. Long rifles are usually illegal for private "
                                                  "citizens in Doskvoll, but you have (real or forged) military "
                                                  "paperwork for this one.", 2, -1)],
                         query_items(item_name="Fine long rifle"))

        self.assertEqual(6, len(query_items(pc_class="whisper")))
        self.assertEqual(16, len(query_items(common_items=True)))

    def test_query_hunting_grounds(self):
        self.assertEqual("Sabotage: Hurt an opponent by destroying something.",
                         query_hunting_grounds("Sabotage", only_names=False)[0])
        self.assertEqual(['Accident', 'Disappearance', 'Murder', 'Ransom', 'Battle', 'Extortion', 'Sabotage',
                          'Smash & Grab', 'Acquisition', 'Augury', 'Consecration', 'Sacrifice', 'Sale', 'Supply',
                          'Show of Force', 'Socialize', 'Burglary', 'Espionage', 'Robbery', 'Arcane/Weird', 'Arms',
                          'Contraband', 'Passengers'], query_hunting_grounds())
        self.assertEqual(['Arcane/Weird', 'Arms', 'Contraband', 'Passengers'],
                         query_hunting_grounds(crew_type="Smugglers"))

    def test_query_claims(self):
        self.assertFalse(query_claims("NotExistingClaim"))

        self.assertEqual(Claim("Cloister", "+1 scale for your Adept cohorts"), query_claims("Cloister")[0])

        self.assertEqual(6, len(query_claims(prison=True, canon=True)))
        self.assertTrue(len(query_claims()) >= 52)
        print(query_claims())

    # TODO: test query_factions & query_npcs

    def test_query_traumas(self):
        self.assertEqual([("Chaotic", "")], query_traumas("chaotic"))

        self.assertTrue(len(query_traumas()) >= 28)

        self.assertTrue(len(query_traumas(pc_class="Human")) >= 8)
