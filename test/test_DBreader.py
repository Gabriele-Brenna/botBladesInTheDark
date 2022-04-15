from unittest import TestCase

from controller.DBreader import *


class TestDBReader(TestCase):

    def setUp(self) -> None:
        root = Path(__file__).parent.parent.resolve()
        root = os.path.join(root, "resources")
        path = os.path.join(root, 'BladesInTheDark.db')
        self.connection = sqlite3.connect(path)
        self.cursor = connection.cursor()

    def test_query_special_abilities(self):
        self.assertEqual([SpecialAbility("Mule", "Your load limits are higher. Light: 5. Normal: 7. Heavy: 8.")],
                         query_special_abilities("Mule"))
        self.assertEqual([SpecialAbility("Battleborn", "You may expend your special armor to reduce harm from an "
                                                       "attack in combat or to push yourself during a fight. ")],
                         query_special_abilities("Cutter", True))

    def test_query_xp_triggers(self):
        # TODO
        pass

    def test_exists_character(self):
        self.assertTrue(exists_character("Hound"))
        self.assertFalse(exists_character("Dark Elf"))

    def test_exists_crew(self):
        self.assertTrue(exists_crew("Cult"))
        self.assertFalse(exists_crew("Whalers"))

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

        cursor.execute("""SELECT COUNT(*) FROM CharacterSheet""")
        query = cursor.fetchall()[0][0]

        self.assertEqual(query, len(query_character_sheets()))

    def test_query_attributes(self):
        self.assertEqual([Attribute("Insight", query_action_list("Insight")),
                          Attribute("Prowess", query_action_list("Prowess")),
                          Attribute("Resolve", query_action_list("Resolve"))], query_attributes())
