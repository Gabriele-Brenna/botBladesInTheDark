from typing import List


class Cohort:
    def __init__(self, type: List[str], armor: int, elite: bool, harm: int, expert: bool, flaws: List[str],
                 edges: List[str], scale: int, quality: int) -> None:
        self.type = type
        self.armor = armor
        self.elite = elite
        self.harm = harm
        self.expert = expert
        self.flaws = flaws
        self.edges = edges
        self.scale = scale
        self.quality = quality

    def add_harm(self, n: int):
        self.harm += n

    def add_type(self, new_type: str):
        self.type.append(new_type)

    def add_flaw(self, new_flaw: str):
        self.type.append(new_flaw)

    def add_edge(self, new_edge: str):
        self.type.append(new_edge)

    def __str__(self) -> str:
        return """
        {},
        Edges: {},
        Flaws: {},
        Scale: {},
        Quality: {}
        
        Harm Level: {}
        Armor: {}
        """.format("Expert" if self.expert is True else "Gang", self.edges, self.flaws, self.scale, self.quality,
                   self.harm, self.armor)
