from PIL import Image, ImageDraw
from PIL import ImageFont
import textwrap

from character.Playbook import Playbook
from organization.Claim import Claim
from organization.Cohort import Cohort
from organization.Lair import Lair
from organization.Upgrade import Upgrade
from utility.imageFactory.factoryUtils import average_char_size

from controller.DBreader import *


def paste_crew_name(name: str, sheet: Image):
    name_box_dim = (280, 20)
    name_box = Image.new('RGBA', name_box_dim, (255, 255, 255, 255))
    draw = ImageDraw.Draw(name_box)

    font = ImageFont.truetype("arial.ttf", 16)
    draw.text((0, 0), name, align="left", fill="black", font=font)

    coordinates = (50, 66)
    sheet.paste(name_box, coordinates)


def paste_crew_reputation(reputation: str, sheet: Image):
    name_box_dim = (220, 20)
    name_box = Image.new('RGBA', name_box_dim, (255, 255, 255, 255))
    draw = ImageDraw.Draw(name_box)

    font = ImageFont.truetype("arial.ttf", 16)
    draw.text((0, 0), reputation, align="left", fill="black", font=font)

    coordinates = (348, 66)
    sheet.paste(name_box, coordinates)


def paste_lair(lair: Lair, sheet: Image):
    paste_lair_description(lair.location, lair.description, sheet)
    paste_lair_claims(lair.claims, sheet)


def paste_lair_description(location: str, description: str, sheet: Image):
    lair_text = location + " - " + description

    if len(lair_text) <= 80:
        font = ImageFont.truetype("verdana.ttf", 12)
        box_dim = (490, 17)
        coordinates = (80, 110)
    else:
        font = ImageFont.truetype("verdana.ttf", 10)
        box_dim = (490, 27)
        coordinates = (80, 100)

    box = Image.new('RGBA', box_dim, (255, 255, 255, 255))
    draw = ImageDraw.Draw(box)

    lines = textwrap.wrap(lair_text, width=int((box_dim[0]) / average_char_size(lair_text, font)))

    y = 0
    for line in lines:
        draw.text((1, y), text=line, font=font, fill="black")
        y += font.getsize("Text")[1]

    sheet.paste(box, coordinates)


def paste_lair_claims(claims: List[Claim], sheet: Image):
    paste_claims(claims, sheet, 50, 172, 5, "LAIR")


def paste_claims(claims: List[Claim], sheet: Image, starting_x: int, starting_y: int, split: int, group: str):
    title_font = ImageFont.truetype("verdanab.ttf", 12)
    name_font = ImageFont.truetype("verdanab.ttf", 9)
    description_font = ImageFont.truetype("ariali.ttf", 9)

    box_dim = (86, 56)
    box = Image.new('RGBA', box_dim, (119, 120, 123, 255))
    draw = ImageDraw.Draw(box)

    connector_dim_horizontal = (14, 10)
    connector_dim_vertical = (10, 10)

    draw.text((box_dim[0] / 2, box_dim[1] / 2), text=group, font=title_font, fill="white", anchor="mm")
    sheet.paste(box, (starting_x, starting_y))

    x = starting_x + box_dim[0] + connector_dim_horizontal[0]
    y = starting_y
    for i in range(len(claims)):

        if i == split - 1:
            y += box_dim[1] + connector_dim_vertical[1]
            x = starting_x
        else:
            connector_horizontal = Image.new('RGBA', connector_dim_horizontal, (220, 221, 222, 255))
            sheet.paste(connector_horizontal,
                        (x - connector_dim_horizontal[0], y + int((box_dim[1] / 2) - connector_dim_horizontal[1] / 2)))

        if i > split - 2:
            connector_vertical = Image.new('RGBA', connector_dim_vertical, (220, 221, 222, 255))
            sheet.paste(connector_vertical,
                        (x + int(box_dim[0] / 2 - connector_dim_vertical[0] / 2), y - connector_dim_vertical[1]))

        box = Image.new('RGBA', box_dim, (220, 221, 222, 255))
        draw = ImageDraw.Draw(box)

        lines = textwrap.wrap(claims[i].name,
                              width=int((box_dim[0] - 20) / average_char_size(claims[i].description, description_font)))
        y_title = 5
        for j in range(len(lines)):
            draw.text((box_dim[0] / 2, y_title), text=lines[j].upper(), font=name_font, fill="black", anchor="mt")
            y_title += description_font.getsize("Text")[1] + 2

        lines = textwrap.wrap(claims[i].description,
                              width=int((box_dim[0]) / average_char_size(claims[i].description, description_font)))
        y_descr = int(box_dim[1] / 2 - 5)
        for j in range(len(lines)):
            draw.text((2, y_descr), text=lines[j], font=description_font, fill="black")
            y_descr += description_font.getsize("Text")[1]

        sheet.paste(box, (x, y))
        x += 100


def paste_crew_description(description: str, sheet: Image):
    box_dim = (545, 376)
    box = Image.new('RGBA', box_dim, (255, 255, 255, 255))
    draw = ImageDraw.Draw(box)

    font = ImageFont.truetype("times.ttf", 14)

    lines = textwrap.wrap(description, width=int((box_dim[0] - 15) / average_char_size(description, font)))

    y = 2
    for i in range(len(lines)):
        draw.text((4, y), text=lines[i], font=font, fill="black")
        y += font.getsize("Text")[1] + 3

    y = font.getsize("Text")[1] + 4
    for j in range(23):
        draw.rectangle(((4, y), (box_dim[0] - 5, y)), outline="gray", width=1)
        y += font.getsize("Text")[1] + 3

    coordinates = (20, 484)
    sheet.paste(box, coordinates)


def paste_rep(rep: int, turfs: int, sheet: Image):
    rep_empty = Image.open("resources/images/StressEmpty.png")
    rep_full = Image.open("resources/images/StressFull.png")
    turf_full = Image.open("resources/images/TurfFull.png")
    turf_rep = Image.open("resources/images/TurfRep.png")
    turf_empty = Image.open("resources/images/TurfEmpty.png")

    box_dim = (175, 30)
    box = Image.new('RGBA', box_dim, (255, 255, 255, 255))

    notch_x = 0
    for i in range(6):
        if i < rep:
            box.paste(rep_full, (notch_x, 0))
        else:
            box.paste(rep_empty, (notch_x, 0))
        notch_x += 15
    for j in range(6, 12):
        if j < rep:
            box.paste(turf_rep, (notch_x, 0))
        elif j >= (12 - turfs):
            box.paste(turf_full, (notch_x, 0))
        else:
            box.paste(turf_empty, (notch_x, 0))
        notch_x += 15

    coordinates = (77, 140)
    sheet.paste(box, coordinates)


def paste_hold(hold: bool, sheet: Image):
    hold_empty = Image.open("resources/images/StressEmpty.png")
    hold_full = Image.open("resources/images/StressFull.png")

    box_dim = (10, 30)
    weak = Image.new('RGBA', box_dim, (255, 255, 255, 255))
    strong = Image.new('RGBA', box_dim, (255, 255, 255, 255))

    if hold:
        weak.paste(hold_empty, (0, 0))
        strong.paste(hold_full, (0, 0))
    else:
        weak.paste(hold_full, (0, 0))
        strong.paste(hold_empty, (0, 0))

    c_weak = (378, 142)
    sheet.paste(weak, c_weak)
    c_strong = (432, 142)
    sheet.paste(strong, c_strong)


def paste_tier(tier: int, sheet: Image):
    box_dim = (84, 17)
    box = Image.new('RGBA', box_dim, (226, 227, 228, 255))
    draw = ImageDraw.Draw(box)

    x = 5
    y = 2
    for i in range(4):
        if i + 1 <= tier:
            color = "red"
        else:
            color = "white"
        draw.ellipse([(x, y), (x + 12, y + 12)], fill=color, outline="black")
        x += 20

    coordinates = (482, 137)
    sheet.paste(box, coordinates)


def paste_heat(heat: int, sheet: Image):
    rep_empty = Image.open("resources/images/StressEmpty.png")
    rep_full = Image.open("resources/images/StressFull.png")

    box_dim = (138, 32)
    box = Image.new('RGBA', box_dim, (255, 255, 255, 255))

    stress_x = 0
    for i in range(heat):
        box.paste(rep_full, (stress_x, 0))
        stress_x += 16
    for i in range(9 - heat):
        box.paste(rep_empty, (stress_x, 0))
        stress_x += 16

    coordinates = (87, 426)
    sheet.paste(box, coordinates)


def paste_wanted_level(w_level: int, sheet: Image):
    trauma_empty = Image.open("resources/images/TraumaEmpty.png")
    trauma_full = Image.open("resources/images/TraumaFull.png")

    notch_box_dim = (70, 20)
    notch_box = Image.new('RGBA', notch_box_dim, (255, 255, 255, 255))

    trauma_x = 0
    for i in range(4):
        if i < w_level:
            notch_box.paste(trauma_full, (trauma_x, 0))
        else:
            notch_box.paste(trauma_empty, (trauma_x, 0))
        trauma_x += 19

    notch_coordinates = (239, 438)
    sheet.paste(notch_box, notch_coordinates)


def paste_vault(coins: int, vault_capacity: int, sheet: Image):
    box_dim = (10, 10)
    starting_x = 320
    starting_y = 442
    cell_x = starting_x
    cell_y = starting_y
    font = ImageFont.truetype("verdanab.ttf", 8)

    for i in range(vault_capacity):

        cell = Image.new('RGBA', box_dim, (255, 255, 255, 255))
        draw = ImageDraw.Draw(cell)

        shape = ((0, 0), (box_dim[0] - 1, box_dim[1] - 1))
        draw.rectangle(shape, outline="black", width=1)

        if i < coins:
            draw.text((2, 0), "*", fill="orange", stroke_width=1, font=font)

        sheet.paste(cell, (cell_x, cell_y))

        if (i + 1) % 16 == 0:
            cell_y += 13
            cell_x = starting_x - 2
        else:
            if (i + 1) == 4 or (i + 1) == 8:
                cell_x += 21
            elif (i + 1) > 16:
                cell_x += 16
            else:
                cell_x += 15

    if vault_capacity < 16:
        for i in range(vault_capacity, 16):
            cell = Image.new('RGBA', box_dim, (255, 255, 255, 255))
            draw = ImageDraw.Draw(cell)

            shape = ((0, 0), (box_dim[0] - 1, box_dim[1] - 1))
            draw.rectangle(shape, outline="grey", width=1)

            sheet.paste(cell, (cell_x, cell_y))

            if (i + 1) == 4 or (i + 1) == 8:
                cell_x += 21
            elif (i + 1) > 16:
                cell_x += 16
            else:
                cell_x += 15


def paste_crew_type(crew_type: str, sheet: Image):
    box_dim = (285, 57)
    box = Image.new('RGBA', box_dim, (220, 221, 222, 255))
    draw = ImageDraw.Draw(box)

    bold = ImageFont.truetype("verdanab.ttf", 42)

    draw.text((box_dim[0] / 2, box_dim[1] / 2), text=crew_type.upper(), font=bold, fill="black", anchor="mm")

    coordinates = (578, 15)
    sheet.paste(box, coordinates)


def paste_crew_type_description(crew_type: str, sheet: Image):

    description = query_sheet_descriptions(crew_type)
    box_dim = (94, 60)
    box = Image.new('RGBA', box_dim, (220, 221, 222, 255))
    draw = ImageDraw.Draw(box)

    font = ImageFont.truetype("verdana.ttf", 9)

    lines = textwrap.wrap(description, width=int((box_dim[0] - 15) / average_char_size(description, font)))

    y = 10
    for i in range(len(lines)):
        draw.text((4, y), text=lines[i].upper(), font=font, fill="gray")
        y += font.getsize("Text")[1]

    coordinates = (860, 18)
    sheet.paste(box, coordinates)


def paste_special_abilities(abilities: List[SpecialAbility], sheet: Image):
    box_dim = (375, 330)
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

    coordinates = (580, 94)

    sheet.paste(box, coordinates)


def paste_xp_triggers(xp_triggers: List[str], sheet: Image):
    box_dim = (376, 102)
    box = Image.new('RGBA', box_dim, (220, 221, 222, 255))
    draw = ImageDraw.Draw(box)

    normal = ImageFont.truetype("verdanai.ttf", 9)

    y = 1
    for trigger in xp_triggers:

        lines = textwrap.wrap("- " + trigger,
                              width=int((box_dim[0]) / average_char_size(trigger, normal)))

        y_text = y
        for line in lines:
            draw.text((1, y_text), text=line, font=normal, fill="black")
            y_text += normal.getsize("Text")[1]

        y = y_text
        y += normal.getsize("Text")[1]

    coordinates = (578, 444)

    sheet.paste(box, coordinates)


def paste_contact(contact: NPC, crew_type: str, sheet: Image):
    # DB query
    contacts = query_crew_contacts()

    contact_full = Image.open("resources/images/ContactFull.png")
    contact_empty = Image.open("resources/images/ContactEmpty.png")

    box_dim = (200, 130)
    box = Image.new('RGBA', box_dim, (220, 221, 222, 255))
    draw = ImageDraw.Draw(box)

    font = ImageFont.truetype("verdanai.ttf", 10)

    y = 2

    for npc in contacts:
        x = 2
        if npc == contact:
            box.paste(contact_full, (x, y))
        else:
            box.paste(contact_empty, (x, y))

        x += 20

        npc_description = npc.name + ", " + npc.role
        lines = textwrap.wrap(npc_description,
                              width=int((box_dim[0] - 30) / average_char_size(npc_description, font)))
        for line in lines:
            draw.text((x, y), text=line, font=font, fill="black")
            y += font.getsize("Text")[1]

        y += font.getsize("Text")[1]

    coordinates = (580, 566)

    sheet.paste(box, coordinates)


def paste_crew_upgrades(owned_upgrades: List[Upgrade], sheet: Image):
    upgrades = owned_upgrades[:]

    paste_specific_upgrades(upgrades, sheet)
    paste_lair_upgrades(upgrades, sheet)
    paste_quality_upgrades(upgrades, sheet)
    paste_training_upgrades(upgrades, sheet)


def paste_upgrades_list(upgrades_list: List[Upgrade], queried_upgrades: List[Upgrade], draw: ImageDraw, box_x: int):
    font = ImageFont.truetype("verdana.ttf", 8)

    y = 0
    for specific_upgrade in queried_upgrades:
        owned_upgrade = find_upgrade(upgrades_list, specific_upgrade.name)
        tot_quality_to_print = specific_upgrade.quality
        if owned_upgrade is not None:
            if owned_upgrade.quality > specific_upgrade.quality:
                tot_quality_to_print = owned_upgrade.quality

            x = 5
            for i in range(tot_quality_to_print):
                fill = "white"
                if owned_upgrade.quality <= tot_quality_to_print:
                    fill = "red"
                draw.rectangle(((x, y), (x + 8, y + 8)), outline="black", fill=fill, width=1)
                x += 8
                if i != tot_quality_to_print - 1:
                    draw.rectangle(((x, y + 4), (x + 4, y + 4)), outline="black", width=1)
                    x += 4

            x += 4
        else:
            x = 5
            for i in range(specific_upgrade.quality):
                draw.rectangle(((x, y), (x + 8, y + 8)), outline="black", fill="white", width=1)
                x += 8
                if i != tot_quality_to_print - 1:
                    draw.rectangle(((x, y + 4), (x + 4, y + 4)), outline="black", fill="white", width=1)
                    x += 4

            x += 4

        lines = textwrap.wrap(specific_upgrade.name,
                              width=int(
                                  (box_x - tot_quality_to_print * 15) / average_char_size(specific_upgrade.name, font)))

        for line in lines:
            draw.text((x, y), text=line, font=font, fill="black")
            y += font.getsize("Text")[1]

        y += 10


def paste_specific_upgrades(upgrades: List[Upgrade], sheet: Image):
    specific_upgrades = [Upgrade("Assassin's Rigging (2 free load of weapons or gear)", 1),
                         Upgrade("Elite Skulks", 1),
                         Upgrade("Elite Thugs", 1),
                         Upgrade("Hardened (+1 Trauma box)", 3),
                         Upgrade("Ironhook Contacts (+1 Tier in prison)", 1)]

    box_dim = (189, 140)
    box = Image.new('RGBA', box_dim, (220, 221, 222, 255))
    draw = ImageDraw.Draw(box)

    paste_upgrades_list(upgrades, specific_upgrades, draw, box_dim[0])

    coordinates = (765, 565)
    sheet.paste(box, coordinates)


def paste_lair_upgrades(upgrades: List[Upgrade], sheet: Image):
    specific_upgrades = [Upgrade("Carriage (Vehicle)", 2),
                         Upgrade("Boat (Vehicle)", 2),
                         Upgrade("Hidden", 1),
                         Upgrade("Quarters", 1),
                         Upgrade("Secure", 2),
                         Upgrade("Vault", 2),
                         Upgrade("Workshop", 1)]

    box_dim = (120, 150)
    box = Image.new('RGBA', box_dim, (255, 255, 255, 255))
    draw = ImageDraw.Draw(box)

    paste_upgrades_list(upgrades, specific_upgrades, draw, box_dim[0])

    coordinates = (955, 580)
    sheet.paste(box, coordinates)


def paste_quality_upgrades(upgrades: List[Upgrade], sheet: Image):
    specific_upgrades = [Upgrade("Documents", 2),
                         Upgrade("Gear", 2),
                         Upgrade("Implements", 1),
                         Upgrade("Supplies", 1),
                         Upgrade("Tools", 2),
                         Upgrade("Weapons", 2)]

    box_dim = (90, 150)
    box = Image.new('RGBA', box_dim, (255, 255, 255, 255))
    draw = ImageDraw.Draw(box)

    paste_upgrades_list(upgrades, specific_upgrades, draw, box_dim[0])

    coordinates = (1080, 580)
    sheet.paste(box, coordinates)


def paste_training_upgrades(upgrades: List[Upgrade], sheet: Image):
    specific_upgrades = [Upgrade("Insight", 1),
                         Upgrade("Prowess", 1),
                         Upgrade("Resolve", 1),
                         Upgrade("Personal", 1),
                         Upgrade("Mastery", 4)]

    box_dim = (100, 110)
    box = Image.new('RGBA', box_dim, (255, 255, 255, 255))
    draw = ImageDraw.Draw(box)

    paste_upgrades_list(upgrades, specific_upgrades, draw, box_dim[0])

    coordinates = (955, 750)
    sheet.paste(box, coordinates)


def find_upgrade(upgrades_list: List[Upgrade], upgrade_to_search: str) -> Upgrade:
    for upgrade in upgrades_list:
        if upgrade.name == upgrade_to_search:
            return upgrade


def paste_crew_exp(exp: Playbook, sheet: Image):
    paste_playbook_exp(exp, sheet)
    paste_playbook_points(exp, sheet)


def paste_playbook_exp(playbook: Playbook, sheet: Image):
    notch_empty = Image.open("resources/images/NotchEmpty.png")
    notch_full = Image.open("resources/images/NotchFull.png")

    box_dim = (playbook.exp_limit * 9, 20)
    box = Image.new('RGBA', box_dim, (0, 0, 0, 255))

    exp_x = 0
    for i in range(playbook.exp):
        box.paste(notch_full, (exp_x, 0))
        exp_x += 9
    for i in range(playbook.exp_limit - playbook.exp):
        box.paste(notch_empty, (exp_x, 0))
        exp_x += 9

    coordinates = (936 - box_dim[0], 424)
    sheet.paste(box, coordinates)


def paste_playbook_points(playbook: Playbook, sheet: Image):
    font = ImageFont.truetype("verdanab.ttf", 14)

    box_dim = (20, 20)
    box = Image.new('RGBA', box_dim, (255, 255, 255, 255))
    draw = ImageDraw.Draw(box)

    # Useful rect around the box
    shape = ((0, 0), (box_dim[0] - 1, box_dim[1] - 1))
    draw.rectangle(shape, outline="black", width=1)

    draw.text((box_dim[0] / 2, box_dim[1] / 2), str(playbook.points), font=font, fill="black", anchor="mm")

    coordinates = (936, 424)
    sheet.paste(box, coordinates)


def paste_cohorts(cohorts: List[Cohort], sheet: Image):
    coordinates = (956, 6)
    stop = 4
    count = 0
    for cohort in cohorts:
        if count <= stop:
            paste_cohort_header(cohort, sheet, coordinates)
            paste_cohort_harm(cohort, sheet, coordinates)
            paste_cohort_types(cohort, sheet, coordinates)

            coordinates = list(coordinates)
            coordinates[1] += 136
            coordinates = tuple(coordinates)
            count += 1


def paste_cohort_header(cohort: Cohort, sheet: Image, coordinates: Tuple[int, int]):
    box_dim = (210, 15)
    box = Image.new('RGBA', box_dim, (0, 0, 0, 255))
    draw = ImageDraw.Draw(box)

    header_font = ImageFont.truetype("verdanab.ttf", 10)
    gang_expert_font = ImageFont.truetype("arial.ttf", 8)

    if cohort.elite:
        fill = "orange"
    else:
        fill = "white"
    draw.text((1, 0), "COHORT", fill=fill, font=header_font)

    x = 80
    y = 2
    draw.text((x - gang_expert_font.getsize("GANG")[0] - 2, y), "GANG", fill="white", font=gang_expert_font)
    draw.rectangle(((x, y), (x + 10, y + 10)), fill=(220, 221, 222, 255))
    if cohort.expert:
        fill = "white"
    else:
        fill = "red"
    draw.ellipse([(x + 1, y + 1), (x + 8, y + 8)], fill=fill, outline="black")

    x = 136
    y = 2
    draw.text((x - gang_expert_font.getsize("EXPERT")[0] - 2, y), "EXPERT", fill="white", font=gang_expert_font)
    draw.rectangle(((x, y), (x + 10, y + 10)), fill=(220, 221, 222, 255))
    if cohort.expert:
        fill = "red"
    else:
        fill = "white"
    draw.ellipse([(x + 1, y + 1), (x + 8, y + 8)], fill=fill, outline="black")

    x = 190
    y = 2
    draw.text((x - gang_expert_font.getsize("ARMOR")[0] - 2, y), "ARMOR", fill="white", font=gang_expert_font)
    draw.rectangle(((x, y), (x + 16, y + 10)), fill="white", outline=(220, 221, 222, 255))
    draw.text((x + 12 / 2, y), text=str(cohort.armor), fill="black", anchor="mm")

    sheet.paste(box, coordinates)


def paste_cohort_harm(cohort: Cohort, sheet: Image, coordinates: Tuple[int, int]):
    harm_empty = Image.open("resources/images/CohortHarmEmpty.png")
    harm_full = Image.open("resources/images/CohortHarmFull.png")

    box_dim = (210, 20)
    box = Image.new('RGBA', box_dim, (255, 255, 255, 255))
    draw = ImageDraw.Draw(box)

    font = ImageFont.truetype("arial.ttf", 9)

    status = ["WEAK", "IMPAIRED", "BROKEN", "DEAD"]

    x = 1
    for i in range(len(status)):
        draw.text((x, 1), status[i], fill="black", font=font)
        x += font.getsize(status[i])[0] + 2
        if i + 1 == cohort.harm:
            box.paste(harm_full, (x, 1))
        else:
            box.paste(harm_empty, (x, 1))
        x += 15

    sheet.paste(box, (coordinates[0], coordinates[1] + 15))


def paste_cohort_types(cohort: Cohort, sheet: Image, coordinates: Tuple[int, int]):
    box_dim = (210, 100)
    box = Image.new('RGBA', box_dim, (255, 255, 255, 255))
    draw = ImageDraw.Draw(box)

    type_font = ImageFont.truetype("comici.ttf", 12)
    title_font = ImageFont.truetype("verdanab.ttf", 12)

    shape = ((0, 0), (box_dim[0] - 1, box_dim[1] - 1))
    draw.rectangle(shape, outline="black", width=1)

    titles = ["TYPES:", "EDGES:", "FLAWS:"]
    contents = [cohort.type, cohort.edges, cohort.flaws]

    y = 1
    for i in range(len(titles)):
        x = 1
        draw.text((x, y), titles[i], fill="black", font=title_font)
        y += title_font.getsize("TEXT")[1] + 2
        for j in range(len(contents[i])):
            if j != len(contents[i]) - 1:
                draw.text((x, y), text=contents[i][j] + ",", fill="black", font=type_font)
            else:
                draw.text((x, y), text=contents[i][j], fill="black", font=type_font)
            x += type_font.getsize(contents[i][j])[0] + 4
        y += type_font.getsize("TEXT")[1] + 4

    sheet.paste(box, (coordinates[0], coordinates[1] + 35))


def paste_hunting_grounds(crew_type: str, sheet: Image):
    # query from DB
    crew_hg = query_hunting_grounds(crew_type=crew_type)

    hunting_grounds = crew_hg[0]
    for i in range(1, len(crew_hg)):
        hunting_grounds += ", " + crew_hg[i]

    box_dim = (370, 120)
    box = Image.new('RGBA', box_dim, (255, 255, 255, 255))
    draw = ImageDraw.Draw(box)

    font = ImageFont.truetype("timesi.ttf", 15)

    lines = textwrap.wrap(hunting_grounds, width=int((box_dim[0] - 15) / average_char_size(hunting_grounds, font)))

    y = 2
    for i in range(len(lines)):
        draw.text((4, y), text=lines[i].upper(), font=font, fill="black")
        y += font.getsize("Text")[1] * 2

    y = font.getsize("Text")[1] + 4
    for j in range(4):
        draw.rectangle(((4, y), (box_dim[0] - 5, y)), outline="gray", width=1)
        y += font.getsize("Text")[1] * 2

    coordinates = (575, 730)
    sheet.paste(box, coordinates)


def paste_prison_claims(p_claims: List[Claim], sheet: Image):
    paste_claims(p_claims, sheet, 50, 300, 5, "PRISON")
