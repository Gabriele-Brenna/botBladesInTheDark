import json
import os
import sqlite3
import traceback
from pathlib import Path
from sqlite3 import Connection


def establish_connection(foreign_key: bool = True) -> Connection:
    root_dir = Path(__file__).parent.parent.parent.resolve()
    root_dir = os.path.join(root_dir, "resources")
    db_path = os.path.join(root_dir, 'BladesInTheDark.db')
    connection = sqlite3.connect(db_path)
    if foreign_key:
        connection.execute("PRAGMA foreign_keys = 1")
        connection.commit()
    return connection


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


def exists_game(game_id: int) -> bool:
    """
    Checks if the specified game has a matching value in the Game table of the database

    :param game_id: is the game to check
    :return: True if the game exists, False otherwise
    """
    connection = establish_connection()
    cursor = connection.cursor()

    cursor.execute("""
                SELECT *
                FROM Game
                WHERE Game_ID = '{}'
                """.format(game_id))

    rows = cursor.fetchall()

    if not rows:
        return False
    return True


def is_json(myjson) -> bool:
    """
    Check if an object is a json string or not.

    :param myjson: object to check
    :return: True if it's a json string, False otherwise
    """
    try:
        json.loads(myjson)
    except ValueError:
        traceback.print_exc()
        return False
    return True
