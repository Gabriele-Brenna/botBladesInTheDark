from typing import List, Tuple, Union
from random import randint


def roll_dice(dice: int = 1) -> Tuple[Union[int, str], List[int]]:
    """
    Throws the specified amount of 6-sided dice (if 0 is selected the roll happens with 2 dice and the final outcome
    is the lower die)

    :param dice: the number of dice to roll.
    :return: a tuple of results: the first element is the outcome of the roll,
            the second is a list of all the rolls' results.
    """
    rolls = []
    if dice > 0:
        for i in range(dice):
            rolls.append(randint(1, 6))
        result = max(rolls)
    else:
        for i in range(2):
            rolls.append(randint(1, 6))
        result = min(rolls)
    if result == 6 and rolls.count(6) >= 2:
        result = "CRIT"

    return result, rolls

