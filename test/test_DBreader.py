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
                         query_special_abilities("Mule"))
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
        VALUES (1, "Game1", 1, "ENG")""")
        self.connection.commit()

        self.assertEqual("ENG", query_lang(1))

        self.cursor.execute("DELETE FROM Game")
        self.connection.commit()
