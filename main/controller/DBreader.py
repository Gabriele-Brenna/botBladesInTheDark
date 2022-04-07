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

    cursor.execute(q_select + q_from + q_where)

    rows = cursor.fetchall()
    abilities = []

    for ability in rows:
        abilities.append(SpecialAbility(ability[0], ability[1]))

    return abilities


def is_crew(sheet: str) -> bool:
    """
    Checks if the given sheet appears in the Crew table or in the Character table in the database.
    Raises an exception if the sheet doesn't appear in the database.
    :param sheet: represents the sheet to check
    :return: True if the sheet is a Crew, False if the sheet is a Character
    """
    query = """
    SELECT *
    FROM CrewSheet
    WHERE name = '{}'
    """.format(sheet)

    cursor.execute(query)
    rows = cursor.fetchall()

    if not rows:
        query.replace("CrewSheet", "CharacterSheet")

        cursor.execute(query)
        rows = cursor.fetchall()

        if not rows:
            raise Exception("{} is not a sheet!".format(sheet))

        return False

    return True


def get_xp_triggers(sheet: str = None, peculiar: bool = False) -> List[str]:
    """
    Creates a parametric query to retrieve from database specified xp triggers.

    :param sheet: represents the sheet of the Crew or Character of interest.
        If this parameter is None and peculiar is False, the complete list of xp trigger is retrieved;
        If this parameter is None and peculiar is True, only the peculiar xp triggers of each sheet are retrieved;
        If this parameter is not None, the targets are the triggers of the specified sheet.
    :param peculiar: True if only the peculiar triggers are the targets, False if all the triggers are the targets
    :return: a list of strings, representing the xp triggers
    """
    q_select = "SELECT X.trigger"

    q_from = "\nFROM XpTrigger X"

    q_where = "\n"

    try:
        if sheet is not None:
            if is_crew(sheet):
                q_where += "WHERE Crew = '{}' ".format(sheet)
                if not peculiar:
                    q_where += "OR Crew_Char = true"
            else:
                q_where += "WHERE Character = '{}' ".format(sheet)
                if not peculiar:
                    q_where += "OR Crew_Char = false"
        else:
            if peculiar:
                q_where += "WHERE Crew IS NOT NULL OR Character IS NOT NULL"

        cursor.execute(q_select + q_from + q_where)
        rows = cursor.fetchall()

        xp_triggers = []
        for trigger in rows:
            xp_triggers.append(trigger[0])

        return xp_triggers

    except Exception:
        return []
