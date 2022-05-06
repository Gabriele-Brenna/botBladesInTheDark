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
            VALUES ({}, '{}', {})
            """.format(game_id, game_title, tel_chat_id))

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
            SET Crew_JSON = '{}'
            WHERE Game_ID = {}
            """.format(crew_json, game_id))

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
            SET Crafted_Item_JSON = '{}'
            WHERE Game_ID = {}
            """.format(crafted_item_json, game_id))

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
            SET NPC_JSON = '{}'
            WHERE Game_ID = {}
            """.format(npc_json, game_id))

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
            SET Faction_JSON = '{}'
            WHERE Game_ID = {}
            """.format(faction_json, game_id))

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
            SET Score_JSON = '{}'
            WHERE Game_ID = {}
            """.format(score_json, game_id))

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
            SET Clock_JSON = '{}'
            WHERE Game_ID = {}
            """.format(clock_json, game_id))

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
            SET Journal = '{}'
            WHERE Game_ID = {}
            """.format(journal, game_id))

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
    :return: True if the journal has been added, False otherwise
    """
    if isinstance(game_id, int) and isinstance(state, int):

        connection = establish_connection()
        cursor = connection.cursor()

        try:

            if not exists_game(game_id):
                raise DatabaseError("Wrong game selected")

            cursor.execute("""
            UPDATE Game
            SET State = {}
            WHERE Game_ID = {}""".format(state, game_id))

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
            DO UPDATE SET name = '{}'
            """.format(name), (user_id, name))

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
            and isinstance(master, bool):
        connection = establish_connection()
        cursor = connection.cursor()

        try:
            cursor.execute("""
                        INSERT INTO User_Game
                        VALUES ({}, {}, '{}', {})
                        ON CONFLICT (User_ID, Game_ID) DO 
                        UPDATE SET (Char_JSON, Master) = (?, ?)""".format(user_id, game_id, char_json, master,),
                           (char_json, master))

            connection.commit()
        except DatabaseError:
            traceback.print_exc()
            return False
        return True
    return False


def insert_character_sheet(char_class: str, description: str) -> bool:
    """
    Insert a new character class in CharacterSheet table in BladesInTheDark Database.

    :param char_class: class of the character
    :param description: description of the class
    :return: True if the new class is added, False otherwise
    """
    if isinstance(char_class, str) and isinstance(description, str):
        connection = establish_connection()
        cursor = connection.cursor()

        try:
            cursor.execute("""
            INSERT INTO CharacterSheet (Class, Description)
            VALUES ('{}', '{}')""".format(char_class, description))

            connection.commit()
        except DatabaseError:
            traceback.print_exc()
            return False
        return True
    return True


def insert_claim(name: str, description: str, prison: bool) -> bool:
    """
    Insert a new claim in Claim table in BladesInTheDark Database.

    :param name: name of the claim
    :param description: description of the claim
    :param prison: if the claim is a prison claim or not
    :return: True if the claim is added, False otherwise
    """
    if isinstance(name, str) and isinstance(description, str) and isinstance(prison, bool):
        connection = establish_connection()
        cursor = connection.cursor()

        try:
            cursor.execute("""
            INSERT INTO Claim (Name, Description, Prison)
            VALUES ('{}', '{}', {})""".format(name, description, prison))

            connection.commit()

        except DatabaseError:
            traceback.print_exc()
            return False
        return True
    return False


def insert_crew_sheet(crew_type: str, description: str) -> bool:
    """
    Insert a new crew type in CrewSheet table in BladesInTheDark Database.

    :param crew_type: type of the crew
    :param description: description of the crew
    :return: True if the crew type is added, False otherwise
    """
    if isinstance(crew_type, str) and isinstance(description, str):
        connection = establish_connection()
        cursor = connection.cursor()

        try:
            cursor.execute("""
            INSERT INTO CrewSheet (Type, Description)
            VALUES ('{}', '{}')""".format(crew_type, description))

            connection.commit()

        except DatabaseError:
            traceback.print_exc()
            return False
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
            VALUES ('{}', '{}')""".format(name, description))

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
            VALUES ('{}', '{}', {}, {})""".format(name, description, weight, usages))

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
            VALUES ('{}', '{}', '{}', '{}')""".format(name, role, faction, description))

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
            VALUES ('{}', '{}')""".format(name, description))

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
            VALUES ('{}', {}, '{}')""".format(name, quality, description))

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
    if isinstance(description, str) and isinstance(crew_char, bool):
        connection = establish_connection()
        cursor = connection.cursor()

        try:
            cursor.execute("""
            INSERT INTO XpTrigger (Description, Crew_Char)
            VALUES ('{}', {})""".format(description, crew_char))

            connection.commit()
        except DatabaseError:
            traceback.print_exc()
            return False
        return True
    return False


def insert_simple_relation(table: str, first_column, second_column) -> bool:
    """
    Insert a simple relation between two other tables a given table in BladesInTheDark Database.

    :param table: table to write the relation in
    :param first_column: value of the first table
    :param second_column: value of the second table
    :return: True if the simple relation is added, False otherwise
    """
    connection = establish_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
        INSERT INTO '{}'
        VALUES (?,?)""".format(table), (first_column, second_column))

        connection.commit()
    except DatabaseError:
        traceback.print_exc()
        return False
    return True


def insert_complex_relation(table: str, first_column, second_column, third_column) -> bool:
    """
    Insert a relation with a third attribute between two other tables a given table in BladesInTheDark Database.

    :param table: table to write the relation in
    :param first_column: value of the first table
    :param second_column: value of the second table
    :param third_column: extra information for the relation
    :return: True if the peculiar relation is added, False otherwise
    """
    connection = establish_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO '{}'
            VALUES (?,?,?)""".format(table), (first_column, second_column, third_column))

        connection.commit()
    except DatabaseError:
        traceback.print_exc()
        return False
    return True


def insert_char_action(character: str, action: str, dots: int) -> bool:
    """
    Insert a new relation in Char_Action table in BladesInTheDark Database.

    :param character: class of the character
    :param action: name of the action
    :param dots: level of the action
    :return: True if the relation is added, False otherwise
    """
    if isinstance(character, str) and isinstance(action, str) and isinstance(dots, int):
        return insert_complex_relation("Char_Action", character, action, dots)
    return False


def insert_char_friend(character: str, NPC: int) -> bool:
    """
    Insert a new relation in Char_Friend table in BladesInTheDark Database.

    :param character: class of the character
    :param NPC: id of the NPC
    :return: True if the relation is added, False otherwise
    """
    if isinstance(character, str) and isinstance(NPC, int):
        return insert_simple_relation("Char_Friend", character, NPC)
    return False


def insert_char_item(character: str, item: str) -> bool:
    """
    Insert a new relation in Char_Item table in BladesInTheDark Database.

    :param character: class of the character
    :param item: name of the item
    :return: True if the relation is added, False otherwise
    """
    if isinstance(character, str) and isinstance(item, str):
        return insert_simple_relation("Char_Item", character, item)
    return False


def insert_char_sa(character: str, sa: str) -> bool:
    """
    Insert a new relation in Char_SA table in BladesInTheDark Database.

    :param character: class of the character
    :param sa: name of the special ability
    :return: True if the relation is added, False otherwise
    """
    if isinstance(character, str) and isinstance(sa, str):
        return insert_simple_relation("Char_SA", character, sa)
    return False


def insert_char_xp(character: str, xp_id: int, peculiar: bool) -> bool:
    """
    Insert a new relation in Char_Xp table in BladesInTheDark Database.

    :param character: class of the character
    :param xp_id: id of the xp trigger
    :param peculiar: True if the xp trigger is peculiar of the character class, False otherwise
    :return: True if the relation is added, False otherwise
    """
    if isinstance(character, str) and isinstance(xp_id, int) and isinstance(peculiar, bool):
        return insert_complex_relation("Char_Xp", character, xp_id, peculiar)
    return False


def insert_crew_contact(crew: str, contact: int) -> bool:
    """
    Insert a new relation in Crew_Contact table in BladesInTheDark Database.

    :param crew: type of the crew
    :param contact: id of the NPC
    :return: True if the relation is added, False otherwise
    """
    if isinstance(crew, str) and isinstance(contact, int):
        return insert_simple_relation("Crew_Contact", crew, contact)
    return False


def insert_crew_hg(hg: str, crew: str) -> bool:
    """
    Insert a new relation in Crew_HG table in BladesInTheDark Database.

    :param hg: name of the hunting ground
    :param crew: type of the crew
    :return: True if the relation is added, False otherwise
    """
    if isinstance(hg, str) and isinstance(crew, str):
        return insert_simple_relation("Crew_HG", hg, crew)
    return False


def insert_crew_sa(crew: str, sa: str, peculiar: bool) -> bool:
    """
    Insert a new relation in Crew_SA table in BladesInTheDark Database.

    :param crew: type of the crew
    :param sa: name of the special ability
    :param peculiar: True if the special ability is peculiar of the crew type, False otherwise
    :return: True if the relation is added, False otherwise
    """
    if isinstance(crew, str) and isinstance(sa, str) and isinstance(peculiar, bool):
        return insert_complex_relation("Crew_SA", crew, sa, peculiar)
    return False


def insert_crew_starting_upgrade(crew: str, upgrade: str, quality: int) -> bool:
    """
    Insert a new relation in Crew_StartingUpgrade table in BladesInTheDark Database.

    :param crew: type of the crew
    :param upgrade: name of the starting upgrade
    :param quality: quality of the starting upgrade
    :return: True if the relation is added, False otherwise
    """
    if isinstance(crew, str) and isinstance(upgrade, str) and isinstance(quality, int):
        return insert_complex_relation("Crew_StartingUpgrade", crew, upgrade, quality)
    return False


def insert_crew_upgrade(crew: str, upgrade: str) -> bool:
    """
    Insert a new relation in Crew_Upgrade table in BladesInTheDark Database.

    :param crew: type of the crew
    :param upgrade: name of the upgrade
    :return: True if the relation is added, False otherwise
    """
    if isinstance(crew, str) and isinstance(upgrade, str):
        return insert_simple_relation("Crew_Upgrade", crew, upgrade)
    return False


def insert_crew_xp(crew: str, xp_id: int, peculiar: bool) -> bool:
    """
    Insert a new relation in Crew_Xp table in BladesInTheDark Database.

    :param crew: type of the crew
    :param xp_id: id of the xp trigger
    :param peculiar: True if the xp trigger is peculiar of the crew type, False otherwise
    :return: True if the relation is added, False otherwise
    """
    if isinstance(crew, str) and isinstance(xp_id, int) and isinstance(peculiar, bool):
        return insert_complex_relation("Crew_Xp", crew, xp_id, peculiar)
    return False


def insert_starting_cohort(crew: str, gang_exp: bool, cohort_type: str) -> bool:
    """
    Insert a new relation in Starting_Cohort table in BladesInTheDark Database.

    :param crew: type of the crew
    :param gang_exp: True if the cohort is a gang, False if it's an expert
    :param cohort_type: type of the cohort
    :return: True if the relation is added, False otherwise
    """
    if isinstance(crew, str) and isinstance(gang_exp, bool) and isinstance(cohort_type, str):
        return insert_complex_relation("Starting_Cohort", crew, gang_exp, cohort_type)
    return False


def delete_user_game(user_id: int, game_id: int) -> bool:
    """
    Removes the specified occurrence in the User_Game table from the Data Baase

    :param user_id: telegram id of the user.
    :param game_id: identifier of the game.
    :return:
    """
    if isinstance(user_id, int) and isinstance(game_id, int):
        connection = establish_connection()
        cursor = connection.cursor()

        try:
            cursor.execute("""
            DELETE FROM User_Game WHERE (User_ID, Game_ID) = ({}, {})
            """.format(user_id, game_id))

            connection.commit()
        except DatabaseError:
            traceback.print_exc()
            return False
        return True
    return False
