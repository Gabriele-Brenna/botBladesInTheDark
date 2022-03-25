from typing import List


class HarmBox:
    def __init__(self, harms: List[List[str]] = List[List[None], List[None], List[None]]) -> None:
        self.harms = harms

    def insert_harm(self, level: int, description: str) -> int:
        if level == len(self.harms):
            if len(self.harms[-1]) == 0:
                self.harms[-1].append(description)
                return level
            else:
                return level+1
        else:
            if len(self.harms[level-1]) < 2:
                self.harms[level-1].append(description)
                return level
            else:
                return self.insert_harm(level+1, description)

    def heal_harm(self):
        self.harms[0].clear()
        for i in range(len(self.harms)-1):
            for harm in self.harms[i+1]:
                self.harms[i].append(harm)
            self.harms[i+1].clear()

    def count_harm(self, level: int) -> int:
        return len(self.harms[level-1])

