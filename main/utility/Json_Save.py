import copy
import json
from typing import List

from character.Ghost import Ghost
from character.Hull import Hull
from character.Human import Human
from character.Item import Item
from character.NPC import NPC
from character.Vampire import Vampire
from component.Clock import Clock
from controller.DBreader import query_game_json, query_users, query_pc_json
from game.Game import Game
from game.Player import Player
from game.Score import Score
from organization.Crew import Crew
from organization.Faction import Faction


def crew_from_json(crew: str):
    return Crew.from_json(json.loads(crew))


def factions_from_json(factions: str):
    data = json.loads(factions)
    return list(map(Faction.from_json, data))


def clocks_from_json(clocks: str):
    data = json.loads(clocks)
    return list(map(Clock.from_json, data))


def characters_from_json(characters: str):
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
    data = json.loads(scores)
    return list(map(Score.from_json, data))


def npcs_from_json(npcs: str):
    data = json.loads(npcs)
    return list(map(NPC.from_json, data))


def items_from_json(items: str):
    data = json.loads(items)
    return list(map(Item.from_json, data))


def setup(game: Game):
    db_game = query_game_json(game.identifier)
    factions = factions_from_json(db_game["Faction_JSON"])
    game.factions = factions

    clocks = clocks_from_json(db_game["Clock_JSON"])
    game.clocks = clocks

    NPCs = npcs_from_json(db_game["NPC_JSON"])
    for npc in NPCs:
        npc.faction = find_obj(npc.faction, factions)
    game.NPCs = NPCs

    crew = crew_from_json(db_game["Crew_JSON"])
    crew.contact = find_obj(crew.contact, NPCs)
    game.crew = crew

    temp = copy.deepcopy(factions)
    temp.append(NPCs)
    scores = scores_from_json(db_game["Score_JSON"])
    for score in scores:
        score.target = find_obj(score.target, temp)
    game.scores = scores

    crafted_items = items_from_json(db_game["Crafted_Item_JSON"])
    game.crafted_items = crafted_items

    journal = db_game["Journal"]
    game.journal = journal

    users = []
    users_tuple = query_users(game.identifier)

    for t in users_tuple:
        users.append(Player(*t))

    characters_dict = query_pc_json(game.identifier)

    for u in users:
        characters = characters_from_json(characters_dict[u.player_id])
        for c in characters:
            c.friend = find_obj(c.friend, NPCs)
            c.enemy = find_obj(c.enemy, NPCs)
        u.characters = characters

    game.users = users


def find_obj(name: str, to_search: List):
    for obj in to_search:
        if obj.name == name:
            return obj
    return name
