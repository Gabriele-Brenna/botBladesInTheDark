import sqlite3
from typing import List

from component.SpecialAbility import SpecialAbility

connection = sqlite3.connect('mydata.db')
cursor = connection.cursor()


def get_special_abilities(name: str = None, peculiar: bool = False) -> List[SpecialAbility]:
    """
    Creates a parametric query to retrieve from database name and description of specified special abilities.

    :param name: represents the name of the ability to get;
        if it is None, the complete list of special abilities is retrieved;
        if peculiar is set to True this parameter represents the class of interest.
    :param peculiar: if True, the search is restricted to peculiar abilities only.
    :return: a list of SpecialAbility objects
    """

    q_select = "SELECT S.name, S.description"

    q_from = "\nFROM SpecialAbility S"

    q_where = "\n"

    if peculiar is True:
        q_from += " NATURAL JOIN Char_SA C"
        q_where += "WHERE C.peculiar = true"
        if name is not None:
            q_where += " AND C.class = '{}'".format(name)

    else:
        if name is not None:
            q_where += "WHERE S.name = '{}'".format(name)

    cursor.execute(q_select+q_from+q_where)

    rows = cursor.fetchall()
    abilities = []

    for ability in rows:
        abilities.append(SpecialAbility(ability[0], ability[1]))

    return abilities
