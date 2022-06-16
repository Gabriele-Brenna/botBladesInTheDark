from sqlite3 import DatabaseError

from controller.DBmanager import *


def insert_game(game_id: int, game_title: str, tel_chat_id: int) -> bool:
    """
    Insert a new game in the Game table in the BladesInTheDark Database.

    :param game_id: int representing the identifier of the game
    :param game_title: string representing the title of the game
    :param tel_chat_id: int representing the id of the telegram chat
    :return: True if the new game is added in the table, False otherwise
    """
    if isinstance(game_id, int) and isinstance(game_title, str) and isinstance(tel_chat_id, int):

        connection = establish_connection()
        cursor = connection.cursor()

        try:
            cursor.execute("""
            INSERT INTO Game (Game_ID, Title, Tel_Chat_ID)
            VALUES (?, ?, ?)
            """, (game_id, game_title, tel_chat_id))

            connection.commit()
        except DatabaseError:
            traceback.print_exc()
            return False
        return True
    return False


def insert_crew_json(game_id: int, crew_json: str) -> bool:
    """
    Insert json string in Crew_JSON attribute in Game table in BladesInTheDark Database

    :param game_id: int representing the identifier of the game
    :param crew_json: string representing json string
    :return: True if the json string is added, False otherwise
    """
    if isinstance(game_id, int) and is_json(crew_json):

        connection = establish_connection()
        cursor = connection.cursor()

        try:

            if not exists_game(game_id):
                raise DatabaseError("Wrong game selected")

            cursor.execute("""
            UPDATE Game
            SET Crew_JSON = ?
            WHERE Game_ID = ?
            """, (crew_json, game_id))

            connection.commit()
        except DatabaseError:
            traceback.print_exc()
            return False
        return True
    return False


def insert_crafted_item_json(game_id: int, crafted_item_json: str) -> bool:
    """
    Insert json string in Crafted_Item_JSON attribute in Game table in BladesInTheDark Database
    
    :param game_id: int representing the identifier of the game
    :param crafted_item_json: string representing json string
    :return: True if the json string is added, False otherwise
    """
    if isinstance(game_id, int) and is_json(crafted_item_json):

        connection = establish_connection()
        cursor = connection.cursor()

        try:

            if not exists_game(game_id):
                raise DatabaseError("Wrong game selected")

            cursor.execute("""
            UPDATE Game
            SET Crafted_Item_JSON = ?
            WHERE Game_ID = ?
            """, (crafted_item_json, game_id))

            connection.commit()
        except DatabaseError:
            traceback.print_exc()
            return False
        return True
    return False


def insert_npc_json(game_id: int, npc_json: str) -> bool:
    """
    Insert json string in NPC_JSON attribute in Game table in BladesInTheDark Database
    
    :param game_id: int representing the identifier of the game
    :param npc_json: string representing json string
    :return: True if the json string is added, False otherwise
    """
    if isinstance(game_id, int) and is_json(npc_json):

        connection = establish_connection()
        cursor = connection.cursor()

        try:

            if not exists_game(game_id):
                raise DatabaseError("Wrong game selected")

            cursor.execute("""
            UPDATE Game
            SET NPC_JSON = ?
            WHERE Game_ID = ?
            """, (npc_json, game_id))

            connection.commit()
        except DatabaseError:
            traceback.print_exc()
            return False
        return True
    return False


def insert_faction_json(game_id: int, faction_json: str) -> bool:
    """
    Insert json string in Faction_JSON attribute in Game table in BladesInTheDark Database.

    :param game_id: int representing the identifier of the game
    :param faction_json: string representing json string
    :return: True if the json string is added, False otherwise
    """
    if isinstance(game_id, int) and is_json(faction_json):

        connection = establish_connection()
        cursor = connection.cursor()

        try:

            if not exists_game(game_id):
                raise DatabaseError("Wrong game selected")

            cursor.execute("""
            UPDATE Game
            SET Faction_JSON = ?
            WHERE Game_ID = ?
            """, (faction_json, game_id))

            connection.commit()
        except DatabaseError:
            traceback.print_exc()
            return False
        return True
    return False


def insert_score_json(game_id: int, score_json: str) -> bool:
    """
    Insert json string in Score_JSON attribute in Game table in BladesInTheDark Database.

    :param game_id: int representing the identifier of the game
    :param score_json: string representing json string
    :return: True if the json string is added, False otherwise
    """
    if isinstance(game_id, int) and is_json(score_json):

        connection = establish_connection()
        cursor = connection.cursor()
        try:

            if not exists_game(game_id):
                raise DatabaseError("Wrong game selected")

            cursor.execute("""
            UPDATE Game
            SET Score_JSON = ?
            WHERE Game_ID = ?
            """, (score_json, game_id))

            connection.commit()
        except DatabaseError:
            traceback.print_exc()
            return False
        return True
    return False


def insert_clock_json(game_id: int, clock_json: str) -> bool:
    """
    Insert json string in Clock_JSON attribute in Game table in BladesInTheDark Database.

    :param game_id: int representing the identifier of the game
    :param clock_json: string representing json string
    :return: True if the json string is added, False otherwise
    """
    if isinstance(game_id, int) and is_json(clock_json):

        connection = establish_connection()
        cursor = connection.cursor()

        try:

            if not exists_game(game_id):
                raise DatabaseError("Wrong game selected")

            cursor.execute("""
            UPDATE Game
            SET Clock_JSON = ?
            WHERE Game_ID = ?
            """, (clock_json, game_id))

            connection.commit()
        except DatabaseError:
            traceback.print_exc()
            return False
        return True
    return False


def insert_journal(game_id: int, journal: str) -> bool:
    """
    Insert the journal inside Game table in BladesInTheDark Database.

    :param game_id: int representing the identifier of the game
    :param journal: string representing the journal
    :return: True if the journal has been added, False otherwise
    """
    if isinstance(game_id, int) and isinstance(journal, str):

        connection = establish_connection()
        cursor = connection.cursor()

        try:

            if not exists_game(game_id):
                raise DatabaseError("Wrong game selected")

            cursor.execute("""
            UPDATE Game
            SET Journal = ?
            WHERE Game_ID = ?
            """, (journal, game_id))

            connection.commit()
        except DatabaseError:
            traceback.print_exc()
            return False
        return True
    return False


def insert_state(game_id: int, state: int) -> bool:
    """
    Insert the current state inside Game table in BladesInTheDark Database.

    :param game_id: int representing the identifier of the game
    :param state: int representing the current state
    :return: True if the state has been added, False otherwise
    """
    if isinstance(game_id, int) and isinstance(state, int):

        connection = establish_connection()
        cursor = connection.cursor()

        try:

            if not exists_game(game_id):
                raise DatabaseError("Wrong game selected")

            cursor.execute("""
            UPDATE Game
            SET State = ?
            WHERE Game_ID = ?""", (state, game_id))

            connection.commit()

        except DatabaseError:
            traceback.print_exc()
            return False
        return True
    return False


def insert_lang(game_id: int, lang: str = "ENG.json") -> bool:
    """
    Insert the preferred language for the game.

    :param game_id: int representing the identifier of the game
    :param lang: str representing the language
    :return: True if the language has been added, False otherwise
    """
    if isinstance(game_id, int) and isinstance(lang, str):

        connection = establish_connection()
        cursor = connection.cursor()

        try:

            if not exists_game(game_id):
                raise DatabaseError("Wrong game selected")

            cursor.execute("""
            UPDATE Game
            SET Language = ?
            WHERE Game_ID = ?
            """, (lang, game_id))

            connection.commit()

        except DatabaseError:
            traceback.print_exc()
            return False
        return True
    return False


def insert_user(user_id: int, name: str) -> bool:
    """
    Insert a new user in the User table in the BladesInTheDark Database.

    :param user_id: int representing the id of the player
    :param name: string representing the name of the player
    :return: True if the new user has been added, False otherwise
    """
    if isinstance(user_id, int) and isinstance(name, str):

        connection = establish_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("""
            INSERT INTO User
            VALUES (?, ?)
            ON CONFLICT (Tel_ID)
            DO UPDATE SET name = ?
            """, (user_id, name, name))

            connection.commit()
        except DatabaseError:
            traceback.print_exc()
            return False
        return True
    return False


def insert_user_game(user_id: int, game_id: int, char_json: str = None, master: bool = False) -> bool:
    """
    Insert a new row in User_Game table in BladesInTheDark Database.

    :param user_id: int representing the id of the player
    :param game_id: int representing the id of the game
    :param char_json: string representing json string
    :param master: bool representing if the player is master or not
    :return: True if the row has been added, False otherwise
    """
    if isinstance(user_id, int) and isinstance(game_id, int) and (char_json is None or is_json(char_json)) \
            and isinstance(master, int) and (master == 0 or master == 1):
        connection = establish_connection()
        cursor = connection.cursor()

        try:
            cursor.execute("""
                        INSERT INTO User_Game
                        VALUES (?, ?, ?, ?)
                        ON CONFLICT (User_ID, Game_ID) DO 
                        UPDATE SET (Char_JSON, Master) = (?, ?)""",
                           (user_id, game_id, char_json, master, char_json, master))

            connection.commit()
        except DatabaseError:
            traceback.print_exc()
            return False
        return True
    return False


def update_user_characters(user_id: int, game_id: int, char_json: str = None) -> bool:
    """
    Updates the Char_JSON of the specified user in the specified game in User_Game table in DB.

    :param user_id: int representing the id of the player.
    :param game_id: int representing the id of the game.
    :param char_json: string containing the user's PCs.
    :return: True if the update is successful, false otherwise.
    """
    if isinstance(user_id, int) and isinstance(game_id, int) and (char_json is None or is_json(char_json)):
        connection = establish_connection()
        cursor = connection.cursor()

        try:
            cursor.execute("""
            UPDATE User_Game
            SET Char_JSON = ?
            WHERE User_ID = ? AND Game_ID = ?""", (char_json, user_id, game_id))

            connection.commit()
        except DatabaseError:
            traceback.print_exc()
            return False
        return True
    return False


def insert_character_sheet(char_class: str, description: str, connection: Connection) -> bool:
    """
    Insert a new character class in CharacterSheet table in BladesInTheDark Database.

    :param char_class: class of the character
    :param description: description of the class
    :param connection: connection used to execute the query
    :return: True if the new class is added, False otherwise
    """
    if isinstance(char_class, str) and isinstance(description, str):
        cursor = connection.cursor()

        try:
            cursor.execute("""
            INSERT INTO CharacterSheet (Class, Description)
            VALUES (?, ?)""", (char_class, description))

        except DatabaseError:
            traceback.print_exc()
            raise DatabaseError
        return True
    return False


def insert_claim(name: str, description: str, prison: bool) -> bool:
    """
    Insert a new claim in Claim table in BladesInTheDark Database.

    :param name: name of the claim
    :param description: description of the claim
    :param prison: if the claim is a prison claim or not
    :return: True if the claim is added, False otherwise
    """
    if isinstance(name, str) and isinstance(description, str) and isinstance(prison, int) \
            and (prison == 0 or prison == 1):
        connection = establish_connection()
        cursor = connection.cursor()

        try:
            cursor.execute("""
            INSERT INTO Claim (Name, Description, Prison)
            VALUES (?, ?, ?)""", (name, description, prison))

            connection.commit()

        except DatabaseError:
            traceback.print_exc()
            return False
        return True
    return False


def insert_crew_sheet(crew_type: str, description: str, connection: Connection) -> bool:
    """
    Insert a new crew type in CrewSheet table in BladesInTheDark Database.

    :param crew_type: type of the crew
    :param description: description of the crew
    :param connection: connection used to execute the query
    :return: True if the crew type is added, False otherwise
    """
    if isinstance(crew_type, str) and isinstance(description, str):
        cursor = connection.cursor()

        try:
            cursor.execute("""
            INSERT INTO CrewSheet (Type, Description)
            VALUES (?, ?)""", (crew_type, description))

        except DatabaseError:
            traceback.print_exc()
            raise DatabaseError
        return True
    return False


def insert_hunting_ground(name: str, description: str) -> bool:
    """
    Insert a new hunting ground in HuntingGround table in BladesInTheDark Database.

    :param name: name of the hunting ground
    :param description: description of the hunting ground
    :return: True if the hunting ground is added, False otherwise
    """
    if isinstance(name, str) and isinstance(description, str):
        connection = establish_connection()
        cursor = connection.cursor()

        try:
            cursor.execute("""
            INSERT INTO HuntingGround (Name, Description)
            VALUES (?, ?)""", (name, description))

            connection.commit()

        except DatabaseError:
            traceback.print_exc()
            return False
        return True
    return False


def insert_item(name: str, description: str, weight: int, usages: int):
    """
    Insert a new item in Item table in BladesInTheDark Database.

    :param name: name of the item
    :param description: description of the item
    :param weight: weight of the item
    :param usages: usages of the item
    :return: True if the item is added, False otherwise
    """
    if isinstance(name, str) and isinstance(description, str) and isinstance(weight, int) and isinstance(usages, int):
        connection = establish_connection()
        cursor = connection.cursor()

        try:
            cursor.execute("""
            INSERT INTO Item (Name, Description, Weight, Usages)
            VALUES (?, ?, ?, ?)""", (name, description, weight, usages))

            connection.commit()

        except DatabaseError:
            traceback.print_exc()
            return False
        return True
    return False


def insert_npc(name: str, role: str, faction: str, description: str) -> bool:
    """
    Insert a new npc in NPC table in BladesInTheDark Database.

    :param name: name of the npc
    :param role: role of the npc
    :param faction: faction of the npc
    :param description: description of the npc
    :return: True if the npc is added, False otherwise
    """
    if isinstance(name, str) and isinstance(role, str) and isinstance(faction, str) and isinstance(description, str):
        connection = establish_connection()
        cursor = connection.cursor()

        try:
            cursor.execute("""
            INSERT INTO NPC (Name, Role, Faction, Description)
            VALUES (?, ?, ?, ?)""", (name, role, faction, description))

            connection.commit()

        except DatabaseError:
            traceback.print_exc()
            return False
        return True
    return False


def insert_special_ability(name: str, description: str) -> bool:
    """
    Insert a new special ability in SpecialAbility table in BladesInTheDark Database.

    :param name: name of the special ability
    :param description: description of the special ability
    :return: True if the special ability is added, False otherwise
    """
    if isinstance(name, str) and isinstance(description, str):
        connection = establish_connection()
        cursor = connection.cursor()

        try:
            cursor.execute("""
            INSERT INTO SpecialAbility (Name, Description)
            VALUES (?, ?)""", (name, description))

            connection.commit()
        except DatabaseError:
            traceback.print_exc()
            return False
        return True
    return False


def insert_upgrade(name: str, quality: int, description: str) -> bool:
    """
    Insert a new upgrade in Upgrade table in BladesInTheDark Database.

    :param name: name of the upgrade
    :param quality: quality of the upgrade
    :param description: description of the upgrade
    :return: True if the upgrade is added, False otherwise
    """
    if isinstance(name, str) and isinstance(quality, int) and isinstance(description, str):
        connection = establish_connection()
        cursor = connection.cursor()

        try:
            cursor.execute("""
            INSERT INTO Upgrade (Name, TotQuality, Description)
            VALUES (?, ?, ?)""", (name, quality, description))

            connection.commit()
        except DatabaseError:
            traceback.print_exc()
            return False
        return True
    return False


def insert_xp_trigger(description: str, crew_char: bool) -> bool:
    """
    Insert a new xp trigger in XpTrigger table in BladesInTheDark Database.

    :param description: description of the xp trigger
    :param crew_char: True if it's a crew upgrade, False otherwise
    :return: True if the xp trigger is added, False otherwise
    """
    if isinstance(description, str) and isinstance(crew_char, int) and (crew_char == 0 or crew_char == 1):
        connection = establish_connection()
        cursor = connection.cursor()

        try:
            cursor.execute("""
            INSERT INTO XpTrigger (Description, Crew_Char)
            VALUES (?, ?)""", (description, crew_char))

            connection.commit()
        except DatabaseError:
            traceback.print_exc()
            return False
        return True
    return False


def insert_simple_relation(table: str, first_column, second_column, commit: bool = True,
                           connection: Connection = None) -> bool:
    """
    Insert a simple relation between two other tables a given table in BladesInTheDark Database.

    :param table: table to write the relation in
    :param first_column: value of the first table
    :param second_column: value of the second table
    :param commit: True if the method has to commit the insertion, False otherwise.
    :param connection: if commit is False it will be the connection used to commit the change
    :return: True if the simple relation is added, raise a DataBase error if it's not added.
    """
    if connection is None:
        connection = establish_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
        INSERT INTO {}
        VALUES (?,?)""".format(table), (first_column, second_column))
        if commit:
            connection.commit()
    except DatabaseError:
        traceback.print_exc()
        raise DatabaseError
    return True


def insert_complex_relation(table: str, first_column, second_column, third_column, commit: bool = True,
                            connection: Connection = None) -> bool:
    """
    Insert a relation with a third attribute between two other tables a given table in BladesInTheDark Database.

    :param table: table to write the relation in
    :param first_column: value of the first table
    :param second_column: value of the second table
    :param third_column: extra information for the relation
    :param commit: True if the method has to commit the insertion, False otherwise.
    :param connection: if commit is False it will be the connection used to commit the change
    :return: True if the peculiar relation is added, raise a DataBase error if it's not added.
    """
    if connection is None:
        connection = establish_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO {}
            VALUES (?,?,?)""".format(table), (first_column, second_column, third_column))

        if commit:
            connection.commit()
    except DatabaseError:
        traceback.print_exc()
        raise DatabaseError
    return True


def insert_char_action(character: str, action: str, dots: int, connection: Connection) -> bool:
    """
    Insert a new relation in Char_Action table in BladesInTheDark Database.

    :param character: class of the character
    :param action: name of the action
    :param dots: level of the action
    :param connection: connection used to commit the insertion in the database
    :return: True if the relation is added, False otherwise
    """
    if isinstance(character, str) and isinstance(action, str) and isinstance(dots, int):
        return insert_complex_relation("Char_Action", character, action, dots, False, connection)
    return False


def insert_char_friend(character: str, NPC: int, connection: Connection) -> bool:
    """
    Insert a new relation in Char_Friend table in BladesInTheDark Database.

    :param character: class of the character
    :param NPC: id of the NPC
    :param connection: connection used to commit the insertion in the database
    :return: True if the relation is added, False otherwise
    """
    if isinstance(character, str) and isinstance(NPC, int):
        return insert_simple_relation("Char_Friend", character, NPC, False, connection)
    return False


def insert_char_item(character: str, item: str, connection: Connection) -> bool:
    """
    Insert a new relation in Char_Item table in BladesInTheDark Database.

    :param character: class of the character
    :param item: name of the item
    :param connection: connection used to commit the insertion in the database
    :return: True if the relation is added, False otherwise
    """
    if isinstance(character, str) and isinstance(item, str):
        return insert_simple_relation("Char_Item", character, item, False, connection)
    return False


def insert_char_sa(character: str, sa: str, connection: Connection, peculiar: bool = False) -> bool:
    """
    Insert a new relation in Char_SA table in BladesInTheDark Database.

    :param character: class of the character
    :param sa: name of the special ability
    :param peculiar: if the ability is peculiar or not
    :param connection: connection used to commit the insertion in the database
    :return: True if the relation is added, False otherwise
    """
    if isinstance(character, str) and isinstance(sa, str):
        return insert_complex_relation("Char_SA", character, sa, peculiar, False, connection)
    return False


def insert_char_xp(character: str, xp_id: int, peculiar: bool, connection: Connection) -> bool:
    """
    Insert a new relation in Char_Xp table in BladesInTheDark Database.

    :param character: class of the character
    :param xp_id: id of the xp trigger
    :param peculiar: True if the xp trigger is peculiar of the character class, False otherwise
    :param connection: connection used to commit the insertion in the database
    :return: True if the relation is added, False otherwise
    """
    if isinstance(character, str) and isinstance(xp_id, int) and isinstance(peculiar, int) \
            and (peculiar == 0 or peculiar == 1):
        return insert_complex_relation("Char_Xp", character, xp_id, peculiar, False, connection)
    return False


def insert_crew_contact(crew: str, contact: int, connection: Connection) -> bool:
    """
    Insert a new relation in Crew_Contact table in BladesInTheDark Database.

    :param crew: type of the crew
    :param contact: id of the NPC
    :param connection: connection used to commit the insertion in the database
    :return: True if the relation is added, False otherwise
    """
    if isinstance(crew, str) and isinstance(contact, int):
        return insert_simple_relation("Crew_Contact", crew, contact, False, connection)
    return False


def insert_crew_hg(hg: str, crew: str, connection: Connection) -> bool:
    """
    Insert a new relation in Crew_HG table in BladesInTheDark Database.

    :param hg: name of the hunting ground
    :param crew: type of the crew
    :param connection: connection used to commit the insertion in the database
    :return: True if the relation is added, False otherwise
    """
    if isinstance(hg, str) and isinstance(crew, str):
        return insert_simple_relation("Crew_HG", hg, crew, False, connection)
    return False


def insert_crew_sa(crew: str, sa: str, peculiar: bool, connection: Connection) -> bool:
    """
    Insert a new relation in Crew_SA table in BladesInTheDark Database.

    :param crew: type of the crew
    :param sa: name of the special ability
    :param peculiar: True if the special ability is peculiar of the crew type, False otherwise
    :param connection: connection used to commit the insertion in the database
    :return: True if the relation is added, False otherwise
    """
    if isinstance(crew, str) and isinstance(sa, str) and isinstance(peculiar, int) \
            and (peculiar == 0 or peculiar == 1):
        return insert_complex_relation("Crew_SA", crew, sa, peculiar, False, connection)
    return False


def insert_crew_starting_upgrade(crew: str, upgrade: str, quality: int, connection: Connection) -> bool:
    """
    Insert a new relation in Crew_StartingUpgrade table in BladesInTheDark Database.

    :param crew: type of the crew
    :param upgrade: name of the starting upgrade
    :param quality: quality of the starting upgrade
    :param connection: connection used to commit the insertion in the database
    :return: True if the relation is added, False otherwise
    """
    if isinstance(crew, str) and isinstance(upgrade, str) and isinstance(quality, int):
        return insert_complex_relation("Crew_StartingUpgrade", crew, upgrade, quality, False, connection)
    return False


def insert_crew_upgrade(crew: str, upgrade: str, connection: Connection) -> bool:
    """
    Insert a new relation in Crew_Upgrade table in BladesInTheDark Database.

    :param crew: type of the crew
    :param upgrade: name of the upgrade
    :param connection: connection used to commit the insertion in the database
    :return: True if the relation is added, False otherwise
    """
    if isinstance(crew, str) and isinstance(upgrade, str):
        return insert_simple_relation("Crew_Upgrade", crew, upgrade, False, connection)
    return False


def insert_crew_xp(crew: str, xp_id: int, peculiar: bool, connection: Connection) -> bool:
    """
    Insert a new relation in Crew_Xp table in BladesInTheDark Database.

    :param crew: type of the crew
    :param xp_id: id of the xp trigger
    :param peculiar: True if the xp trigger is peculiar of the crew type, False otherwise
    :param connection: connection used to commit the insertion in the database
    :return: True if the relation is added, False otherwise
    """
    if isinstance(crew, str) and isinstance(xp_id, int) and isinstance(peculiar, int) \
            and (peculiar == 0 or peculiar == 1):
        return insert_complex_relation("Crew_Xp", crew, xp_id, peculiar, False, connection)
    return False


def insert_starting_cohort(crew: str, gang_exp: bool, cohort_type: str, connection: Connection) -> bool:
    """
    Insert a new relation in Starting_Cohort table in BladesInTheDark Database.

    :param crew: type of the crew
    :param gang_exp: True if the cohort is a gang, False if it's an expert
    :param cohort_type: type of the cohort
    :param connection: connection used to commit the insertion in the database
    :return: True if the relation is added, False otherwise
    """
    if isinstance(crew, str) and isinstance(gang_exp, int) and (gang_exp == 0 or gang_exp == 1) \
            and isinstance(cohort_type, str):
        return insert_complex_relation("Starting_Cohort", crew, gang_exp, cohort_type, False, connection)
    return False


def insert_char_info(info: dict) -> bool:
    """
    Method used to insert all the information needed to have a new playable character class.

    :param info: dictionary containing all the information needed to add the class
    :return: True if character has been added properly, False otherwise
    """
    connection = establish_connection()
    sheet_name = info["name"]
    try:
        insert_character_sheet(sheet_name, **info["CharacterSheet"], connection=connection)
        for key in info["Char_Action"]["action_dots"].keys():
            insert_char_action(sheet_name, key, info["Char_Action"]["action_dots"][key], connection)
        for npc in info["Char_Friend"]["NPCs"]:
            insert_char_friend(sheet_name, npc, connection)
        for item in info["Char_Item"]["items"]:
            insert_char_item(sheet_name, item, connection)
        insert_char_sa(sheet_name, info["Char_Sa"]["sas"][0], connection, True)
        info["Char_Sa"]["sas"].pop(0)
        for special_ability in info["Char_Sa"]["sas"]:
            insert_char_sa(sheet_name, special_ability, connection)
        for i in range(1, 4):
            insert_char_xp(sheet_name, i, False, connection)
        insert_char_xp(sheet_name, info["Char_Xp"]["xp_id"], True, connection)
    except:
        traceback.print_exc()
        return False
    connection.commit()
    return True


def insert_crew_info(info: dict) -> bool:
    """
        Method used to insert all the information needed to have a new playable crew class.

        :param info: dictionary containing all the information needed to add the class
        :return: True if crew has been added properly, False otherwise
        """
    connection = establish_connection()
    sheet_name = info["crew_type"]
    try:
        insert_crew_sheet(sheet_name, **info["CrewSheet"], connection=connection)
        for npc in info["Crew_Contact"]["contacts"]:
            insert_crew_contact(sheet_name, npc, connection)
        for upgrade in info["Crew_Upgrade"]["upgrades"]:
            insert_crew_upgrade(sheet_name, upgrade, connection)
        for upgrade in info["Crew_StartingUpgrade"]["upgrades"]:
            insert_crew_starting_upgrade(sheet_name, upgrade[0], upgrade[1], connection)
        for hg in info["Crew_Hg"]["hgs"]:
            insert_crew_hg(hg, sheet_name, connection)
        insert_crew_sa(sheet_name, info["Crew_Sa"]["sas"][0], True, connection)
        info["Crew_Sa"]["sas"].pop(0)
        for special_ability in info["Crew_Sa"]["sas"]:
            insert_crew_sa(sheet_name, special_ability, False, connection)
        for i in range(16, 19):
            insert_crew_xp(sheet_name, i, False, connection)
        insert_crew_xp(sheet_name, info["Crew_Xp"]["xp_id"], True, connection)
    except:
        traceback.print_exc()
        return False
    connection.commit()
    return True


def delete_user_game(user_id: int, game_id: int) -> bool:
    """
    Removes the specified occurrence in the User_Game table from the Data Base

    :param user_id: telegram id of the user.
    :param game_id: identifier of the game.
    :return: True if the operation is successful, False otherwise
    """
    if isinstance(user_id, int) and isinstance(game_id, int):
        connection = establish_connection()
        cursor = connection.cursor()

        try:
            cursor.execute("""
            DELETE FROM User_Game WHERE (User_ID, Game_ID) = (?, ?)
            """, (user_id, game_id))

            connection.commit()
        except DatabaseError:
            traceback.print_exc()
            return False
        return True
    return False


def delete_game(game_id: int) -> bool:
    """
    Deletes the selected game from the database

    :param game_id: the id of the game to delete.
    :return: True if the operation is successful, False otherwise
    """
    connection = establish_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
        DELETE FROM Game WHERE Game_ID == ?""", (game_id,))

        connection.commit()
    except DatabaseError:
        traceback.print_exc()
        return False
    return True
