from unittest import TestCase
from main.controller.DBwriter import *


class TestDBwriter(TestCase):
    def setUp(self) -> None:
        self.connection = establish_connection()
        self.cursor = self.connection.cursor()

    def test_insert_game(self):
        self.assertTrue(insert_game(1, "Game1", 1))
        self.assertFalse(insert_game(1, "Game2", 2))
        self.cursor.execute("DELETE FROM Game WHERE Game_ID = 1")
        self.connection.commit()

    def test_insert_crew_json(self):
        insert_game(1, "Game1", 1)
        self.assertTrue(insert_crew_json(1, '{"Assassins": "Hit man"}'))

        # Game_ID not present
        self.assertFalse(insert_crew_json(2, '{"Assassins": "Hit man"}'))

        # crew_json parameter not json string
        self.assertFalse(insert_crew_json(1, 'Assassins'))

        self.cursor.execute("DELETE FROM Game WHERE Game_ID = 1")
        self.connection.commit()

    def test_insert_crafted_item_json(self):
        insert_game(1, "Game1", 1)
        self.assertTrue(insert_crafted_item_json(1, '{"Aerondight": "Magical silver sword"}'))

        # Game_ID not present
        self.assertFalse(insert_crafted_item_json(2, '{"Aerondight": "Magical silver sword"}'))

        # crafted_item_json parameter not json string
        self.assertFalse(insert_crafted_item_json(1, 'Aerondight: Magical silver sword'))

        self.cursor.execute("DELETE FROM Game WHERE Game_ID = 1")
        self.connection.commit()

    def test_insert_npc_json(self):
        insert_game(1, "Game1", 1)
        self.assertTrue(insert_npc_json(1, '{"Dandelion": "An humble bard"}'))

        # Game_ID not present
        self.assertFalse(insert_npc_json(2, '{"Dandelion": "An humble bard"}'))

        # npc_json parameter not json string
        self.assertFalse(insert_npc_json(1, 'Dandelion: An humble bard'))

        self.cursor.execute("DELETE FROM Game WHERE Game_ID = 1")
        self.connection.commit()

    def test_insert_faction_json(self):
        insert_game(1, "Game1", 1)
        self.assertTrue(insert_faction_json(1, '{"The Unseen": "One you see them you can not unsee them"}'))

        # Game_ID not present
        self.assertFalse(insert_faction_json(2, '{"The Unseen": "One you see them you can not unsee them"}'))

        # faction_json parameter not json string
        self.assertFalse(insert_faction_json(1, 'The Unseen: One you see them you can not unsee them'))

        self.cursor.execute("DELETE FROM Game WHERE Game_ID = 1")
        self.connection.commit()

    def test_insert_score_json(self):
        insert_game(1, "Game1", 1)
        self.assertTrue(insert_score_json(1, '{"Jenny o the Woods": "Love can make you become a nightwraith"}'))

        # Game_ID not present
        self.assertFalse(insert_score_json(2, '{"Jenny o the Woods": "Love can make you become a nightwraith"}'))

        # score_json parameter not json string
        self.assertFalse(insert_score_json(1, 'Jenny o the Woods: Love can make you become a nightwraith'))

        self.cursor.execute("DELETE FROM Game WHERE Game_ID = 1")
        self.connection.commit()

    def test_insert_clock_json(self):
        insert_game(1, "Game1", 1)
        self.assertTrue(insert_clock_json(1, '{"Healing": "How long will it take?"}'))

        # Game_ID not present
        self.assertFalse(insert_clock_json(2, '{"Healing": "How long will it take?"}'))

        # clock_json parameter not json string
        self.assertFalse(insert_clock_json(1, 'Healing: How long will it take?'))

        self.cursor.execute("DELETE FROM Game WHERE Game_ID = 1")
        self.connection.commit()

    def test_insert_journal(self):
        insert_game(1, "Game1", 1)
        self.assertTrue(insert_journal(1, "Welcome to Blades in the Dark"))

        # Game_ID not present
        self.assertFalse(insert_journal(2, "Welcome to Blades in the Dark"))

        self.cursor.execute("DELETE FROM Game WHERE Game_ID = 1")
        self.connection.commit()

    def test_insert_state(self):
        insert_game(1, "Game1", 1)
        self.assertTrue(insert_state(1, 1))

        # Game_ID not present
        self.assertFalse(insert_state(2, 1))

        self.cursor.execute("DELETE FROM Game WHERE Game_ID = 1")
        self.connection.commit()

    def test_insert_user(self):
        self.assertTrue(insert_user(1, "Aldo"))

        # Tel_ID already present
        self.assertTrue(insert_user(1, "Giacomo"))

        self.cursor.execute("DELETE FROM User WHERE Tel_ID = 1")
        self.connection.commit()

    def test_insert_user_game(self):
        insert_game(-1, "Game1", -1)
        insert_user(-1, "Aldo")
        insert_user(-2, "Giovanni")
        insert_user(-3, "Giacomo")

        self.assertTrue(insert_user_game(-1, -1, '{"Ronny": "A whisper"}', False))
        self.assertTrue(insert_user_game(-2, -1, master=True))
        self.assertTrue(insert_user_game(-3, -1))

        # Game_ID not present
        self.assertFalse(insert_user_game(-1, 2))

        # User_ID not present
        self.assertFalse(insert_user_game(4, -1))

        self.cursor.execute("DELETE FROM Game WHERE Game_ID = -1")
        self.cursor.execute("DELETE FROM User WHERE Tel_ID = -1 or Tel_ID = -2 or Tel_ID = -3")
        self.cursor.execute("DELETE FROM User_Game "
                            "WHERE Game_ID = -1 and (User_ID = -1 or User_ID = -2 or User_ID = -3)")

        self.connection.commit()

    def test_insert_character_sheet(self):
        self.assertTrue(insert_character_sheet("Witchers", "Welcome to Kaer Morhen"))

        # Class already present
        self.assertFalse(insert_character_sheet("Witchers", "Welcome to Kaer Morhen"))

        self.cursor.execute("DELETE FROM CharacterSheet WHERE Class = 'Witchers'")
        self.connection.commit()

    def test_insert_claim(self):
        self.assertTrue(insert_claim("Toussaint Prison", "Old leper colony", True))
        self.assertTrue(insert_claim("Corvo Bianco", "Richest Vineyard", False))

        # Name already present
        self.assertFalse(insert_claim("Toussaint Prison", "Not a prison", False))

        self.cursor.execute("DELETE FROM Claim WHERE Name = 'Toussaint Prison' or Name = 'Corvo Bianco'")
        self.connection.commit()

    def test_insert_crew_sheet(self):
        self.assertTrue(insert_crew_sheet("The Lodge", "Most powerful mages"))

        # Type already present
        self.assertFalse(insert_crew_sheet("The Lodge", "Not so powerful mages"))

        self.cursor.execute("DELETE FROM CrewSheet WHERE Type = 'The Lodge'")
        self.connection.commit()

    def test_insert_hunting_ground(self):
        self.assertTrue(insert_hunting_ground("Tracking", "Find anybody anywhere"))

        # Name already present
        self.assertFalse(insert_hunting_ground("Tracking", "Can't even find my sword "))

        self.cursor.execute("DELETE FROM HuntingGround WHERE Name = 'Tracking'")
        self.connection.commit()

    def test_insert_item(self):
        self.assertTrue(insert_item("Aerondight", "Magical silver sword", 2, -1))
        self.assertTrue(insert_item("Crossbow", "Like an arrow but powerful", 0, 3))

        # Name already present
        self.assertFalse(insert_item("Aerondight", "Not so magical rusted sword", 2, -1))

        # Usages lower than -1
        self.assertFalse(insert_item("Superior Blizzard", "Time slows", 0, -2))

        # Weight lower than 0
        self.assertFalse(insert_item("Superior Cat", "Can see in pitch black", -1, 1))

        self.cursor.execute("DELETE FROM Item WHERE Name = 'Aerondight' or Name = 'Crossbow'")
        self.connection.commit()

    def test_insert_npc(self):
        self.assertTrue(insert_npc("Dandelion", "An humble bard", "Ink Rakes", "Always talks"))
        self.cursor.execute("SELECT MAX(NpcID) FROM NPC")
        dandelion = self.cursor.fetchone()[0]

        # Faction not present
        self.assertFalse(insert_npc("Ciri", "A princess", "The Empire", "An annoying girl"))

        self.cursor.execute("DELETE FROM NPC WHERE NpcID = {}".format(dandelion))
        self.connection.commit()

    def test_insert_special_ability(self):
        self.assertTrue(insert_special_ability("Cat eyes", "Can see in the dark"))

        # Name already present
        self.assertFalse(insert_special_ability("Cat eyes", "Your pupil has another shape"))

        self.cursor.execute("DELETE FROM SpecialAbility WHERE Name = 'Cat eyes'")
        self.connection.commit()

    def test_insert_upgrade(self):
        self.assertTrue(insert_upgrade("Roach", 2, "New horse"))

        # Quality lower than 0
        self.assertFalse(insert_upgrade("Bear school armor", -1, "New armor"))

        # Name already present
        self.assertFalse(insert_upgrade("Roach", 0, "Really slow horse"))

        self.cursor.execute("DELETE FROM Upgrade WHERE Name = 'Roach'")
        self.connection.commit()

    def test_insert_xp_trigger(self):
        self.assertTrue(insert_xp_trigger("When you drink with others you will obtain exp", True))
        self.cursor.execute("SELECT MAX(XpID) FROM XpTrigger")
        drink = self.cursor.fetchone()[0]

        self.assertTrue(insert_xp_trigger("Slain monsters and get exp", False))
        self.cursor.execute("SELECT MAX(XpID) FROM XpTrigger")
        slain = self.cursor.fetchone()[0]

        self.cursor.execute("DELETE FROM XpTrigger WHERE XpID = {} or XpID = {}".format(drink, slain))
        self.connection.commit()

    def test_insert_simple_relation(self):
        self.assertTrue(insert_simple_relation("Char_Friend", "Whisper", 18))

        # Table not present
        self.assertFalse(insert_simple_relation("Char_Enemy", "Hound", 13))

        # First column is not present
        self.assertFalse(insert_simple_relation("Crew_HG", "Slaughter", "Assassins"))

        # Second column is not present
        self.assertFalse(insert_simple_relation("Char_Item", "Leech", True))

        self.cursor.execute("DELETE FROM Char_Friend WHERE Character = 'Whisper' and NPC = 18")
        self.connection.commit()

    def test_insert_complex_relation(self):
        self.assertTrue(insert_complex_relation("Char_Action", "Hull", "Prowl", True))

        # Table is not present
        self.assertFalse(insert_complex_relation("Char_Upgrade", "Whisper", "Skirmish", 3))

        # First column is not present
        self.assertFalse(insert_complex_relation("Crew_StartingUpgrade", "Killers", "Gear", 1))

        # Second column is not present
        self.assertFalse(insert_complex_relation("Char_Xp", "Leech", 30, True))

        # Third column is not of right type
        self.assertFalse(insert_complex_relation("Crew_SA", "Assassins", "Mule", 2))

        self.cursor.execute("DELETE FROM Char_Action WHERE Character = 'Hull' and Action = 'Prowl'")
        self.connection.commit()

    def test_delete_user_game(self):
        insert_game(-1, "Game1", -1)
        insert_user(-1, "Aldo")

        insert_user_game(-1, -1, '{"Jonny": "A whisper"}', False)

        delete_user_game(-1, -1)

        self.cursor.execute("DELETE FROM Game WHERE Game_ID = -1")
        self.cursor.execute("DELETE FROM User WHERE Tel_ID = -1")

        self.connection.commit()
