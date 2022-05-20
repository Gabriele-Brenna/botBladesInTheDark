import textwrap

from PIL import Image, ImageDraw
from PIL import ImageFont

from character.Playbook import Playbook
from component.Clock import Clock
from utility.imageFactory.factoryUtils import average_char_size

from controller.DBreader import *


def paste_name(name: str, sheet: Image):
    name_box_dim = (300, 20)
    name_box = Image.new('RGBA', name_box_dim, (255, 255, 255, 255))
    draw = ImageDraw.Draw(name_box)

    font = ImageFont.truetype("arial.ttf", 16)
    draw.text((0, 0), name, align="left", fill="black", font=font)

    coordinates = (40, 95)
    sheet.paste(name_box, coordinates)


def paste_alias(alias: str, sheet: Image):
    box_dim = (180, 20)
    box = Image.new('RGBA', box_dim, (255, 255, 255, 255))
    draw = ImageDraw.Draw(box)

    font = ImageFont.truetype("arial.ttf", 16)
    draw.text((0, 0), alias, align="left", fill="black", font=font)

    coordinates = (350, 95)
    sheet.paste(box, coordinates)


def paste_crew(crew_name: str, sheet: Image):
    box_dim = (180, 20)
    box = Image.new('RGBA', box_dim, (255, 255, 255, 255))
    draw = ImageDraw.Draw(box)

    font = ImageFont.truetype("arial.ttf", 16)
    draw.text((0, 0), crew_name, align="left", fill="black", font=font)

    coordinates = (350, 55)
    sheet.paste(box, coordinates)


def paste_look(look: str, sheet: Image):
    box_dim = (490, 20)
    box = Image.new('RGBA', box_dim, (255, 255, 255, 255))
    draw = ImageDraw.Draw(box)

    font = ImageFont.truetype("arial.ttf", 16)
    draw.text((0, 0), look, align="left", fill="black", font=font)

    coordinates = (40, 135)
    sheet.paste(box, coordinates)


def paste_heritage(heritage: str, sheet: Image):
    box_dim = (245, 20)
    box = Image.new('RGBA', box_dim, (255, 255, 255, 255))
    draw = ImageDraw.Draw(box)

    font = ImageFont.truetype("arial.ttf", 16)
    draw.text((0, 0), heritage, align="left", fill="black", font=font)

    coordinates = (40, 180)
    sheet.paste(box, coordinates)


def paste_background(background: str, sheet: Image):
    box_dim = (240, 20)
    box = Image.new('RGBA', box_dim, (255, 255, 255, 255))
    draw = ImageDraw.Draw(box)

    font = ImageFont.truetype("arial.ttf", 16)
    draw.text((0, 0), background, align="left", fill="black", font=font)

    coordinates = (295, 180)
    sheet.paste(box, coordinates)


def paste_vice(vice: Vice, sheet: Image):
    vice_text = vice.name + ": " + vice.description

    y = 0

    if len(vice_text) <= 80:
        font = ImageFont.truetype("verdana.ttf", 12)
        box_dim = (490, 27)
    elif len(vice_text) <= 150:
        font = ImageFont.truetype("verdana.ttf", 10)
        box_dim = (490, 27)
    else:
        font = ImageFont.truetype("arial.ttf", 9)
        box_dim = (490, 32)
        y = 4

    box = Image.new('RGBA', box_dim, (255, 255, 255, 255))
    draw = ImageDraw.Draw(box)

    lines = textwrap.wrap(vice_text, width=int((box_dim[0]) / average_char_size(vice_text, font)))

    for line in lines:
        draw.text((1, y), text=line, font=font, fill="black")
        y += font.getsize("Text")[1]

    if vice.purveyor is not None:
        vice_purveyor = "Purveyor: " + vice.purveyor
        draw.text((1, y), vice_purveyor, align="left", fill="black", font=font)

    coordinates = (40, 233)
    sheet.paste(box, coordinates)


def paste_hull_functions(functions: List[str], sheet: Image):
    function_text = ""
    for function in functions:
        function_text += function + ", "

    y = 0

    if len(function_text) <= 80:
        font = ImageFont.truetype("times.ttf", 12)
        box_dim = (490, 27)
    elif len(function_text) <= 150:
        font = ImageFont.truetype("times.ttf", 10)
        box_dim = (490, 27)
    else:
        font = ImageFont.truetype("times.ttf", 9)
        box_dim = (490, 32)
        y = 4

    box = Image.new('RGBA', box_dim, (255, 255, 255, 255))
    draw = ImageDraw.Draw(box)

    lines = textwrap.wrap(function_text, width=int((box_dim[0]) / average_char_size(function_text, font)))

    for line in lines:
        draw.text((1, y), text=line.upper(), font=font, fill="black")
        y += font.getsize("Text")[1]

    coordinates = (40, 245)
    sheet.paste(box, coordinates)


def paste_stress(stress_level: int, stress_limit: int, sheet: Image):
    stress_empty = Image.open("resources/images/StressEmpty.png")
    stress_full = Image.open("resources/images/StressFull.png")

    box_dim = (130, 30)
    box = Image.new('RGBA', box_dim, (255, 255, 255, 255))

    stress_x = 0
    for i in range(stress_level):
        box.paste(stress_full, (stress_x, 0))
        stress_x += 15
    for i in range(stress_limit - stress_level):
        box.paste(stress_empty, (stress_x, 0))
        stress_x += 15

    coordinates = (80, 291)
    sheet.paste(box, coordinates)


def paste_traumas(traumas: List[str], sheet: Image):
    paste_traumas_notches(len(traumas), sheet)
    paste_traumas_names(traumas, sheet)


def paste_traumas_notches(traumas_n: int, sheet: Image):
    trauma_empty = Image.open("resources/images/TraumaEmpty.png")
    trauma_full = Image.open("resources/images/TraumaFull.png")

    notch_box_dim = (52, 20)
    notch_box = Image.new('RGBA', notch_box_dim, (255, 255, 255, 255))

    trauma_x = 0
    for i in range(4):
        if i < traumas_n:
            notch_box.paste(trauma_full, (trauma_x, 0))
        else:
            notch_box.paste(trauma_empty, (trauma_x, 0))
        trauma_x += 14

    notch_coordinates = (220, 301)
    sheet.paste(notch_box, notch_coordinates)


def paste_traumas_names(traumas: List[str], sheet: Image):
    box_dim = (260, 35)
    box = Image.new('RGBA', box_dim, (255, 255, 255, 255))
    draw = ImageDraw.Draw(box)

    font = ImageFont.truetype("verdana.ttf", 14)

    text = ""
    for trauma in traumas:
        text += trauma + ", "

    lines = textwrap.wrap(text, width=int((box_dim[0]) / average_char_size(text, font)))

    y = 0
    for line in lines:
        draw.text((1, y), text=line, font=font, fill="black")
        y += font.getsize("Text")[1]

    list_coordinates = (273, 292)
    sheet.paste(box, list_coordinates)


def paste_harms(harms: List[List[str]], sheet: Image):
    last_box_dim = (348, 28)
    last_box = Image.new('RGBA', last_box_dim, (255, 255, 255, 255))
    draw = ImageDraw.Draw(last_box)

    font = ImageFont.truetype("verdanab.ttf", 16)
    draw.text((last_box_dim[0] / 2, last_box_dim[1] / 2), harms[len(harms) - 1][0], anchor="mm", fill="black",
              font=font)

    coordinates = (52, 340)
    sheet.paste(last_box, coordinates)

    x_harm = 53
    y_harm = 371
    for i in range(len(harms) - 1, 0, -1):
        for j in range(len(harms[i - 1])):
            box_dim = (172, 28)
            box = Image.new('RGBA', box_dim, (255, 255, 255, 255))
            draw = ImageDraw.Draw(box)

            font = ImageFont.truetype("verdanai.ttf", 12)
            draw.text((box_dim[0] / 2, box_dim[1] / 2), harms[i - 1][j], anchor="mm", fill="black", font=font)

            coordinates = (x_harm, y_harm)
            sheet.paste(box, coordinates)

            x_harm += 174
        x_harm = 53
        y_harm += 29


def paste_healing_clock(healing: Clock, sheet: Image):
    box_dim = (35, 35)
    box = Image.new('RGBA', box_dim, (255, 255, 255, 255))
    draw = ImageDraw.Draw(box)

    angle = 360 / healing.segments
    start = -90
    for i in range(healing.segments):
        if i < healing.progress:
            fill = "red"
        else:
            fill = "white"
        draw.pieslice(((0, 0), (box_dim[0] - 1, box_dim[1] - 1)), start=start, end=start + angle, fill=fill,
                      outline="black")
        start += angle

    coordinates = (495, 325)
    sheet.paste(box, coordinates)


def paste_armor_uses(armors: List[bool], sheet: Image):
    box_dim = (10, 10)
    cell_x = 518
    cell_y = 383
    font = ImageFont.truetype("verdanab.ttf", 8)

    for armor in armors:
        cell = Image.new('RGBA', box_dim, (255, 255, 255, 255))
        draw = ImageDraw.Draw(cell)

        shape = ((0, 0), (box_dim[0] - 1, box_dim[1] - 1))
        draw.rectangle(shape, outline="black", width=1)

        if armor is True:
            draw.text((2, 0), "*", fill="red", stroke_width=1, font=font)

        sheet.paste(cell, (cell_x, cell_y))
        cell_y += 18


def paste_description(description: str, sheet: Image, width: int = 510, height: int = 410):
    box_dim = (width, height)
    box = Image.new('RGBA', box_dim, (255, 255, 255, 255))
    draw = ImageDraw.Draw(box)

    font = ImageFont.truetype("times.ttf", 14)

    lines = textwrap.wrap(description, width=int((box_dim[0] - 15) / average_char_size(description, font)))

    y = 2
    for i in range(len(lines)):
        draw.multiline_text((4, y), text=lines[i], font=font, fill="black")
        y += font.getsize("Text")[1] + 3

    y = font.getsize("Text")[1] + 4
    for j in range(25):
        draw.rectangle(((4, y), (box_dim[0] - 5, y)), outline="gray", width=1)
        y += font.getsize("Text")[1] + 3

    coordinates = (20, 450)
    sheet.paste(box, coordinates)


def paste_pc_class(pc_class: str, sheet: Image):
    box_dim = (285, 57)
    box = Image.new('RGBA', box_dim, (220, 221, 222, 255))
    draw = ImageDraw.Draw(box)

    bold = ImageFont.truetype("verdanab.ttf", 50)

    draw.text((box_dim[0] / 2, box_dim[1] / 2), text=pc_class.upper(), font=bold, fill="black", anchor="mm")

    coordinates = (542, 45)
    sheet.paste(box, coordinates)


def paste_class_description(pc_class: str, sheet: Image):

    description = query_sheet_descriptions(pc_class)[0]

    box_dim = (90, 57)
    box = Image.new('RGBA', box_dim, (220, 221, 222, 255))
    draw = ImageDraw.Draw(box)

    font = ImageFont.truetype("verdana.ttf", 9)

    lines = textwrap.wrap(description, width=int((box_dim[0] - 15) / average_char_size(description, font)))

    y = 10
    for i in range(len(lines)):
        draw.text((4, y), text=lines[i].upper(), font=font, fill="gray")
        y += font.getsize("Text")[1]

    coordinates = (827, 45)
    sheet.paste(box, coordinates)


def paste_special_abilities(abilities: List[SpecialAbility], sheet: Image):
    box_dim = (375, 340)
    box = Image.new('RGBA', box_dim, (220, 221, 222, 255))
    draw = ImageDraw.Draw(box)

    normal = ImageFont.truetype("verdana.ttf", 10)

    y = 1
    for ability in abilities:
        name = ability.name
        description = ability.description

        lines = textwrap.wrap(name + ": " + description,
                              width=int((box_dim[0]) / average_char_size(description, normal)))

        y_text = y
        for line in lines:
            draw.text((1, y_text), text=line, font=normal, fill="black")
            y_text += normal.getsize("Text")[1]

        draw.text((0, y), text=name, font=normal, fill="black", stroke_width=1, stroke_fill="gray")

        y = y_text
        y += normal.getsize("Text")[1]

    coordinates = (542, 115)

    sheet.paste(box, coordinates)


def paste_strange_friends(friend: NPC, enemy: NPC, pc_class: str, sheet: Image):
    friend_mark = Image.open("resources/images/SFfriend.png")
    enemy_mark = Image.open("resources/images/SFenemy.png")
    neutral_mark = Image.open("resources/images/SFneutral.png")
    complex_mark = Image.open("resources/images/SFneutral.png")

    box_dim = (200, 115)
    box = Image.new('RGBA', box_dim, (220, 221, 222, 255))
    draw = ImageDraw.Draw(box)

    normal = ImageFont.truetype("verdanai.ttf", 10)

    query_strange_friends = query_char_strange_friends(pc_class=pc_class)

    y = 2

    for npc in query_strange_friends:
        x = 2
        if npc == friend and npc == enemy:
            box.paste(complex_mark, (x, y))
        elif npc == friend:
            box.paste(friend_mark, (x, y))
        elif npc == enemy:
            box.paste(enemy_mark, (x, y))
        else:
            box.paste(neutral_mark, (x, y))

        x += 30

        npc_description = npc.name + ", " + npc.role
        lines = textwrap.wrap(npc_description,
                              width=int((box_dim[0] - 30) / average_char_size(npc_description, normal)))
        for line in lines:
            draw.text((x, y), text=line, font=normal, fill="black")
            y += normal.getsize("Text")[1]

        y += normal.getsize("Text")[1]

    coordinates = (542, 470)

    sheet.paste(box, coordinates)


def paste_ghost_enemies(enemies: List[str], sheet: Image):
    box_dim = (200, 115)
    box = Image.new('RGBA', box_dim, (220, 221, 222, 255))
    draw = ImageDraw.Draw(box)

    normal = ImageFont.truetype("verdanai.ttf", 10)

    y = 2

    for enemy in enemies:
        x = 4
        lines = textwrap.wrap(enemy,
                              width=int((box_dim[0] - 30) / average_char_size(enemy, normal)))
        for line in lines:
            draw.text((x, y), text=line, font=normal, fill="black")
            y += normal.getsize("Text")[1]

        y += normal.getsize("Text")[1]

    coordinates = (542, 470)

    sheet.paste(box, coordinates)


def paste_vampire_servants(servants: List[NPC], sheet: Image):
    servant_empty = Image.open("resources/images/RoundEmpty.png")
    servant_full = Image.open("resources/images/RoundFull.png")

    box_dim = (200, 115)
    box = Image.new('RGBA', box_dim, (220, 221, 222, 255))
    draw = ImageDraw.Draw(box)

    normal = ImageFont.truetype("verdanai.ttf", 10)

    query_strange_friends = query_char_strange_friends("Vampire")

    y = 2

    for npc in query_strange_friends:
        x = 2
        if npc in servants:
            box.paste(servant_full, (x, y))
        else:
            box.paste(servant_empty, (x, y))

        x += 15

        npc_description = npc.name + ", " + npc.role
        lines = textwrap.wrap(npc_description,
                              width=int((box_dim[0] - 30) / average_char_size(npc_description, normal)))
        for line in lines:
            draw.text((x, y), text=line, font=normal, fill="black")
            y += normal.getsize("Text")[1]

        y += normal.getsize("Text")[1]

    coordinates = (542, 470)

    sheet.paste(box, coordinates)


def paste_hull_frame(frame: str, sheet: Image):
    frame_empty = Image.open("resources/images/RoundEmpty.png")
    frame_full = Image.open("resources/images/RoundFull.png")

    box_dim = (370, 115)
    box = Image.new('RGBA', box_dim, (220, 221, 222, 255))
    draw = ImageDraw.Draw(box)

    normal = ImageFont.truetype("verdanai.ttf", 10)

    hull_frames = [
        "Small (cat size, -1 scale): A metal orb, a mechanical doll, a clockwork spider. Levitation—Reflexes",
        "Medium (human size): A metal mannequin, a clockwork animal. Life-Like Appearance—Spider Climb",
        "Heavy (wagon size, +1 scale): A hulking metal giant, a self-driving vehicle. Interior "
        "Chamber—Plating (special armor)"]

    y = 2

    for hull_frame in hull_frames:
        x = 2
        if frame in hull_frame:
            box.paste(frame_full, (x, y))
        else:
            box.paste(frame_empty, (x, y))

        x += 15

        lines = textwrap.wrap(hull_frame,
                              width=int((box_dim[0] - 30) / average_char_size(hull_frame, normal)))
        for line in lines:
            draw.text((x, y), text=line, font=normal, fill="black")
            y += normal.getsize("Text")[1]

        y += normal.getsize("Text")[1]

    coordinates = (542, 470)

    sheet.paste(box, coordinates)


def paste_hull_frame_features(features: List[SpecialAbility], sheet: Image):
    query_frame_features_s = query_frame_features(group="S")
    query_frame_features_m = query_frame_features(group="M")
    query_frame_features_l = query_frame_features(group="L")
    query_frame_features_e = query_frame_features(group="E")
    frame_features = [query_frame_features_s, query_frame_features_m, query_frame_features_l, query_frame_features_e]

    box_dim = (160, 360)
    box = Image.new('RGBA', box_dim, (255, 255, 255, 255))
    draw = ImageDraw.Draw(box)

    normal = ImageFont.truetype("verdanab.ttf", 10)

    y = 1
    for feature_group in frame_features:
        for feature in feature_group:
            if feature in features:
                color = "red"
            else:
                color = "gray"
            name = feature.name

            lines = textwrap.wrap(name,
                                  width=int((box_dim[0]) / average_char_size(name, normal)) - 10)

            y_text = y
            for line in lines:
                draw.text((10, y_text), text=line, font=normal, fill=color)
                y_text += normal.getsize("Text")[1]

            y = y_text
            y += normal.getsize("Text")[1]
        draw.rectangle(((4, y), (box_dim[0] - 5, y)), outline="gray", width=1)
        y += 5

    coordinates = (380, 470)

    sheet.paste(box, coordinates)


def paste_vampire_strictures(strictures: List[SpecialAbility],
                             sheet: Image):

    box_dim = (190, 360)
    box = Image.new('RGBA', box_dim, (255, 255, 255, 255))
    draw = ImageDraw.Draw(box)

    normal = ImageFont.truetype("verdanai.ttf", 10)

    y = 1
    for stricture in strictures:
        name = stricture.name
        description = stricture.description

        lines = textwrap.wrap(name + ": " + description,
                              width=int((box_dim[0]) / average_char_size(description, normal)) - 2)

        y_text = y
        for line in lines:
            draw.text((1, y_text), text=line, font=normal, fill="black")
            y_text += normal.getsize("Text")[1]

        draw.text((0, y), text=name, font=normal, fill="black", stroke_width=1, stroke_fill=(193, 15, 23, 255))

        y = y_text
        y += normal.getsize("Text")[1]

    coordinates = (350, 500)

    sheet.paste(box, coordinates)


def paste_xp_triggers(triggers: List[str], sheet: Image):
    box_dim = (374, 102)
    box = Image.new('RGBA', box_dim, (220, 221, 222, 255))
    draw = ImageDraw.Draw(box)

    normal = ImageFont.truetype("verdanai.ttf", 9)

    y = 1
    for trigger in triggers:

        lines = textwrap.wrap("- " + trigger,
                              width=int((box_dim[0]) / average_char_size(trigger, normal)))

        y_text = y
        for line in lines:
            draw.text((1, y_text), text=line, font=normal, fill="black")
            y_text += normal.getsize("Text")[1]

        y = y_text
        y += normal.getsize("Text")[1]

    coordinates = (542, 598)

    sheet.paste(box, coordinates)


def paste_items(items: List[Item], pc_class: str, sheet: Image):
    # DB query
    common = query_items(common_items=True)

    if not items:
        paste_character_items(pc_class, sheet)
        paste_items_right(common, sheet)
    else:
        paste_items_right(items, sheet)


def paste_character_items(pc_class: str, sheet: Image):
    # extraction with DB queries ;)
    peculiars = query_items(pc_class=pc_class)
    commons = []

    paste_items_peculiar(peculiars, sheet)
    paste_items_right(commons, sheet)


def paste_items_right(items: List[Item], sheet: Image):
    box_dim = (192, 228)
    box = Image.new('RGBA', box_dim, (255, 255, 255, 255))
    draw = ImageDraw.Draw(box)

    normal = ImageFont.truetype("verdana.ttf", 10)
    italic = ImageFont.truetype("verdanai.ttf", 10)

    y = 0
    for item in items:
        x = 5
        draw.rectangle(((x, y), (x + 10, y + 10)), outline="black", width=1)
        x += 10
        for i in range(item.weight - 1):
            draw.rectangle(((x, y + 5), (x + 5, y + 5)), outline="black", width=1)
            x += 5
            draw.rectangle(((x, y), (x + 10, y + 10)), outline="black", width=1)
            x += 10
        x += 5

        if item.weight == 0:
            font = italic
        else:
            font = normal

        if item.usages != -1:
            draw.text((x, y), text=item.name + " (" + str(item.usages) + ")", font=font, fill="black")
        else:
            draw.text((x, y), text=item.name, font=font, fill="black")

        y += 14

    coordinates = (918, 472)
    sheet.paste(box, coordinates)


def paste_items_peculiar(items: List[Item], sheet: Image):
    box_dim = (164, 100)
    box = Image.new('RGBA', box_dim, (220, 221, 222, 255))
    draw = ImageDraw.Draw(box)

    normal = ImageFont.truetype("verdana.ttf", 10)
    italic = ImageFont.truetype("verdanai.ttf", 10)

    y = 0
    for item in items:
        x = 0
        draw.rectangle(((x, y), (x + 10, y + 10)), outline="black", width=1, fill="white")
        x += 10
        for i in range(item.weight - 1):
            draw.rectangle(((x, y + 5), (x + 5, y + 5)), outline="black", width=1)
            x += 5
            draw.rectangle(((x, y), (x + 10, y + 10)), outline="black", width=1, fill="white")
            x += 10
        x += 5

        if item.weight == 0:
            font = italic
        else:
            font = normal

        if item.usages != -1:
            draw.text((x, y), text=item.name + " (" + str(item.usages) + ")", font=font, fill="black")
        else:
            draw.text((x, y), text=item.name, font=font, fill="black")

        y += 14

    coordinates = (750, 472)
    sheet.paste(box, coordinates)


def paste_load(load: int, sheet: Image):
    load_empty = Image.open("resources/images/LoadEmpty.png")
    load_full = Image.open("resources/images/LoadFull.png")

    box_dim = (240, 15)
    box = Image.new('RGBA', box_dim, (188, 190, 192, 255))
    draw = ImageDraw.Draw(box)

    bold = ImageFont.truetype("verdanab.ttf", 9)
    italic = ImageFont.truetype("verdanai.ttf", 9)

    draw.text((2, box_dim[1] / 2), text="LOAD", font=bold, fill="black", anchor="lm")

    x = bold.getsize("LOAD")[0] + 5
    loads = [3, 5, 6, 99]
    descriptions = ["light", "normal", "heavy", "encumbered"]
    check = False
    for i in range(len(loads)):
        if not check and load != 0 and load <= loads[i]:
            check = True
            box.paste(load_full, (x, 0))
        else:
            box.paste(load_empty, (x, 0))

        x += 14

        draw.text((x, box_dim[1] / 2), text=descriptions[i], font=italic, fill="black", anchor="lm")

        x += italic.getsize(descriptions[i])[0] + 2

    coordinates = (872, 455)
    sheet.paste(box, coordinates)


def paste_coin(coin: int, sheet: Image):
    box_dim = (10, 10)
    starting_x = 928
    starting_y = 68
    cell_x = starting_x
    cell_y = starting_y
    font = ImageFont.truetype("verdanab.ttf", 8)

    for i in range(4):
        cell = Image.new('RGBA', box_dim, (255, 255, 255, 255))
        draw = ImageDraw.Draw(cell)

        shape = ((0, 0), (box_dim[0] - 1, box_dim[1] - 1))
        draw.rectangle(shape, outline="black", width=1)

        if i < coin:
            draw.text((2, 0), "*", fill="orange", stroke_width=1, font=font)

        sheet.paste(cell, (cell_x, cell_y))

        if i % 2 == 0:
            cell_x += 14
        else:
            cell_y += 14
            cell_x = starting_x


def paste_stash(stash: int, sheet: Image):
    box_dim = (10, 10)
    starting_x = 960
    starting_y = 43
    cell_x = starting_x
    cell_y = starting_y
    font = ImageFont.truetype("verdanab.ttf", 8)

    gray = (199, 200, 202, 255)
    white = (255, 255, 255, 255)

    for i in range(40):

        if (i + 1) % 10 == 0:
            color = gray
        else:
            color = white

        cell = Image.new('RGBA', box_dim, color)
        draw = ImageDraw.Draw(cell)

        shape = ((0, 0), (box_dim[0] - 1, box_dim[1] - 1))
        draw.rectangle(shape, outline="black", width=1)

        if i < stash:
            draw.text((2, 0), "*", fill="orange", stroke_width=1, font=font)

        sheet.paste(cell, (cell_x, cell_y))

        if (i + 1) % 10 == 0:
            cell_y += 13
            cell_x = starting_x
        else:
            cell_x += 11


def paste_playbook(playbook: Playbook, sheet: Image):
    paste_playbook_exp(playbook, sheet)
    paste_playbook_points(playbook, sheet)


def paste_playbook_exp(playbook: Playbook, sheet: Image):
    notch_empty = Image.open("resources/images/NotchEmpty.png")
    notch_full = Image.open("resources/images/NotchFull.png")

    box_dim = (playbook.exp_limit * 9, 20)
    box = Image.new('RGBA', box_dim, (255, 255, 255, 255))

    exp_x = 0
    for i in range(playbook.exp):
        box.paste(notch_full, (exp_x, 0))
        exp_x += 9
    for i in range(playbook.exp_limit - playbook.exp):
        box.paste(notch_empty, (exp_x, 0))
        exp_x += 9

    coordinates = (1072 - box_dim[0], 102)
    sheet.paste(box, coordinates)


def paste_playbook_points(playbook: Playbook, sheet: Image):
    font = ImageFont.truetype("verdanab.ttf", 14)

    box_dim = (30, 20)
    box = Image.new('RGBA', box_dim, (255, 255, 255, 255))
    draw = ImageDraw.Draw(box)

    # Useful rect around the box
    shape = ((0, 0), (box_dim[0] - 1, box_dim[1] - 1))
    draw.rectangle(shape, outline="black", width=1)

    draw.text((box_dim[0] / 2, box_dim[1] / 2), str(playbook.points), font=font, fill="black", anchor="mm")

    coordinates = (1080, 102)
    sheet.paste(box, coordinates)


def paste_attributes(attributes: List[Attribute], sheet: Image):
    paste_attribute_exp(attributes, sheet)
    paste_attribute_points(attributes, sheet)
    paste_attribute_actions_dots(attributes, sheet)
    paste_separator_lines(sheet)


def paste_attribute_exp(attributes: List[Attribute], sheet: Image):
    notch_empty = Image.open("resources/images/NotchEmpty.png")
    notch_full = Image.open("resources/images/NotchFull.png")

    y_box = 135

    for attribute in attributes:
        box_dim = (attribute.exp_limit * 9, 20)
        box = Image.new('RGBA', box_dim, (255, 255, 255, 255))

        notch_x = 0
        for i in range(attribute.exp):
            box.paste(notch_full, (notch_x, 0))
            notch_x += 9
        for i in range(attribute.exp_limit - attribute.exp):
            box.paste(notch_empty, (notch_x, 0))
            notch_x += 9

        coordinates = (1072 - box_dim[0], y_box)
        sheet.paste(box, coordinates)

        y_box += 84


def paste_attribute_points(attributes: List[Attribute], sheet: Image):
    y_box = 135

    font = ImageFont.truetype("verdanab.ttf", 14)

    for attribute in attributes:
        box_dim = (30, 20)
        box = Image.new('RGBA', box_dim, (255, 255, 255, 255))
        draw = ImageDraw.Draw(box)

        # Useful rect around the box
        shape = ((0, 0), (box_dim[0] - 1, box_dim[1] - 1))
        draw.rectangle(shape, outline="black", width=1)

        draw.text((box_dim[0] / 2, box_dim[1] / 2), str(attribute.points), font=font, fill="black", anchor="mm")

        coordinates = (1080, y_box)
        sheet.paste(box, coordinates)

        y_box += 84


def paste_attribute_actions_dots(attributes: List[Attribute], sheet: Image):
    dot_empty = Image.open("resources/images/ActionDotEmpty.png")
    dot_full = Image.open("resources/images/ActionDotFull.png")
    font = ImageFont.truetype("verdanab.ttf", 11)

    y_box = 154

    for attribute in attributes:
        for action in attribute.actions:
            dots_box_dim = (142, 12)
            dots_box = Image.new('RGBA', dots_box_dim, (255, 255, 255, 255))
            draw = ImageDraw.Draw(dots_box)

            x_dot = 0

            for dot in range(action.limit):
                if dot < action.rating:
                    dots_box.paste(dot_full, (x_dot, 2))
                else:
                    dots_box.paste(dot_empty, (x_dot, 2))
                x_dot += 16

            draw.text((140, dots_box_dim[1] / 2), text=action.name.upper(), font=font, fill="black", anchor="rm")

            coordinates = (930, y_box)
            sheet.paste(dots_box, coordinates)

            y_box += 14
        y_box += 29


def paste_separator_lines(sheet: Image):
    draw = ImageDraw.Draw(sheet)
    line_x = 942
    line_y = 147

    for i in range(3):
        end_y = line_y + 66
        draw.rectangle(((line_x, line_y), (line_x, end_y)), outline="black", width=1)
        line_y += 82
