import json
from typing import List

from character.Ghost import Ghost
from character.Hull import Hull
from character.Human import Human
from character.NPC import NPC
from character.Vampire import Vampire
from component.Clock import Clock
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


def score_from_json(score: str):
    return Score.from_json(json.loads(score))


def npcs_from_json(npcs: str):
    data = json.loads(npcs)
    return list(map(NPC.from_json, data))


def from_json(crew_str: str, factions_str: str, npcs_str: str, characters_str: str, score_str: str, clocks_str: str):
    factions = factions_from_json(factions_str)

    clocks = clocks_from_json(clocks_str)

    npcs = npcs_from_json(npcs_str)
    for npc in npcs:
        npc.faction = find_obj(npc.faction, factions)

    crew = crew_from_json(crew_str)
    crew.contact = find_obj(crew.contact, npcs)

    characters = characters_from_json(characters_str)
    for c in characters:
        c.friend = find_obj(c.friend, npcs)
        c.enemy = find_obj(c.enemy, npcs)

    score = score_from_json(score_str)
    temp = factions.append(npcs)
    print(factions)
    score.target = find_obj(score.target, temp)


def find_obj(name: str, to_search: List):
    for obj in to_search:
        if obj.name == name:
            return obj
    return name
