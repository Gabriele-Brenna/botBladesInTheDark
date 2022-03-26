from typing import List
from random import randint


def roll_dice(dice: int = 1) -> List:
    rolls = []
    out = []
    if dice > 0:
        for i in range(dice):
            rolls.append(randint(1, 6))
        result = max(rolls)
    else:
        for i in range(2):
            rolls.append(randint(1, 6))
        result = min(rolls)
    if result == 6 and rolls.count(6) >= 2:
        out.append("CRIT")
    else:
        out.append(result)
    out.append(rolls)
    return out
