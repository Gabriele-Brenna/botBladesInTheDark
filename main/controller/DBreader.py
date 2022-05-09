from typing import List, Tuple, Dict, Union

from character.Action import Action
from character.Attribute import Attribute
from character.NPC import NPC
from character.Vice import Vice
from component.SpecialAbility import SpecialAbility
from controller.DBmanager import *


def query_special_abilities(sheet: str = None, peculiar: bool = None, special_ability: str = None,
                            as_dict: bool = False) -> Union[List[SpecialAbility], List[Dict[str, str]]]:
    """
    Creates a parametric query to retrieve from database name and description of specified special abilities.

    :param sheet: represents the sheet of interest, both crews and characters.
    :param peculiar: if True, the search is restricted to peculiar abilities only.
    :param special_ability: represents the name of the ability to get;
        if it is None, the complete list of special abilities is retrieved;
    :param as_dict: if True the result objects will be returned as dictionaries.
    :return: a list of SpecialAbility objects
    """
    connection = establish_connection()
    cursor = connection.cursor()

    q_select = "SELECT Name, Description"

    q_from = "\nFROM SpecialAbility"

    q_where = "\n"

    if special_ability is not None:
        q_where += "WHERE Name = '{}'".format(special_ability)

    else:
        if sheet is not None:
            if exists_crew(sheet):
                q_from += " JOIN Crew_SA ON Name = SpecialAbility"
                q_where += "WHERE Crew = '{}'".format(sheet)
            elif exists_character(sheet):
                q_from += " JOIN Char_SA ON Name = SpecialAbility"
                q_where += "WHERE Character = '{}'".format(sheet)
            else:
                return []
            if peculiar is not None:
                q_where += " AND peculiar is {}".format(peculiar)
        elif peculiar is not None:
            q_from = "\nFROM (SpecialAbility S LEFT JOIN Crew_SA CREW ON S.Name = CREW.SpecialAbility) LEFT JOIN " \
                     "Char_SA CHAR ON S.Name = CHAR.SpecialAbility "
            q_where += "WHERE CREW.peculiar is {} OR CHAR.peculiar is {}".format(peculiar, peculiar)

    cursor.execute(q_select + q_from + q_where)

    rows = cursor.fetchall()

    abilities = []
    for elem in rows:
        abilities.append({"name": elem[0], "description": elem[1]})

    if not as_dict:
        for i in range(len(abilities)):
            abilities[i] = SpecialAbility(**abilities[i])

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


def query_action_list(attr: str = None, as_list: bool = False) -> Union[List[Action], List[str]]:
    """
    Retrieve the list of Actions of the specified attribute

    :param attr: is the Attribute of interest
    :param as_list: if True the result objects will be returned as a list of strings.
    :return: a list of Actions
    """
    connection = establish_connection()
    cursor = connection.cursor()

    query = """
    SELECT name
    FROM Action"""

    if attr is not None:
        query += "\nWHERE attribute = '{}'".format(attr)

    cursor.execute(query)

    rows = cursor.fetchall()

    actions = []
    for action in rows:
        if as_list:
            actions.append(str(action[0]).lower())
        else:
            actions.append(Action(str(action[0]).lower()))

    return actions


def query_vice(vice: str = None, character_class: str = None,
               as_dict: bool = False) -> Union[List[Vice], List[Dict[str, str]]]:
    """
    Retrieves the list of Vices of the specified character class or the specified vice.

    :param vice: is the Vice of interest
    :param character_class: is the class of interest
    :param as_dict: if True the result objects will be returned as dictionaries.
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
        vices.append({"name": elem[0], "description": elem[1]})

    if not as_dict:
        for i in range(len(vices)):
            vices[i] = Vice(**vices[i])

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


def query_attributes(only_names: bool = False) -> Union[List[Attribute], List[str]]:
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

    if not only_names:
        attributes = []
        for i in range(len(attribute_names)):
            attributes.append(Attribute(attribute_names[i], query_action_list(attribute_names[i])))

        return attributes
    return attribute_names


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
    Retrieves selected json strings from the Game table in the BladesInTheDark DataBase related to a specific game ID.

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
        WHERE name LIKE '%JSON%' or name = 'Journal' or name = 'State'""")

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


def query_users_from_game(game_id: int) -> List[Tuple[str, int, bool]]:
    """
    Retrieve all the User_ID and Name of the users with a specific Game_ID attribute.

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
    Retrieve all Users_ID and Char_JSON of a specific Game_ID.

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


def query_lang(game_id: int) -> str:
    """
    Retrieve the language preferred in a specific Game.

    :param game_id: int representing the specific Game
    :return: str representing the language
    """
    connection = establish_connection()
    cursor = connection.cursor()

    cursor.execute("""
    SELECT Language
    FROM Game
    WHERE Game_ID = {}""".format(game_id))

    return cursor.fetchone()[0]


def query_games_info(chat_id: int = None, game_id: int = None) -> List[Dict]:
    """
    Retrieves the Game_ID, Title and Tel_Chat_ID of all the games stored in the Data Base

    :param chat_id: if this parameter is passed, only the info about the game of the specified chat are retrieved.
    :param game_id: if this parameter is passed, only the info of the specified game are retrieved.
    :return:
    """
    connection = establish_connection()
    cursor = connection.cursor()

    query = """
       SELECT Game_ID, Title, Tel_Chat_ID
       FROM Game"""

    if chat_id is not None:
        query += "\nWHERE Tel_Chat_ID = {}".format(chat_id)

    elif game_id is not None:
        query += "\nWHERE Game_ID = {}".format(game_id)

    cursor.execute(query)

    games_info = []
    rows = cursor.fetchall()

    if rows:
        for t in rows:
            games_info.append({"identifier": t[0], "title": t[1], "chat_id": t[2]})
    return games_info


def query_users_names(user_id: int = None) -> List[str]:
    """
    Retrieves the list of registered users' names.

    :param user_id: if passed, the specific username associated to this id is searched.
    :return: a list of usernames
    """

    connection = establish_connection()
    cursor = connection.cursor()

    query = """
    SELECT Name
    FROM User"""

    if user_id is not None:
        query += "\nWHERE Tel_ID = {}".format(user_id)

    cursor.execute(query)

    rows = cursor.fetchall()

    usernames = []
    for user in rows:
        usernames.append(user[0])
    return usernames


def query_game_ids(tel_chat_id: int = None, title: str = None) -> List[int]:
    """
    Retrieves a list of Game IDs from the Game table in the DB.
    If no arguments are passed, it retrieves all the IDs of the games.

    :param tel_chat_id: the Telegram chat ID of interest.
    :param title: The title of the games of interest.
    :return: a list of int IDs.
    """
    connection = establish_connection()
    cursor = connection.cursor()

    query = """
    SELECT Game_ID
    FROM Game"""

    if tel_chat_id is not None and title is not None:
        query += "\nWHERE (Tel_Chat_ID, Title) = ({}, '{}')".format(tel_chat_id, title)
    elif tel_chat_id is not None:
        query += "\nWHERE Tel_Chat_ID = {}".format(tel_chat_id)
    elif title is not None:
        query += "\nWHERE Title = '{}'".format(title)

    cursor.execute(query)

    rows = cursor.fetchall()

    ids = []
    for elem in rows:
        ids.append(elem[0])
    return ids


def query_char_strange_friends(pc_class: str = None, strange_friend: str = None,
                               as_dict: bool = False) -> Union[List[NPC], List[Dict[str, str]]]:
    connection = establish_connection()
    cursor = connection.cursor()

    query = """
    SELECT Name, Role
    FROM Char_Friend JOIN NPC ON NPC = NpcID"""

    if pc_class is not None and strange_friend is not None:
        query += "\nWHERE Character = '{}' AND Name = '{}'".format(pc_class.lower().capitalize(),
                                                                   strange_friend.lower().capitalize())
    elif pc_class is not None:
        query += "\nWHERE Character = '{}'".format(pc_class.lower().capitalize())
    elif strange_friend is not None:
        query += "\nWHERE Name = '{}'".format(strange_friend.lower().capitalize())

    cursor.execute(query)

    rows = cursor.fetchall()

    strange_friends = []
    for elem in rows:
        strange_friends.append({"name": elem[0], "role": elem[1]})

    if not as_dict:
        for i in range(len(strange_friends)):
            strange_friends[i] = NPC(**strange_friends[i])

    return strange_friends


def query_actions(action: str = None, attribute: str = None) -> List[Tuple[str, str, str]]:
    """
    Retrieves from the DB the information about a specified Action or group of actions.

    :param action: is the Action to search.
    :param attribute: is the group of action to search.
    :return: a list of tuples, containing the name of the Action, its description and its attribute of belonging
            (in this order)
    """

    connection = establish_connection()
    cursor = connection.cursor()

    query = """
    SELECT *
    FROM Action"""

    if action is not None:
        query += "\nWHERE Name = '{}'".format(action)
    elif attribute is not None:
        query += "\nWHERE Attribute = '{}'".format(attribute)

    cursor.execute(query)

    return cursor.fetchall()
