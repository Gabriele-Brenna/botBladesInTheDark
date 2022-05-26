from typing import List, Tuple, Dict, Union, Optional

from character.Action import Action
from character.Attribute import Attribute
from character.Item import Item
from character.NPC import NPC
from character.Vice import Vice
from component.SpecialAbility import SpecialAbility
from controller.DBmanager import *
from organization.Claim import Claim
from organization.Faction import Faction


def query_game_of_user(tel_chat_id: int, user_id: int) -> Optional[int]:
    """
    Gets the game_id given the chat_id and the user_id.

    :param tel_chat_id: id of the telegram chat
    :param user_id: telegram id of the user
    :return: the game_id (None if there are no correspondences in the DB)
    """
    connection = establish_connection()
    cursor = connection.cursor()

    query = """
        SELECT G.Game_ID
        FROM Game G JOIN User_Game UG ON G.Game_ID = UG.Game_ID
        WHERE G.Tel_Chat_ID = {} AND UG.User_ID = {}""".format(tel_chat_id, user_id)

    cursor.execute(query)

    result = cursor.fetchone()
    if result is None:
        return result
    else:
        return result[0]


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
        q_where += "WHERE Name = ?"
        cursor.execute(q_select + q_from + q_where, (special_ability,))

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


def query_sheet_descriptions(sheet: str = None) -> List[str]:
    """
    Retrieves the description of a specified sheet (regardless if character or crew).

    :param sheet: represents the target sheet. If not passed, all the descriptions are retrieved.
    :return: a list of strings containing the sheets descriptions.
    """
    connection = establish_connection()
    cursor = connection.cursor()

    if sheet is not None:
        if exists_crew(sheet):
            query = """SELECT Description
                    FROM CrewSheet
                    WHERE type = ?"""
        elif exists_character(sheet):
            query = """SELECT Description
                         FROM CharacterSheet
                         WHERE class = ?"""
        else:
            return []

        cursor.execute(query, (sheet,))
        rows = cursor.fetchall()
    else:
        cursor.execute("""SELECT Description
                            FROM CharacterSheet""")
        rows = cursor.fetchall()

        cursor.execute("""SELECT Description
                                FROM CrewSheet""")
        rows.extend(cursor.fetchall())

    descriptions = []
    for elem in rows:
        descriptions.append(elem[0])

    return descriptions


def query_crew_sheets(canon: bool = None) -> List[str]:
    """
    Retrieves the list of crew sheets of the specified type.
    If default values are used (None) all the sheets are retrieved

    :param canon: if True the targets are all the canon sheets; if False the targets are all the non-canon sheets
    :return: list of the required sheets
    """
    connection = establish_connection()
    cursor = connection.cursor()

    q_select = "SELECT Type"
    q_from = "\nFROM CrewSheet"
    q_where = "\n"

    if canon is not None:
        q_where += "WHERE canon IS {}".format(canon)

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


def query_games_info(chat_id: int = None, game_id: int = None) -> List[Dict[str, Union[str, int]]]:
    """
    Retrieves the Game_ID, Title and Tel_Chat_ID of all the games stored in the Data Base

    :param chat_id: if this parameter is passed, only the info about the game of the specified chat are retrieved.
    :param game_id: if this parameter is passed, only the info of the specified game are retrieved.
    :return: a list of dictionaries with the keys: "identifier", "title", "chat_id".
        An empty list if no results are found
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

    if tel_chat_id is not None and title is not None:
        cursor.execute("""
        SELECT Game_ID
        FROM Game
        WHERE (Tel_Chat_ID, Title) = (?, ?)""", (tel_chat_id, title))

    elif tel_chat_id is not None:
        cursor.execute("""
                SELECT Game_ID
                FROM Game
                WHERE Tel_Chat_ID = ?""", (tel_chat_id,))
    elif title is not None:
        cursor.execute("""
                       SELECT Game_ID
                       FROM Game
                       WHERE Title = ?""", (title,))
    else:
        cursor.execute("""SELECT Game_ID
                          FROM Game""")

    rows = cursor.fetchall()

    ids = []
    for elem in rows:
        ids.append(elem[0])
    return ids


def query_char_strange_friends(pc_class: str = None, strange_friend: str = None,
                               as_dict: bool = False) -> Union[List[NPC], List[Dict[str, str]]]:
    """
    Retrieves the List of the Strange Friends of the specified sheet.

    :param pc_class: the target pc class.
    :param strange_friend: the target NPC.
    :param as_dict: if True the result objects will be returned as dictionaries.
    :return: a list of NPCs or a list of their dictionary
    """
    connection = establish_connection()
    cursor = connection.cursor()

    query = """
    SELECT Name, Role
    FROM Char_Friend JOIN NPC ON NPC = NpcID"""

    if pc_class is not None and strange_friend is not None:
        query += "\nWHERE Character = ? AND Name = ?"
        cursor.execute(query, (pc_class, strange_friend))
    elif pc_class is not None:
        query += "\nWHERE Character = ?".format(pc_class)
        cursor.execute(query, (pc_class,))
    elif strange_friend is not None:
        query += "\nWHERE Name = ?"
        cursor.execute(query, (strange_friend,))

    rows = cursor.fetchall()

    return result_npcs(rows, as_dict)


def query_crew_contacts(crew_type: str = None, contact: str = None,
                        as_dict: bool = False) -> Union[List[NPC], List[Dict[str, str]]]:
    """
    Retrieves the list of contacts of the specified crew.

    :param crew_type: the target crew.
    :param contact: the target NPC.
    :param as_dict: if True the result objects will be returned as dictionaries.
    :return: a list of NPCs or a list of their dictionary
    """
    connection = establish_connection()
    cursor = connection.cursor()

    query = """
    SELECT Name, Role
    FROM Crew_Contact JOIN NPC ON NPC = NpcID"""

    if crew_type is not None and contact is not None:
        query += "\nWHERE Crew = '{}' AND Name = '{}'".format(crew_type, contact)
    elif crew_type is not None:
        query += "\nWHERE Crew = '{}'".format(crew_type)
    elif contact is not None:
        query += "\nWHERE Name = '{}'".format(contact)

    cursor.execute(query)

    rows = cursor.fetchall()

    return result_npcs(rows, as_dict)


def result_npcs(rows: List[Tuple[str, str]], as_dict: bool) -> Union[List[NPC], List[Dict[str, str]]]:
    """
    Utility method used to return the list of NPCs (or their dict).

    :param rows: the result of the query.
    :param as_dict: if True the result objects will be returned as dictionaries.
    :return: a list of NPCs or a list of their dictionary.
    """
    npcs = []
    for elem in rows:
        npcs.append({"name": elem[0], "role": elem[1]})

    if not as_dict:
        for i in range(len(npcs)):
            npcs[i] = NPC(**npcs[i])

    return npcs


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


def query_upgrade_groups() -> List[str]:
    """
    Retrieves all the distinct "group" from the Upgrade table.

    :return: a list of the groups.
    """
    connection = establish_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT DISTINCT "group"
        FROM Upgrade 
        ORDER BY "group"
        """)

    rows = cursor.fetchall()

    groups = []
    for elem in rows:
        groups.append(elem[0])

    return groups


def query_upgrades(upgrade: str = None, crew_sheet: str = None, group: str = None,
                   common: bool = False, canon: bool = None) -> List[Dict[str, Union[str, int]]]:
    """
    Retrieves the specified upgrade from the database.

    :param upgrade: the target upgrade. If specified the other parameters are ignored
    :param crew_sheet: the target crew. If specified only the specific upgrades of that crew are retrieved
    :param group: the target group of upgrades.
    :param common: if the wanted upgrades are not in the "specific" group.
    :param canon: if the upgrades are canon or not.
    :return: a list of dictionaries containing the keys: "name", "description" and "tot_quality"
    """
    connection = establish_connection()
    cursor = connection.cursor()

    q_select = "SELECT Name, Description, TotQuality"
    q_from = "\nFROM Upgrade"
    q_where = "\n "

    if upgrade is not None:
        q_where += "WHERE name LIKE ?"

        cursor.execute(q_select + q_from + q_where, (upgrade + "%",))

    else:
        if crew_sheet is not None:
            q_from += " JOIN Crew_Upgrade ON name=upgrade"
            q_where += "WHERE crew = ?"

            cursor.execute(q_select + q_from + q_where, (crew_sheet,))

        else:
            if common:
                q_where += """WHERE "group" != "Specific" """
                cursor.execute(q_select + q_from + q_where)
            else:
                if canon is not None and group is not None:
                    q_where += """WHERE "group" = ? AND canon = ? """
                    cursor.execute(q_select + q_from + q_where, (group, canon))

                elif canon is not None:
                    q_where += """WHERE canon = ? """
                    cursor.execute(q_select + q_from + q_where, (canon,))

                elif group is not None:
                    q_where += """WHERE "group" = ? """
                    cursor.execute(q_select + q_from + q_where, (group,))

                else:
                    cursor.execute(q_select + q_from)

    rows = cursor.fetchall()

    upgrades = []
    for elem in rows:
        upgrades.append({"name": elem[0], "description": elem[1], "tot_quality": int(elem[2])})

    return upgrades


def query_starting_upgrades_and_cohorts(crew_sheet: str) -> \
        Tuple[List[Dict[str, Union[str, int]]], List[Dict[str, Union[str, bool]]]]:
    """
    Retrieves the starting upgrades and cohorts of the specified crew.

    :param crew_sheet: the target crew.
    :return: a tuple of two lists: the first one containing dictionaries representing the upgrades ("name", "quality"),
    the second one containing dictionaries representing the upgrades ("type", "expert").
    """
    connection = establish_connection()
    cursor = connection.cursor()

    cursor.execute("""
    SELECT Name, Quality
    FROM Upgrade JOIN Crew_StartingUpgrade ON Name = Upgrade
    WHERE Crew = ? 
    """, (crew_sheet,))

    upgrades = []
    for elem in cursor.fetchall():
        upgrades.append({"name": elem[0], "quality": int(elem[1])})

    cursor.execute("""
        SELECT Type, Expert
        FROM Starting_Cohort
        WHERE Crew = ? 
        """, (crew_sheet,))

    cohorts = []
    for elem in cursor.fetchall():
        cohorts.append({"type": elem[0], "expert": bool(elem[1])})

    return upgrades, cohorts


def query_frame_features(feature: str = None, group: str = None,
                         as_dict: bool = False) -> Union[List[SpecialAbility], List[Dict[str, str]]]:
    """
    Retrieves the name and the description of the specified hull's frame feature
    or all the frame features of a specified group. If neither feature nor group are specified, the complete list of
    frame features is retrieved.

    :param feature: is the target frame feature.
    :param group: is the target group.
    :param as_dict: if True the result objects will be returned as dictionaries.
    :return: a list of SpecialAbility
    """
    connection = establish_connection()
    cursor = connection.cursor()

    if feature is not None:
        query = """
        SELECT Name, Description
        FROM SpecialAbility
        WHERE FrameFeature != 'N' AND Name = ?
        """

        cursor.execute(query, (feature,))
    else:
        if group is not None:
            query = """
            SELECT Name, Description
            FROM SpecialAbility
            WHERE FrameFeature = ?"""

            cursor.execute(query, (group,))
        else:
            query = """
                    SELECT Name, Description
                    FROM SpecialAbility
                    WHERE FrameFeature != 'N'
                    """
            cursor.execute(query)

    rows = cursor.fetchall()

    frame_features = []
    for elem in rows:
        frame_features.append({"name": elem[0], "description": elem[1]})

    if not as_dict:
        for i in range(len(frame_features)):
            frame_features[i] = SpecialAbility(**frame_features[i])

    return frame_features


def query_items(item_name: str = None, common_items: bool = False, pc_class: str = None, canon: bool = None,
                as_dict: bool = False) -> Union[List[Item], List[dict]]:
    """
    Retrieves a list of Items from the DB. If item_name is passed this method searches for its occurrence.
    Otherwise, if pc_class is passed, the targets are all the items of this specific sheet.

    :param item_name: is the target item's name.
    :param common_items: True if only the common items should be retrieved, False otherwise.
    :param pc_class: is the target PC's sheet.
    :param canon: True if the canon items are the target, false if the non-canon items are the target.
    :param as_dict: if True the result objects will be returned as dictionaries.
    :return: a list of Item.
    """
    connection = establish_connection()
    cursor = connection.cursor()

    if item_name is not None:
        query = """
        SELECT Name, Description, Weight, Usages
        FROM Item
        WHERE Name = ?"""
        cursor.execute(query, (item_name,))

    elif common_items:
        query = """
                SELECT Name, Description, Weight, Usages
                FROM Item
                WHERE Canon = True AND Name NOT IN (SELECT Item
                                  FROM Char_Item)"""

        cursor.execute(query)

    else:
        if pc_class is not None and canon is not None:
            query = """SELECT Name, Description, Weight, Usages
                       FROM Item JOIN Char_Item ON Name = Item
                       WHERE Character = ? AND Canon = ?"""
            cursor.execute(query, (pc_class, canon))

        elif pc_class is not None:
            query = """
                    SELECT Name, Description, Weight, Usages
                    FROM Item JOIN Char_Item ON Name = Item
                    WHERE Character = ?"""
            cursor.execute(query, (pc_class,))

        elif canon is not None:
            query = """SELECT Name, Description, Weight, Usages
                       FROM Item
                       WHERE Canon = ?"""
            cursor.execute(query, (canon,))
        else:
            query = """SELECT Name, Description, Weight, Usages
                       FROM Item
                       WHERE Canon = ?"""
            cursor.execute(query)

    rows = cursor.fetchall()

    items = []
    for elem in rows:
        items.append({"name": elem[0], "description": elem[1], "weight": elem[2], "usages": elem[3]})

    if not as_dict:
        for i in range(len(items)):
            items[i] = Item(**items[i])

    return items


def query_hunting_grounds(hunting_ground: str = None, crew_type: str = None, canon: bool = None,
                          only_names: bool = True) -> List[str]:
    """
    Retrieves a list of hunting grounds from The DB. If crew_type is passed this method searches for all the hunting
    grounds of the crew.

    :param hunting_ground: represents the target hunting ground.
    :param crew_type: represents the target crew sheet.
    :param canon: True if the canon hunting grounds are the target,
            false if the non-canon hunting grounds are the target.
    :param only_names: True if only the hunting grounds' names should be returned, False otherwise.
    :return: a list of string composed with name and description of the hunting grounds.
    """
    connection = establish_connection()
    cursor = connection.cursor()

    if hunting_ground is not None:
        query = """
                SELECT Name, Description
                FROM HuntingGround
                WHERE Name = ?"""
        cursor.execute(query, (hunting_ground,))
    else:
        if crew_type is not None and canon is not None:
            query = """
                    SELECT Name, Description
                    FROM HuntingGround JOIN Crew_HG ON Name = HuntingGround
                    WHERE Crew = ? AND Canon = ?"""
            cursor.execute(query, (crew_type, canon))

        elif crew_type is not None:
            query = """
                    SELECT Name, Description
                    FROM HuntingGround JOIN Crew_HG ON Name = HuntingGround
                    WHERE Crew = ?"""
            cursor.execute(query, (crew_type,))

        elif canon is not None:
            query = """
                    SELECT Name, Description
                    FROM HuntingGround
                    WHERE Canon = ?"""
            cursor.execute(query, (canon,))

        else:
            query = """
                    SELECT Name, Description
                    FROM HuntingGround"""
            cursor.execute(query)

    rows = cursor.fetchall()

    hg = []
    for elem in rows:
        if only_names:
            hg.append(elem[0])
        else:
            hg.append(elem[0] + ": " + elem[1])

    return hg


def query_claims(name: str = None, prison: bool = None, canon: bool = None,
                 as_dict: bool = False) -> Union[List[Claim], List[dict]]:
    """
    Retrieves a list of Claim from the DB. If name is passed this method searches for its occurrence.
    Otherwise, if prison is passed, the targets are all the claims of this specific group.

    :param name: is the target claim's name.
    :param prison: True if only the prison claims should be retrieved, False if only the lair claims should be retrieved.
    :param canon: True if the canon claims are the target, false if the non-canon claims are the target.
    :param as_dict: if True the result objects will be returned as dictionaries.
    :return: a list of Claim.
    """
    connection = establish_connection()
    cursor = connection.cursor()

    query = """
            SELECT Name, Description
            FROM Claim \n"""

    if name is not None:
        query += "WHERE Name = ?"
        query += "\nORDER BY Canon DESC"

        cursor.execute(query, (name,))
    else:
        if prison is not None and canon is not None:
            query += "WHERE Prison is ? AND Canon is ?"
            query += "\nORDER BY Canon DESC"

            cursor.execute(query, (prison, canon))
        elif prison is not None:
            query += "WHERE Prison is ?"
            query += "\nORDER BY Canon DESC"

            cursor.execute(query, (prison,))
        elif canon is not None:
            query += "WHERE Canon is ?"
            query += "\nORDER BY Canon DESC"

            cursor.execute(query, (canon,))
        else:
            query += "\nORDER BY Canon DESC"
            cursor.execute(query)

    rows = cursor.fetchall()

    claims = []
    for elem in rows:
        claims.append({"name": elem[0], "description": elem[1]})

    if not as_dict:
        for i in range(len(claims)):
            claims[i] = Claim(**claims[i])

    return claims


def query_traumas(name: str = None, pc_class: str = None) -> List[Tuple[str, str]]:
    """
    Retrieves the traumas from the data base.

    :param name: the name of the trauma to search; if passed this method searches for its occurrence.
    :param pc_class: the name of the class; if passed all the traumas of that class are retrieved.
    :return: a list of tuple containing the traumas' name and description (in this order).
    """
    connection = establish_connection()
    cursor = connection.cursor()

    query = """
                SELECT Name, Description
                FROM Trauma \n"""

    if name is not None:
        query += "WHERE Name = ?"
        cursor.execute(query, (name, ))

    elif pc_class is not None:
        query += "WHERE Class = ?"
        cursor.execute(query, (pc_class,))

    else:
        cursor.execute(query)

    return cursor.fetchall()


def query_factions(name: str = None, category: str = None, tier: int = None, hold: bool = None,
                   as_dict: bool = False) -> Union[List[Faction], List[dict]]:
    """
    Retrieves a list of Faction from the DB. If name is passed this method searches for its occurrence.
    Otherwise, if category is passed, the targets are all the factions of this specific group.

    :param name: is the target faction's name.
    :param category: is the group of the target factions.
    :param tier: is the tier of the target factions
    :param hold: is the hold situation of the target factions.
    :param as_dict: if True the result objects will be returned as dictionaries.
    :return: a list of Claim.
    """
    connection = establish_connection()
    cursor = connection.cursor()

    query = """
            SELECT Name, Description, Tier, Hold
            FROM Faction \n"""

    if name is not None:
        query += "WHERE Name = ?"

        cursor.execute(query, (name,))
    else:
        if category is not None and tier is not None and hold is not None:
            query += "WHERE Category = ? AND Tier = ? AND hold is ?"

            cursor.execute(query, (category, tier, hold))
        elif category is not None and tier is not None:
            query += "WHERE Category = ? AND Tier = ?"

            cursor.execute(query, (category, tier))
        elif tier is not None and hold is not None:
            query += "WHERE Tier = ? AND hold is ?"

            cursor.execute(query, (tier, hold))
        elif category is not None and hold is not None:
            query += "WHERE Category = ? AND hold is ?"

            cursor.execute(query, (category, hold))
        elif category is not None:
            query += "WHERE Category = ?"

            cursor.execute(query, (category,))
        elif tier is not None:
            query += "WHERE Tier = ?"

            cursor.execute(query, (tier,))
        elif hold is not None:
            query += "WHERE Hold is ?"

            cursor.execute(query, (hold,))
        else:
            cursor.execute(query)

    rows = cursor.fetchall()

    factions = []
    for elem in rows:
        factions.append({"name": elem[0], "description": elem[1], "tier": elem[2], "hold": elem[3]})

    if not as_dict:
        for i in range(len(factions)):
            factions[i].pop("description")
            factions[i] = Faction(**factions[i])

    return factions


def query_npcs(npc_id: int = None, name: str = None, role: str = None, faction: str = None, canon: bool = None,
               as_dict: bool = False) -> Union[List[NPC], List[dict]]:
    """
    Retrieves a list of NPC from the DB. If npc_id is passed this method searches for its occurrence, else
    all the other parameters are used to found the matching NPCs.
    The NPC's attribute faction is passed as string and not as a Faction object.

    :param npc_id: represents the id of the NPC.
    :param name: represents the name of the NPC.
    :param role: represents the role of the NPC.
    :param faction: represents the faction of the NPC.
    :param canon: True if the target NPCs are canon, False if not-canon.
    :param as_dict: if True the result objects will be returned as dictionaries.
    :return: a list of NPC or a list of Dictionaries
    """
    connection = establish_connection()
    cursor = connection.cursor()

    query = """
                SELECT Name, Role, Faction, Description
                FROM NPC \n"""

    if npc_id is not None:
        query += "WHERE NpcID = ?"

        cursor.execute(query, (npc_id,))
    elif name is not None and role is not None and faction is not None and canon is not None:
        query += "WHERE Name = ? AND Role = ? AND Faction = ? AND Canon is ?"

        cursor.execute(query, (name, role, faction, canon))
    elif name is not None and role is not None and faction is not None:
        query += "WHERE Name = ? AND Role = ? AND Faction = ?"

        cursor.execute(query, (name, role, faction))
    elif name is not None and role is not None and canon is not None:
        query += "WHERE Name = ? AND Role = ? AND Canon is ?"

        cursor.execute(query, (name, role, canon))
    elif name is not None and faction is not None and canon is not None:
        query += "WHERE Name = ? AND Faction = ? AND Canon is ?"

        cursor.execute(query, (name, faction, canon))
    elif name is not None and role is not None and canon is not None:
        query += "WHERE Name = ? AND Role = ? AND Canon is ?"

        cursor.execute(query, (name, role, canon))
    elif name is not None and role is not None:
        query += "WHERE Name = ? AND Role = ?"

        cursor.execute(query, (name, role))
    elif name is not None and faction is not None:
        query += "WHERE Name = ? AND Faction = ?"

        cursor.execute(query, (name, faction))
    elif name is not None and canon is not None:
        query += "WHERE Name = ? AND Canon = ?"

        cursor.execute(query, (name, canon))
    elif role is not None and faction is not None:
        query += "WHERE Role = ? AND Faction = ?"

        cursor.execute(query, (role, faction))
    elif role is not None and canon is not None:
        query += "WHERE Role = ? AND Canon is ?"

        cursor.execute(query, (role, canon))
    elif faction is not None and canon is not None:
        query += "WHERE Faction = ? AND Canon is ?"

        cursor.execute(query, (faction, canon))
    elif name is not None:
        query += "WHERE Name = ?"

        cursor.execute(query, (name, ))
    elif role is not None:
        query += "WHERE Role = ?"

        cursor.execute(query, (role, ))
    elif faction is not None:
        query += "WHERE Faction = ?"

        cursor.execute(query, (faction, ))
    elif canon is not None:
        query += "WHERE Canon is ?"

        cursor.execute(query, (canon, ))
    else:
        cursor.execute(query)

    rows = cursor.fetchall()

    npcs = []
    for elem in rows:
        npcs.append({"name": elem[0], "role": elem[1], "faction": elem[2], "description": elem[3]})

    if not as_dict:
        for i in range(len(npcs)):
            npcs[i] = NPC(**npcs[i])

    return npcs
