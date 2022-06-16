from typing import List


class Cohort:
    """
     Gang or an expert who works for your crew.
    """
    def __init__(self, type: List[str] = None, armor: int = 0, elite: bool = False, harm: int = 0, expert: bool = False,
                 flaws: List[str] = None, edges: List[str] = None, scale: int = 0, quality: int = 0) -> None:
        """
        Constructor of Cohort. It takes all the parameters necessary to model this object.

        :param type: a list of strings that represents the cohort's types.
        :param armor: an int that represents the level of armor of the cohort.
        :param elite: a boolean value: True if the cohort is elite, False otherwise.
        :param harm: an int that represents the level of harm of the cohort.
        :param expert: a boolean value: True if the cohort is an expert, False if it's a gang.
        :param flaws: a list of strings that represents the flaws of the cohort.
        :param edges: a list of strings that represents the edges of the cohort.
        :param scale: represents the quantity of the members of the cohort.
        :param quality: represents the quality of the cohort.
        """
        if type is None:
            type = []
        if isinstance(type, str):
            type = [type]
        self.type = type
        self.armor = armor
        self.elite = elite
        self.harm = harm
        self.expert = expert
        if flaws is None:
            flaws = []
        self.flaws = flaws
        if edges is None:
            edges = []
        self.edges = edges
        self.scale = scale
        self.quality = quality

    def add_harm(self, n: int):
        """
        Adds the specified amount of harm

        :param n: the amount of harm to add
        """
        self.harm += n
        if self.harm > 4:
            self.harm = 4
        if self.harm < 0:
            self.harm = 0

    def add_type(self, new_type: str):
        """
        Adds the specified type of gang/expert

        :param new_type: the new type to add
        """
        self.type.append(new_type)

    def add_flaw(self, new_flaw: str):
        """
        Adds the specified flaw to the gang/expert

        :param new_flaw: the new flaw to add
        """
        self.flaws.append(new_flaw)

    def add_edge(self, new_edge: str):
        """
        Adds the specified flaw to the gang/expert

        :param new_edge: the new edge to add
        """
        self.edges.append(new_edge)

    def add_armor(self, armor: int):
        """
        Adds the specified amount of armor to the cohort (0 is the minimum value for the armor attribute)

        :param armor: an int representing the armor levels to add
        """
        self.armor += armor
        if self.armor < 0:
            self.armor = 0
        if self.armor > 99:
            self.armor = 99

    @classmethod
    def from_json(cls, data):
        """
        Method used to create an instance of this object given a dictionary

        :param data: dictionary of the object
        :return: Cohort
        """
        return cls(**data)

    def __repr__(self) -> str:
        return """
        {} {}:
        Edges: {},
        Flaws: {},
        Scale: {},
        Quality: {}
        
        Harm Level: {}
        Armor: {}
        """.format(self.type, "Expert" if self.expert is True else "Gang", self.edges, self.flaws, self.scale, self.quality,
                   self.harm, self.armor)

    def __eq__(self, o: object) -> bool:
        return isinstance(o, self.__class__) and o.__dict__ == self.__dict__
