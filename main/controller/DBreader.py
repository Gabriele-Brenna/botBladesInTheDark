import os
import sqlite3
from pathlib import Path
from sqlite3 import Connection
from typing import List, Tuple

from character.Action import Action
from character.Attribute import Attribute
from character.Vice import Vice
from component.SpecialAbility import SpecialAbility


def establish_connection() -> Connection:
    root_dir = Path(__file__).parent.parent.parent.resolve()
    root_dir = os.path.join(root_dir, "resources")
    db_path = os.path.join(root_dir, 'BladesInTheDark.db')
    return sqlite3.connect(db_path)


def query_special_abilities(special_ability: str = None, peculiar: bool = False) -> List[SpecialAbility]:
    """
    Creates a parametric query to retrieve from database name and description of specified special abilities.

    :param special_ability: represents the name of the ability to get;
        if it is None, the complete list of special abilities is retrieved;
        if peculiar is set to True this parameter represents the class of interest.
    :param peculiar: if True, the search is restricted to peculiar abilities only.
    :return: a list of SpecialAbility objects
    """
    connection = establish_connection()
    cursor = connection.cursor()

    q_select = "SELECT S.name, S.description"

    q_from = "\nFROM SpecialAbility S"

    q_where = "\n"

    if peculiar is True:
        special_ability = special_ability.lower().capitalize()
        if exists_character(special_ability):
            q_from += " JOIN Char_SA C ON S.name = C.SpecialAbility"
            q_where += "WHERE C.peculiar is True"
            if special_ability is not None:
                q_where += " AND C.character = '{}'".format(special_ability)
        elif exists_crew(special_ability):
            q_from += " JOIN Crew_SA C ON S.name = C.SpecialAbility"
            q_where += "WHERE C.peculiar is True"
            if special_ability is not None:
                q_where += " AND C.crew = '{}'".format(special_ability)
        else:
            return []

    else:
        if special_ability is not None:
            q_where += "WHERE S.name = '{}'".format(special_ability)

    cursor.execute(q_select + q_from + q_where)

    rows = cursor.fetchall()
    abilities = []

    for ability in rows:
        abilities.append(SpecialAbility(ability[0], ability[1]))

    return abilities


def query_xp_triggers(sheet: str = None, peculiar: bool = None) -> List[str]:
    """
    Creates a parametric query to retrieve from database specified xp triggers.

    :param sheet: represents the sheet of the Crew or PC of interest.
        If this parameter is None and peculiar is None, the complete list of xp triggers is retrieved;
        If this parameter is not None, the targets are the triggers of the specified sheet.
    :param peculiar: True if only the peculiar triggers are the targets, False if all the triggers are the targets
    :return: a list of strings, representing the xp triggers
    """
    connection = establish_connection()
    cursor = connection.cursor()

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

        if peculiar is not None:
            q_where += "and Peculiar is {}".format(peculiar)
        query = q_select + q_from + q_where
    else:
        if peculiar is not None:
            query = """
            SELECT Description
            FROM XpTrigger NATURAL JOIN Crew_Xp 
            WHERE Peculiar is {}
            UNION
            SELECT Description
            FROM XpTrigger NATURAL JOIN Char_Xp 
            WHERE Peculiar is {}""".format(peculiar, peculiar)

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
    connection = establish_connection()
    cursor = connection.cursor()

    cursor.execute("""
            SELECT *
            FROM CharacterSheet
            WHERE class = '{}'
            """.format(sheet.lower().capitalize()))

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
    connection = establish_connection()
    cursor = connection.cursor()

    cursor.execute("""
            SELECT *
            FROM CrewSheet
            WHERE type = '{}'
            """.format(sheet.lower().capitalize()))

    rows = cursor.fetchall()

    if not rows:
        return False
    return True


def query_action_list(attr: str) -> List[Action]:
    """
    Retrieve the list of Actions of the specified attribute

    :param attr: is the Attribute of interest
    :return: a list of Actions
    """
    connection = establish_connection()
    cursor = connection.cursor()

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


def query_vice(vice: str = None, character_class: str = None) -> List[Vice]:
    """
    Retrieves the list of Vices of the specified character class or the specified vice.

    :param vice: is the Vice of interest
    :param character_class: is the class of interest
    :return: a list of Vices
    """
    connection = establish_connection()
    cursor = connection.cursor()

    q_select = "SELECT name, description"
    q_from = "\nFROM Vice"
    q_where = "\n"

    if vice is not None:
        q_where += "WHERE name = '{}'".format(vice)

    else:
        if character_class is not None:
            q_where += "WHERE class = '{}'".format(str(character_class).capitalize())

    cursor.execute(q_select + q_from + q_where)

    rows = cursor.fetchall()

    vices = []
    for elem in rows:
        vices.append(Vice(elem[0], elem[1]))

    return vices


def query_character_sheets(canon: bool = None, spirit: bool = None) -> List[str]:
    """
    Retrieves the list of sheets of the specified character class or type.
    If default values are used (None) all the sheets are retrieved

    :param canon: if True the targets are all the canon sheets; if False the targets are all the non-canon sheets
    :param spirit: if True the targets are all the spirit sheets; if False the targets are all the non-spirit sheets
    :return: list of the required sheets
    """
    connection = establish_connection()
    cursor = connection.cursor()

    q_select = "SELECT class"
    q_from = "\nFROM CharacterSheet"
    q_where = "\n"

    if canon is not None:
        q_where += "WHERE canon IS {}".format(canon)

        if spirit is not None:
            q_where += " AND spirit IS {}".format(spirit)

    elif spirit is not None:
        q_where += "WHERE spirit IS {}".format(spirit)

    cursor.execute(q_select + q_from + q_where)

    rows = cursor.fetchall()

    sheets = []
    for elem in rows:
        sheets.append(elem[0])

    return sheets


def query_attributes() -> List[Attribute]:
    """
    Retrieves the list of all Attributes of the game

    :return: a list of Attributes with all the corresponding Actions
    """
    connection = establish_connection()
    cursor = connection.cursor()

    cursor.execute("""
    SELECT DISTINCT attribute
    FROM Action
    ORDER BY attribute
    """)

    attribute_names = []
    for elem in cursor.fetchall():
        attribute_names.append(elem[0])

    attributes = []
    for i in range(len(attribute_names)):
        attributes.append(Attribute(attribute_names[i], query_action_list(attribute_names[i])))

    return attributes


def query_initial_dots(sheet: str) -> List[Tuple[str, int]]:
    """
    Retrieves the initial Action dots of the specified character sheet.

    :param sheet: is the character sheet of interest
    :return: a list of tuples: each one contains the name of the action and its initial dots
    """
    connection = establish_connection()
    cursor = connection.cursor()

    cursor.execute("""
    SELECT Action, Dots
    FROM Char_Action 
    WHERE Character = '{}'  
    """.format(sheet))

    return cursor.fetchall()


def query_last_game_id() -> int:
    """
    Retrieves the last added game id

    :return: the maximum id value of game present in the DataBase. If there is no game, it returns 0.
    """
    connection = establish_connection()
    cursor = connection.cursor()

    cursor.execute("""
    SELECT Max(Game_ID)
    FROM Game
    """)

    result = cursor.fetchone()[0]
    if result is not None:
        return result
    else:
        return 0


def query_game_json(game_id: int, files: List = None) -> dict:
    """
    Retrieves selected json strings from the Game table in the BladesInTheDark DataBase related to a specific game ID

    :param game_id: int representing the ID of the specific Game
    :param files: list of files to retrieve from the table. If the list is None it will retrieve all the files.
    :return: dictionary containing the json strings got from the DataBase
    """
    connection = establish_connection()
    cursor = connection.cursor()

    q_select = "SELECT "
    if files is None:
        cursor.execute("""
        SELECT name
        FROM PRAGMA_TABLE_INFO('Game')
        WHERE name LIKE '%JSON%' or name = 'Journal'""")

        rows = cursor.fetchall()

        files = []
        for el in rows:
            files.append(el[0])

    for i in range(len(files) - 1):
        q_select += files[i] + ", "
    q_select += files[len(files) - 1]

    query = q_select + """
    FROM Game
    WHERE Game_ID = {}""".format(game_id)

    cursor.execute(query)
    rows = cursor.fetchall()

    dict_json = {}
    for i in range(len(files)):
        dict_json[files[i]] = rows[0][i]
    return dict_json


def query_users(game_id: int) -> List:
    """
    Retrieve all the User_ID and Name of the users with a specific Game_ID attribute

    :param game_id: int representing the specific Game_ID
    :return: list of tuples containing Tel_ID and Name of the users
    """
    connection = establish_connection()
    cursor = connection.cursor()

    cursor.execute("""
    SELECT Name, Tel_ID, Master 
    FROM User JOIN User_Game ON Tel_ID = User_ID
    WHERE Game_ID = {}""".format(game_id))
    return cursor.fetchall()


def query_pc_json(game_id: int) -> dict:
    """
    Retrieve all Users_ID and Char_JSON of a specific Game_ID

    :param game_id: int representing the specific Game_ID
    :return: dictionary containing all json files with their respective user
    """
    connection = establish_connection()
    cursor = connection.cursor()

    cursor.execute("""
    SELECT User_ID, Char_JSON
    FROM User_Game
    WHERE Game_ID = {}""".format(game_id))

    dict_json = {}
    rows = cursor.fetchall()

    for t in rows:
        dict_json[t[0]] = t[1]
    return dict_json
