import os
import sqlite3
from pathlib import Path
from typing import List

from character.Action import Action
from character.Vice import Vice
from component.SpecialAbility import SpecialAbility

root_dir = Path(__file__).parent.parent.parent.resolve()
root_dir = os.path.join(root_dir, "resources")
db_path = os.path.join(root_dir, 'BladesInTheDark.db')
connection = sqlite3.connect(db_path)
cursor = connection.cursor()


def query_special_abilities(special_ability: str = None, peculiar: bool = False) -> List[SpecialAbility]:
    """
    Creates a parametric query to retrieve from database name and description of specified special abilities.

    :param special_ability: represents the name of the ability to get;
        if it is None, the complete list of special abilities is retrieved;
        if peculiar is set to True this parameter represents the class of interest.
    :param peculiar: if True, the search is restricted to peculiar abilities only.
    :return: a list of SpecialAbility objects
    """

    q_select = "SELECT S.name, S.description"

    q_from = "\nFROM SpecialAbility S"

    q_where = "\n"

    if peculiar is True:
        q_from += " JOIN Char_SA C ON S.name = C.SpecialAbility"
        q_where += "WHERE C.peculiar is True"
        if special_ability is not None:
            q_where += " AND C.character = '{}'".format(special_ability)

    else:
        if special_ability is not None:
            q_where += "WHERE S.name = '{}'".format(special_ability)

    cursor.execute(q_select + q_from + q_where)

    rows = cursor.fetchall()
    abilities = []

    for ability in rows:
        abilities.append(SpecialAbility(ability[0], ability[1]))

    return abilities


def query_xp_triggers(sheet: str = None, peculiar: bool = False) -> List[str]:
    """
    Creates a parametric query to retrieve from database specified xp triggers.

    :param sheet: represents the sheet of the Crew or Character of interest.
        If this parameter is None and peculiar is False, the complete list of xp triggers is retrieved;
        If this parameter is None and peculiar is True, only the peculiar xp triggers of each sheet are retrieved;
        If this parameter is not None, the targets are the triggers of the specified sheet.
    :param peculiar: True if only the peculiar triggers are the targets, False if all the triggers are the targets
    :return: a list of strings, representing the xp triggers
    """
    q_select = "SELECT Description"

    q_from = "\nFROM XpTrigger"

    q_where = "\n"

    query = q_select + q_from + q_where

    if sheet is not None:
        if exists_crew(sheet):
            q_from += " NATURAL JOIN Crew_Xp"
            q_where += "WHERE Crew = '{}' ".format(sheet)

        elif exists_character(sheet):
            q_from += " NATURAL JOIN Char_Xp"
            q_where += "WHERE Character = '{}' ".format(sheet)

        else:
            return []

        if not peculiar:
            q_where += "and Peculiar is False"
        query = q_select + q_from + q_where
    else:
        if peculiar:
            query = """
            SELECT Description
            FROM XpTrigger NATURAL JOIN Crew_Xp 
            WHERE Peculiar is True
            UNION
            SELECT Description
            FROM XpTrigger NATURAL JOIN Char_Xp 
            WHERE Peculiar is True"""

    cursor.execute(query)
    rows = cursor.fetchall()

    xp_triggers = []
    for trigger in rows:
        xp_triggers.append(trigger[0])

    return xp_triggers


def exists_character(sheet: str) -> bool:
    """
    Checks if the specified sheet has a matching value in the CharacterSheet table of the database

    :param sheet: is the character to check
    :return: True if the character exists, False otherwise
    """
    cursor.execute("""
            SELECT *
            FROM CharacterSheet
            WHERE class = '{}'
            """.format(sheet))

    rows = cursor.fetchall()

    if not rows:
        return False
    return True


def exists_crew(sheet: str) -> bool:
    """
    Checks if the specified sheet has a matching value in the CrewSheet table of the database

    :param sheet: is the crew to check
    :return: True if the crew exists, False otherwise
    """
    cursor.execute("""
            SELECT *
            FROM CrewSheet
            WHERE type = '{}'
            """.format(sheet))

    rows = cursor.fetchall()

    if not rows:
        return False
    return True


def query_action_list(attr: str) -> List[Action]:
    """
    Retrieve the list of Actions of the specified attribute

    :param attr:
    :return:
    """
    cursor.execute("""
    SELECT name
    FROM Action
    WHERE attribute = '{}'
    """.format(attr))

    rows = cursor.fetchall()

    actions = []
    for action in rows:
        actions.append(Action(str(action[0]).lower()))

    return actions


def query_vice(vice: str = None, hull: bool = None) -> List[Vice]:

    q_select = "SELECT name, description"
    q_from = "\nFROM Vice"
    q_where = "\n"

    if vice is not None:
        q_where += "WHERE name = '{}'".format(vice)

    else:
        if hull is not None:
            q_where += "WHERE hull = '{}'".format(str(hull).upper())

    print(q_select+q_from+q_where)
    cursor.execute(q_select+q_from+q_where)

    rows = cursor.fetchall()

    vices = []
    for elem in rows:
        vices.append(Vice(elem[0], elem[1]))

    return vices
