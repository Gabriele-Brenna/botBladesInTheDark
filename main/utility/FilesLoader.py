import copy
import json
from typing import List

from bs4 import BeautifulSoup

from character.Ghost import Ghost
from character.Hull import Hull
from character.Human import Human
from character.Item import Item
from character.NPC import NPC
from character.Vampire import Vampire
from component.Clock import Clock
from controller.DBreader import *
from game.Game import Game
from game.Player import Player
from game.Score import Score
from organization.Crew import Crew
from organization.Faction import Faction


def crew_from_json(crew: str):
    """
    This method is used to load a Crew from a json string

    :param crew: string with json syntax
    :return: Crew
    """
    return Crew.from_json(json.loads(crew))


def factions_from_json(factions: str):
    """
    This method is used to load a list of Factions from a json string

    :param factions: string with json syntax
    :return: list of Factions
    """
    data = json.loads(factions)
    return list(map(Faction.from_json, data))


def clocks_from_json(clocks: str):
    """
    This method is used to load a list of Clocks from a json string

    :param clocks: string with json syntax
    :return: list of Clocks
    """
    data = json.loads(clocks)
    return list(map(Clock.from_json, data))


def characters_from_json(characters: str):
    """
    This method is used to load a list of PCs from a json string. Depending on the Class attribute it will load a Human,
    a Vampire, a Hull or a Ghost

    :param characters: string with json syntax
    :return: list of PCs
    """
    data = json.loads(characters)
    characters = []
    for d in data:
        if d["Class"] == "Human":
            d.pop("Class")
            characters.append(Human.from_json(d))
        elif d["Class"] == "Vampire":
            d.pop("Class")
            characters.append(Vampire.from_json(d))
        elif d["Class"] == "Ghost":
            d.pop("Class")
            d.pop("need")
            characters.append(Ghost.from_json(d))
        elif d["Class"] == "Hull":
            d.pop("Class")
            characters.append(Hull.from_json(d))
    return characters


def scores_from_json(scores: str):
    """
    This method is used to load a list of Scores from a json string

    :param scores: string with json syntax
    :return: list of Scores
    """
    data = json.loads(scores)
    return list(map(Score.from_json, data))


def npcs_from_json(NPCs: str):
    """
    This method is used to load a list of NPCs from a json string
    
    :param NPCs: string with json syntax
    :return: list of NPCs
    """
    data = json.loads(NPCs)
    return list(map(NPC.from_json, data))


def items_from_json(items: str):
    """
    This method is used to load a list of Items from a json string

    :param items: string with json syntax
    :return: list of Items
    """
    data = json.loads(items)
    return list(map(Item.from_json, data))


def load_games() -> List[Game]:
    """
    Fetches from the Data Base all the stored Games and proceeds calling the setup() for all of them.

    :return: a list of Games
    """
    games_info = query_games_info()
    games = []
    if games_info:
        for elem in games_info:
            game = Game(**elem)
            setup(game)
            games.append(game)

    return games


def setup(game: Game) -> None:
    """
    This method is used to set all the Game's attribute contained in the DataBase via json strings.

    :param game: Game whose attributes will be set
    """
    db_game = query_game_json(game.identifier)

    if db_game["Faction_JSON"] is not None:
        game.factions = factions_from_json(db_game["Faction_JSON"])

    if db_game["Clock_JSON"] is not None:
        game.clocks = clocks_from_json(db_game["Clock_JSON"])

    if db_game["NPC_JSON"] is not None:
        game.NPCs = npcs_from_json(db_game["NPC_JSON"])
        for npc in game.NPCs:
            npc.faction = find_obj(npc.faction, game.factions)

    if db_game["Crew_JSON"] is not None:
        crew = crew_from_json(db_game["Crew_JSON"])
        crew.contact = find_obj(crew.contact, game.NPCs)
        game.crew = crew

    if db_game["Score_JSON"] is not None:
        temp = copy.deepcopy(game.factions)
        temp += game.NPCs
        scores = scores_from_json(db_game["Score_JSON"])
        for score in scores:
            score.target = find_obj(score.target, temp)
        game.scores = scores

    if db_game["Crafted_Item_JSON"] is not None:
        game.crafted_items = items_from_json(db_game["Crafted_Item_JSON"])

    if db_game["Journal"] is not None:
        game.journal.log = BeautifulSoup(db_game["Journal"], 'html.parser')
        scores = game.journal.log.find_all("div", attrs={"class": "score"}, recursive=True)
        game.journal.score_tag = scores[len(scores)-1]
        game.journal.indentation = len(game.scores)

    if db_game["State"] is not None:
        game.state = db_game["State"]

    users = []
    users_tuple = query_users_from_game(game.identifier)
    for t in users_tuple:
        users.append(Player(*t))

    characters_dict = query_pc_json(game.identifier)

    for u in users:
        characters = characters_from_json(characters_dict[u.player_id])
        for c in characters:
            c.friend = find_obj(c.friend, game.NPCs)
            c.enemy = find_obj(c.enemy, game.NPCs)
        u.characters = characters

    game.users = users


def find_obj(name: str, to_search: List):
    """
    Method used to find an object in a list given its name

    :param name: string with the name of the object
    :param to_search: list of object that have an attribute name
    :return: object with matching name
    """
    for obj in to_search:
        if obj.name == name:
            return obj
    return name
