import os.path
from random import randint
from typing import List

from bs4 import BeautifulSoup

from utility.FilesManager import get_resources_folder

colors = [(32, 3, 255), (255, 0, 0), (144, 0, 206), (0, 255, 81), (229, 255, 0), (0, 229, 255), (255, 0, 204)]


def modify(players: List[str]) -> bytes:
    name = os.path.join(get_resources_folder(), "map")
    name = os.path.join(name, "DoskvolMapTemplate.html")

    with open(name, "r") as m:
        game_map = BeautifulSoup(m, 'html.parser')
    body = game_map.select_one("body")
    ul_tag = body.find('ul', recursive=False)
    div_li_tag = ul_tag.find("div", {"class": "dropdown-content players"})

    svg_tag = body.find('svg', recursive=False)

    for i in range(len(players)):
        div_li_tag.insert(0, BeautifulSoup('<button class="element" id="p{}">{}</button>'.
                                           format(i + 1, players[i]), 'html.parser'))
        if i < len(colors):
            circle_tag = BeautifulSoup('<circle class="marker p{}" cx="0" cy="0" r="0" fill="rgb{}"></circle>'.
                                       format(i + 1, colors[i]), 'html.parser')
        else:
            circle_tag = BeautifulSoup('<circle class="marker p{}" cx="0" cy="0" r="0" fill="rgb({}, {}, {})">'
                                       '</circle>'.format(i + 1, randint(150, 240), randint(150, 240),
                                                          randint(150, 240)), 'html.parser')
        svg_tag.append(circle_tag)

    return bytes(str(game_map), 'UTF-8')
