from unittest import TestCase

from character.Vice import Vice


class TestVice(TestCase):

    def setUp(self) -> None:
        self.vice1 = Vice("pleasure",
                          "Gratification from lovers, food, drink, drugs, art, theater, ecc.",
                          "Lady Freyla, the Emperor’s Cask, bar, Whitecrown")
        self.vice2 = Vice("gambling",
                          "You crave games of chance, betting on sporting events, etc.")

    def test_add_purveyor(self):
        self.vice2.add_purveyor("Spogg’s dice game, Crow’s Foot")
        self.assertEqual("Spogg’s dice game, Crow’s Foot", self.vice2.purveyor)

    def test_remove_purveyor(self):
        self.vice1.remove_purveyor()
        self.assertIsNone(self.vice1.purveyor)