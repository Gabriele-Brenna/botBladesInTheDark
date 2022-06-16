import json
import math
from typing import List, Union, Tuple, Dict

from bs4.element import Doctype
from bs4 import *

from component.Clock import Clock
from utility.FilesManager import path_finder
from utility.htmlFactory.HtmlParser import MyHTMLParser


class Journal:
    """
    Keeps track of what happens in the game by writing it in a text file.
    """

    def __init__(self, notes: List[str] = None, indentation: int = 0, lang: str = "ENG") -> None:
        if notes is None:
            notes = []
        self.notes = notes
        self.indentation = indentation
        with open(path_finder("{}.json".format(lang.upper())), 'r') as f:
            self.lang = json.load(f)["Journal"]
        self.log = BeautifulSoup("", 'html.parser')
        self.score_tag = None
        self.write_heading("Journal", self.log)

    def get_note(self, number: int):
        """
        Method used to get a note in a given position.

        :param number: is the position of the note. It's given starting from the most recent to the oldest one,
        meaning the note 1 is the last note written
        :return: the note in the given position.
        """
        notes = self.log.find_all(attrs={"class": "user"}, recursive=True)
        number = - number
        if len(notes) == 0 or number > len(notes):
            return None
        return notes[number]

    def read_note(self, number: int = 1) -> str:
        """
        Method used to get the text inside a note in a given position.

        :param number: position of the note
        :return: content of the note tag
        """
        note = self.get_note(number)
        return note.text

    def edit_note(self, new_note: str, number: int = 1):
        """
        Allows to change a specified note, depending on its position inside the list of description.

        :param new_note: is the new note that will be written
        :param number: is the position of the note. It's given starting from the most recent to the oldest one,
        meaning the note 1 is the last note written
        """
        note = self.get_note(number)
        if note:
            note.clear()
            note.append(new_note)

    def read_journal(self) -> bytes:
        """
        Gives the binary encoding of the Journal.

        :return: bytes used to create the html document of the Journal.
        """
        parser = MyHTMLParser()
        parser.feed(self.get_log_string())

        return bytes(parser.get_parsed_string(), 'UTF-8')

    def get_log_string(self) -> str:
        """
        Gets the string version of the log.

        :return: the str containing the journal's html source.
        """
        return str(self.log)

    def get_lang(self, method: str) -> dict:
        """
        Extracts the user's language preference dictionary.

        :param method: if not None the specific method lang dictionary is returned
        :return: a dict
        """
        return self.lang[method]

    def get_codex(self, game_name: str, info: Dict[str, List[Tuple]]) -> str:
        """
        Method used to get all the information contained in the database as html file.

        :param game_name: str representing the name of the game
        :param info: dictionary containing all the info about the database
        :return: the str containing the codex's html source
        """
        codex = BeautifulSoup("", "html.parser")
        self.write_heading("Codex", codex)

        body_tag = codex.select_one("body")
        body_tag.append(self.create_h1_tag("Codex - {}".format(game_name), log=codex))

        style = {"style": """
        margin: 1%;
        width: 98%;"""}

        for key in info:
            body_tag.append(self.create_h2_tag(key, log=codex))
            body_tag.append(self.create_table_tag(info[key], attrs=style, log=codex))

        return str(codex)

    def read_codex(self, game_name: str, info: Dict[str, List[Tuple]]) -> bytes:
        """
        Gives the binary encoding of the Codex.

        :param game_name: str representing the name of the game
        :param info: dictionary containing all the info about the database
        :return: bytes used to create the html document of the Codex.
        """
        parser = MyHTMLParser()
        parser.feed(self.get_codex(game_name, info))
        return bytes(parser.get_parsed_string(), 'UTF-8')

    def write_heading(self, title: str, log: BeautifulSoup):
        """
        Method used to write all the heading in the attribute journal representing the html file of the journal.

        :param title: str representing the title of the page
        :param log: represents the html file
        """
        doctype = Doctype('html')
        log.append(doctype)

        html_tag = log.new_tag("html", lang="en")

        head_tag = log.new_tag("head")
        html_tag.append(head_tag)

        meta_tag = log.new_tag("meta", charset="UTF-8")
        head_tag.append(meta_tag)

        head_tag.append(BeautifulSoup('''<link rel="preconnect" href="https://fonts.googleapis.com"> 
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin> 
        <link href="https://fonts.googleapis.com/css2?family=Merienda+One&family=Mochiy+Pop+One&family=Rye&family=Syne+Mono&family=Vast+Shadow&display=swap" rel="stylesheet">''',
                                      'html.parser'))

        title_tag = log.new_tag("title")
        title_tag.string = "Blades in The Dark - {}".format(title)
        head_tag.append(title_tag)

        style_tag = log.new_tag("style")

        with open(path_finder("Style.css"), 'r') as f:
            style_str = f.read()
        style_tag.append(style_str)

        head_tag.append(style_tag)

        log.append(html_tag)

        log.select_one("html").append(log.new_tag("body"))

    def create_title_tag(self, game_name: str):
        """
        Method used to write the title of the game in the attribute journal representing the html file of the journal.

        :param game_name: str representing the name of the game
        """
        placeholder = self.get_lang(self.write_title.__name__)
        title_tag = self.create_h1_tag(placeholder["0"].format(game_name))

        return title_tag

    def create_phase_tag(self, phase_name: str):
        """
        Method used to write a phase heading in the attribute journal representing the html file of the journal.

        :param phase_name: name of the phase
        :return: tag containing the name of the phase
        """
        return self.create_h4_tag(phase_name, {"class": "state"})

    def write_phase(self, new_state: int):
        """
        Method used to write new phase heading in the attribute journal representing the html file of the journal.
        """
        placeholder = self.get_lang(self.write_phase.__name__)
        h4_tag = self.create_phase_tag(placeholder[str(new_state)])

        self.log.select_one("body").append(h4_tag)

    def create_note_tag(self, title: str, text: str):
        """
        Method used to create and insert a div tag with class attribute set to "generalNotes".

        :param title: str representing the title of the notes
        :param text: str representing the actual notes
        :return: the div Tag
        """
        div_tag = self.create_div_tag({"class": "generalNotes"})

        div_tag.append(self.create_h2_tag(title))

        div_tag.append(self.create_p_tag(text, {"class": "user"}))

        return div_tag

    def create_fortune_roll_tag(self, pc: str, what: str, goal: str, outcome: int, notes: str):
        """
        Method used to create and insert a div tag with class attribute set to "fortuneRoll".

        :param pc: who does the fortune roll
        :param what: what do they roll
        :param goal: what is their goal
        :param outcome: what is the outcome of the roll
        :param notes: extra notes
        :return: the div Tag
        """
        placeholder = self.get_lang(self.write_fortune_roll.__name__)

        div_tag = self.create_div_tag(attrs={"class": "fortuneRoll",
                                             "style": "margin-left: {}%".format(str(self.get_indentation()))})

        div_tag.append(self.create_h2_tag(placeholder["0"]))

        div_tag.append(self.create_h4_tag(placeholder["1"]))

        div_tag.append(self.create_p_tag(placeholder["2"].format(pc, what)))

        div_tag.append(self.create_p_tag(placeholder["3"].format(goal)))

        div_tag.append(self.create_h4_tag(placeholder["4"]))

        div_tag.append(self.create_p_tag(placeholder["5"].format(outcome)))

        div_tag.append(self.create_p_tag(notes, {"class": "user"}))

        return div_tag

    def create_score_tag(self, title: str, category: str, plan_type: str, target: str, plan_details: str,
                         pc_load: List[Tuple[str, int]], outcome: Union[str, int], notes: str):
        """
        Method used to create and insert a div tag with class attribute set to "score".

        :param title: name of the score
        :param category: category of the score
        :param plan_type: type of the score's plan
        :param target: target of the score
        :param plan_details: details of the plan
        :param pc_load: list of tuples made of name of the pc and their load
        :param outcome: position of the engagement roll
        :param notes: extra notes
        :return: the div Tag
        """
        placeholder = self.get_lang(self.write_score.__name__)
        div_tag = self.create_div_tag({"class": "score",
                                       "style": "margin-left: {}%".format(self.get_indentation())})

        div_tag.append(self.create_h2_tag(placeholder["0"].format(title, category)))

        div_tag.append(self.create_h3_tag(placeholder["1"]))

        div_tag.append(self.create_p_tag(plan_type))

        div_tag.append(self.create_h3_tag(placeholder["8"]))

        div_tag.append(self.create_p_tag(target))

        div_tag.append(self.create_h3_tag(placeholder["2"]))

        div_tag.append(self.create_p_tag(plan_details))

        div_tag.append(self.create_h3_tag(placeholder["3"]))

        content = [(placeholder["4"], placeholder["5"])]
        for i in range(len(pc_load)):
            content.append((pc_load[i][0], str(pc_load[i][1])))

        div_tag.append(self.create_table_tag(content))

        div_tag.append(self.create_h3_tag(placeholder["6"]))

        lang_result = self.get_lang("results")["engagement"]
        for key in lang_result.keys():
            if str(outcome) in key:
                div_tag.append(self.create_p_tag(placeholder["7"].format(lang_result[key])))

        div_tag.append(self.create_p_tag(notes, {"class": "user"}))

        self.indentation += 1

        return div_tag

    def create_action_tag(self, pc: str, goal: str, action: str, position: str, effect: str,
                          outcome: Union[int, str], notes: str, participants: List[dict] = None,
                          cohort: str = None, assistants: List[str] = None, push: bool = False,
                          devils: str = None):
        """
        Method used to create and insert a div tag with class attribute set to "action".

        :param pc: who starts the action
        :param goal: goal of the action
        :param action: what will be rolled
        :param position: starting position of the action
        :param effect: effect of the action if successful
        :param outcome: outcome of the dice roll
        :param notes: extra notes
        :param participants: if it's a group action made with other players this is the list of their name. None otherwise
        :param cohort: if it's a group action made with a cohort this is the type of the cohort. None otherwise
        :param assistants: from whom the user got help
        :param push: True if the pc pushed themselves. False otherwise
        :param devils: if a devil's bargain has been made this is its description. None otherwise
        :return: the div Tag
        """
        placeholder = self.get_lang(self.write_action.__name__)
        div_tag = self.create_div_tag({"class": "action",
                                       "style": "margin-left: {}%".format(self.get_indentation())})

        if participants is not None or cohort is not None:
            div_tag.append(self.create_h2_tag(placeholder["12"]))
        else:
            div_tag.append(self.create_h2_tag(placeholder["0"]))

        div_tag.append(self.create_h4_tag(placeholder["1"]))

        div_tag.append(self.create_p_tag(placeholder["2"].format(pc, goal, action)))

        div_tag.append(self.create_p_tag(placeholder["3"].format(position, effect)))

        if push:
            div_tag.append(self.create_p_tag(placeholder["5"].format(pc)))
        if devils:
            div_tag.append(self.create_p_tag(placeholder["6"].format(pc, devils)))

        if assistants:
            div_tag.append(self.create_p_tag(placeholder["4"].format(" ".join(assistants))))

        if cohort is not None and participants is None:
            div_tag.append(self.create_p_tag(placeholder["10"].format(pc, cohort)))

        elif cohort is None and participants is not None:
            div_tag.append(self.create_h4_tag(placeholder["9"]))
            for p in participants:
                if p["push"]:
                    div_tag.append(self.create_p_tag(placeholder["5"].format(p["name"])))
                if "devil_bargain" in p:
                    div_tag.append(self.create_p_tag(placeholder["6"].format(p["name"], p["devil_bargain"])))
                div_tag.append(self.create_p_tag(placeholder["11"].format(p["name"], p["outcome"])))

        div_tag.append(self.create_h4_tag(placeholder["7"]))

        div_tag.append(self.create_p_tag(placeholder["8"].format(outcome)))

        try:
            lang = self.get_lang("results")["action"][position.lower()]
        except:
            lang = self.get_lang("results")["action"]["others"]

        for key in lang.keys():
            if str(outcome) in key:
                div_tag.append(self.create_p_tag(lang[key]))

        p_tag = self.log.new_tag("p")
        p_tag.string = notes
        div_tag.append(self.create_p_tag(notes, {"class": "user"}))

        return div_tag

    def create_end_score_tag(self, outcome: str, notes: str):
        """
        Method used to create and insert a div tag with class attribute set to "endScore".

        :param outcome: exposure of the score
        :param notes: extra notes
        :return: the div Tag
        """
        placeholder = self.get_lang(self.write_end_score.__name__)
        div_tag = self.create_div_tag({"class": "endScore"})

        div_tag.append(self.create_h3_tag(placeholder["0"].format(outcome)))

        div_tag.append(self.create_p_tag(notes, {"class": "user"}))

        self.indentation -= 1

        return div_tag

    def create_payoff_tag(self, amount: int, distributed: bool, notes: str):
        """
        Method used to create and insert a div tag with class attribute set to "payoff".

        :param amount: amount of money obtained during the score
        :param distributed: True if the coin are distributed among the players, False otherwise
        :param notes: extra notes about the payoff
        :return: the div Tag
        """
        placeholder = self.get_lang(self.write_payoff.__name__)
        div_tag = self.create_div_tag({"class": "payoff"})

        div_tag.append(self.create_h2_tag(placeholder["0"]))

        div_tag.append(self.create_h4_tag(placeholder["1"]))

        if distributed is not None:
            div_tag.append(self.create_p_tag(placeholder["2"].format(
                amount, placeholder[str(3 + int(distributed))]
            )))
        else:
            div_tag.append(self.create_p_tag(placeholder["2"].format(amount, placeholder["5"])))

        div_tag.append(self.create_p_tag(notes, {"class": "user"}))

        return div_tag

    def create_heat_tag(self, execution: str, exposure: str, famous_target: bool, hostile: bool, war: bool,
                        bodies: bool, heat: int, wanted: int):
        """
        Method used to create and insert a div tag with class attribute set to "heat".

        :param execution: how loud the score was executed
        :param exposure: type of exposure received
        :param famous_target: True if the target was famous, False otherwise
        :param hostile: True if the score was made in a hostile turf, False otherwise
        :param war: True if the crew is at war, False otherwise
        :param bodies: True if someone was killed, False otherwise
        :param heat: amount of heat received
        :param wanted: amount of wanted level received
        :return: the div Tag
        """
        placeholder = self.get_lang(self.write_heat.__name__)
        div_tag = self.create_div_tag({"class": "heat"})

        div_tag.append(self.create_h2_tag(placeholder["0"]))

        div_tag.append(self.create_p_tag(placeholder["1"].format(execution, exposure), ))

        if famous_target:
            div_tag.append(self.create_p_tag(placeholder["2"]))

        if hostile:
            div_tag.append(self.create_p_tag(placeholder["3"]))

        if war:
            div_tag.append(self.create_p_tag(placeholder["4"]))

        if bodies:
            div_tag.append(self.create_p_tag(placeholder["5"]))

        div_tag.append(self.create_p_tag(placeholder["6"].format(heat)))

        div_tag.append(self.create_p_tag(placeholder["7"].format(wanted)))

        return div_tag

    def create_entanglement_tag(self, name: str, description: str):
        """
        Method used to create and insert a div tag with class attribute set to "entanglement".

        :param name: name of the entanglement
        :param description: description of the entanglement
        :return: the div Tag
        """
        placeholder = self.get_lang(self.write_entanglement.__name__)
        div_tag = self.create_div_tag({"class": "entanglement"})

        div_tag.append(self.create_h2_tag(placeholder["0"]))

        div_tag.append(self.create_h4_tag(placeholder["1"]))

        div_tag.append(self.create_p_tag(name))

        div_tag.append(self.create_p_tag(description, {"class": "user"}))

        return div_tag

    def create_secret_entanglement_tag(self, name: str, description: str):
        """
        Method used to create and insert a div tag with class attribute set to "secretEntanglement".

        :param name: name of the secret entanglement
        :param description: description of the secret entanglement
        :return: the div Tag
        """
        placeholder = self.get_lang(self.write_secret_entanglement.__name__)
        div_tag = self.create_div_tag({"class": "secretEntanglement"})

        div_tag.append(self.create_h2_tag(placeholder["0"]))

        details_tag = self.create_details_tag()

        summary_tag = self.create_summary_tag(placeholder["1"])
        details_tag.append(summary_tag)

        details_tag.append(self.create_p_tag(name))

        details_tag.append(self.create_p_tag(description, {"class": "user"}))

        div_tag.append(details_tag)

        self.log.select_one("body").append(div_tag)

        return div_tag

    def create_acquire_asset_tag(self, pc: str, asset: str, quality: int, minimum_quality: int,
                                 outcome: Union[int, str], extra_quality: int, notes: str):
        """
        Method used to create and insert a div tag with class attribute set to "acquire_asset".

        :param pc: who does the downtime activity
        :param asset: the asset to acquire
        :param quality: quality obtained after the dice roll
        :param minimum_quality: minimum quality of the asset
        :param outcome: outcome of the roll
        :param extra_quality: by how much the quality is increased
        :param notes: extra notes
        :return: the div Tag
        """
        placeholders = self.get_lang(self.write_activity.__name__)["acquire_asset"]
        div_tag = self.create_div_tag({"class": "acquire_asset"})
        div_tag.append(self.create_h2_tag(placeholders["0"]))

        div_tag.append(self.create_p_tag(placeholders["1"].format(
            pc, asset, placeholders["2"].format(minimum_quality) if minimum_quality > -1 else ".")))

        div_tag.append(self.create_p_tag(placeholders["3"].format(outcome)))

        div_tag.append(self.create_p_tag(placeholders["4"].format(quality)))

        if extra_quality > 0:
            div_tag.append(self.create_p_tag(placeholders["5"].format(pc, quality+extra_quality)))

        if quality + extra_quality >= minimum_quality:
            div_tag.append(self.create_p_tag(placeholders["6"].format(pc)))
        else:
            div_tag.append(self.create_p_tag(placeholders["7"].format(pc)))

        div_tag.append(self.create_p_tag(notes, {"class": "user"}))

        return div_tag

    def create_long_term_project_tag(self, pc: str, clock: Clock, notes: str, tick: int, action: str):
        """
        Method used to create and insert a div tag with class attribute set to "long_term_project".

        :param action: action rolled by the pc
        :param tick: by how much the clock advances
        :param pc: who does the downtime activity
        :param clock: project clock
        :param notes: extra notes
        :return: the div Tag
        """
        placeholders = self.get_lang(self.write_activity.__name__)["long_term_project"]

        div_tag = self.create_div_tag({"class": ["long_term_project", "clock"]})

        one_tag = self.create_div_tag({"class": "one"})

        one_tag.append(self.create_h2_tag(placeholders["0"]))

        one_tag.append(self.create_p_tag(placeholders["1"].format(pc, clock.name.split("] ")[1])))

        one_tag.append(self.create_p_tag(placeholders["3"].format(
            pc, action.split(": ")[0], action.split(": ")[1], tick)))

        if clock.progress == clock.segments:
            one_tag.append(self.create_p_tag(placeholders["2"]))

        one_tag.append(self.create_p_tag(notes, {"class": "user"}))

        div_tag.append(one_tag)

        div_tag.append(self.create_clock_tag(clock))

        return div_tag

    def create_crafting_tag(self, pc: str, item: str, minimum_quality: int, quality: int, outcome: Union[int, str],
                            extra_quality: int, notes: str, item_description: str = None):
        """
        Method used to create and insert a div tag with class attribute set to "crafting".

        :param pc: who does the downtime activity
        :param item: item to craft
        :param item_description: description of the item
        :param minimum_quality: minimum quality of the item to craft
        :param quality: quality obtained after the dice roll
        :param outcome: outcome of the roll
        :param extra_quality: by how much the quality is increased
        :param notes: extra notes
        :return: the div Tag
        """
        placeholders = self.get_lang(self.write_activity.__name__)["crafting"]
        div_tag = self.create_div_tag({"class": "crafting"})
        div_tag.append(self.create_h2_tag(placeholders["0"]))

        div_tag.append(self.create_p_tag(placeholders["1"].format(
            pc, item, " ({})".format(item_description) if item_description else ".")))
        div_tag.append(self.create_p_tag(placeholders["2"].format(minimum_quality)))
        div_tag.append(self.create_p_tag(placeholders["3"].format(outcome)))

        if extra_quality > 0:
            div_tag.append(self.create_p_tag(placeholders["5"].format(pc, quality+extra_quality)))
        else:
            div_tag.append(self.create_p_tag(placeholders["4"].format(quality)))

        if quality + extra_quality >= minimum_quality:
            div_tag.append(self.create_p_tag(placeholders["7"].format(pc, item)))
        else:
            div_tag.append(self.create_p_tag(placeholders["8"].format(pc, item)))

        div_tag.append(self.create_p_tag(notes, {"class": "user"}))

        return div_tag

    def create_recover_tag(self, pc: str, segments: int, tick: int, notes: str, healer: str = None,
                           npc: str = None, cohort: str = None):
        """
        Method used to create and insert a div tag with class attribute set to "recover".

        :param pc: who does the downtime activity
        :param segments: total segments of the healing clock
        :param tick: advancement of the project's clock
        :param healer: if not None is the crew's member helping the pc out
        :param npc: if not None is the npc helping the pc out
        :param cohort: if not None is the cohort helping the pc out
        :param notes: extra notes
        :return: the div Tag
        """
        placeholders = self.get_lang(self.write_activity.__name__)["recover"]
        div_tag = self.create_div_tag({"class": "recover"})
        div_tag.append(self.create_h2_tag(placeholders["0"]))

        div_tag.append(self.create_p_tag(placeholders["1"].format(pc)))

        if healer or npc or cohort:
            if healer:
                div_tag.append(self.create_p_tag(placeholders["2"].format(pc, healer)))
            elif npc:
                div_tag.append(self.create_p_tag(placeholders["2"].format(pc, npc)))
            elif cohort:
                div_tag.append(self.create_p_tag(placeholders["2"].format(pc, cohort)))
        else:
            div_tag.append(self.create_p_tag(placeholders["3"].format(pc)))

        div_tag.append(self.create_p_tag(placeholders["4"].format(pc, tick, segments)))

        div_tag.append(self.create_p_tag(notes, {"class": "user"}))

        return div_tag

    def create_reduce_heat_tag(self, pc: str, action: str, outcome: Union[int, str], heat: int, notes):
        """
        Method used to create and insert a div tag with class attribute set to "reduce_heat".

        :param pc: who does the downtime activity
        :param action: method used by the pc to reduce the heat
        :param outcome: outcome of the roll
        :param heat: by how much is the heat reduced
        :param notes: extra notes
        :return: the div Tag
        """
        placeholders = self.get_lang(self.write_activity.__name__)["reduce_heat"]
        div_tag = self.create_div_tag({"class": "reduce_heat"})
        div_tag.append(self.create_h2_tag(placeholders["0"]))

        div_tag.append(self.create_p_tag(placeholders["1"].format(pc, action)))
        div_tag.append(self.create_p_tag(placeholders["2"].format(outcome)))
        div_tag.append(self.create_p_tag(placeholders["3"].format(pc, heat)))

        div_tag.append(self.create_p_tag(notes, {"class": "user"}))

        return div_tag

    def create_train_tag(self, pc: str, attribute: str, points: int, notes: str):
        """
        Method used to create and insert a div tag with class attribute set to "train".

        :param pc: who does the downtime activity
        :param attribute: what has been trained
        :param points: amount of the xp gained
        :param notes: extra notes
        :return: the div Tag
        """
        placeholders = self.get_lang(self.write_activity.__name__)["train"]
        div_tag = self.create_div_tag({"class": "train"})

        div_tag.append(self.create_h2_tag(placeholders["0"]))

        div_tag.append(self.create_p_tag(placeholders["1"].format(pc, attribute, points)))

        div_tag.append(self.create_p_tag(notes, {"class": "user"}))

        return div_tag

    def create_indulge_vice_tag(self, pc: str, outcome: Union[int, str],
                                notes: str, brag: str = None, lost: str = None, tapped: str = None,
                                trouble: bool = False):
        """
        Method used to create and insert a div tag with class attribute set to "indulge_vice".

        :param pc: who does the downtime activity
        :param outcome: outcome of the roll
        :param notes: extra notes
        :param brag: if not None how the pc overindulges
        :param lost: if not None how the pc overindulges
        :param tapped: if not None how the pc overindulges
        :param trouble: if not None how the pc overindulges
        :return: the div Tag
        """
        placeholders = self.get_lang(self.write_activity.__name__)["indulge_vice"]
        div_tag = self.create_div_tag({"class": "indulge_vice"})

        div_tag.append(self.create_h2_tag(placeholders["0"]))
        div_tag.append(self.create_p_tag(placeholders["1"].format(pc)))
        div_tag.append(self.create_p_tag(placeholders["2"].format(outcome)))
        if isinstance(outcome, str):
            amount = placeholders["CRIT"]
        else:
            amount = outcome
        div_tag.append(self.create_p_tag(placeholders["3"].format(pc, amount)))

        attr = [brag, lost, tapped]
        for i in range(len(attr)):
            if attr[i]:
                div_tag.append(self.create_p_tag(placeholders["4"].format(pc, placeholders[str(5+i)].format(attr[i]))))

        if trouble:
            div_tag.append(self.create_p_tag(placeholders["4"].format(pc, placeholders["8"])))

        div_tag.append(self.create_p_tag(notes, {"class": "user"}))

        return div_tag

    def create_help_cohort_tag(self, pc: str, cohort: str, notes: str, harm: str = None):
        """
        Method used to create and insert a div tag with class attribute set to "help_cohort".

        :param pc: who does the downtime activity
        :param cohort: what cohort the pc will help
        :param notes: extra notes
        :param harm: if not None is the harm the cohort now has
        :return: the div Tag
        """
        placeholders = self.get_lang(self.write_activity.__name__)["help_cohort"]
        div_tag = self.create_div_tag({"class": "help_cohort"})
        div_tag.append(self.create_h2_tag(placeholders["0"]))

        div_tag.append(self.create_p_tag(placeholders["1"].format(pc, cohort)))
        if harm:
            div_tag.append(self.create_p_tag(placeholders["2"].format(harm)))
        else:
            div_tag.append(self.create_p_tag(placeholders["3"]))

        div_tag.append(self.create_p_tag(notes, {"class": "user"}))

        return div_tag

    def create_replace_cohort_tag(self, pc: str, cohort: str, notes: str):
        """
        Method used to create and insert a div tag with class attribute set to "replace_cohort".

        :param pc: who does the downtime activity
        :param cohort: new cohort the pc will have
        :param notes: extra notes
        :return: the div Tag
        """
        placeholders = self.get_lang(self.write_activity.__name__)["replace_cohort"]
        div_tag = self.create_div_tag({"class": "replace_cohort"})
        div_tag.append(self.create_h2_tag(placeholders["0"]))

        div_tag.append(self.create_p_tag(placeholders["1"].format(pc, cohort)))

        div_tag.append(self.create_p_tag(notes, {"class": "user"}))

        return div_tag

    def create_add_claim_tag(self, prison: bool, name: str):
        """
        Method used to create and insert a div tag with class attribute set to "addClaim".

        :param prison: True if the new claim is a lair claim, False if it's a prison claim
        :param name: name of the new claim
        :return: the div Tag
        """
        placeholder = self.get_lang(self.write_add_claim.__name__)
        div_tag = self.create_div_tag({"class": "addClaim",
                                       "style": "margin-left: {}%".format(self.get_indentation())})

        div_tag.append(self.create_h4_tag(placeholder["0"]))

        div_tag.append(self.create_p_tag(placeholder["1"].format(placeholder[str(2 + prison)], name)))

        return div_tag

    def create_incarceration_tag(self, pc: str, outcome: Union[str, int], notes: str):
        """
        Method used to create and insert a div tag with class attribute set to "incarceration".

        :param pc: who is going to jail
        :param outcome: what he rolls
        :param notes: extra notes
        :return: the div Tag
        """
        placeholder = self.get_lang(self.write_incarceration.__name__)
        div_tag = self.create_div_tag({"class": "incarceration"})

        div_tag.append(self.create_h2_tag(placeholder["0"]))

        div_tag.append(self.create_p_tag(placeholder["1"].format(pc)))

        div_tag.append(self.create_p_tag(placeholder["2"].format(outcome)))

        if isinstance(outcome, int):
            if 0 < outcome < 4:
                div_tag.append(self.create_p_tag(placeholder["6"]))
            elif 3 < outcome < 6:
                div_tag.append(self.create_p_tag(placeholder["5"]))
            elif outcome == 6:
                div_tag.append(self.create_p_tag(placeholder["4"]))
        else:
            div_tag.append(self.create_p_tag(placeholder["3"]))

        div_tag.append(self.create_p_tag(notes, {"class": "user"}))

        return div_tag

    def create_flashback_tag(self, pc: str, goal: str, stress: int, entail: bool = None):
        """
        Method used to create and insert a div tag with class attribute set to "flashback".

        :param pc: who does the flashback
        :param goal: goal of the flashback
        :param stress: amount of stress gained
        :param entail: what the flashback entails
        """
        placeholder = self.get_lang(self.write_flashback.__name__)
        div_tag = self.create_div_tag({"class": "flashback",
                                       "style": "margin-left: {}%".format(self.get_indentation())})

        div_tag.append(self.create_h2_tag(placeholder["0"]))

        div_tag.append(self.create_p_tag(placeholder["1"].format(pc, goal)))

        div_tag.append(self.create_p_tag(placeholder["2"].format(stress)))

        if entail is not None:
            div_tag.append(self.create_p_tag(placeholder["3"].format(placeholder[str(entail)])))
        else:
            div_tag.append(self.create_p_tag(placeholder["4"]))

        return div_tag

    def create_resistance_roll_tag(self, pc: str, description: str, damage: str, attribute: str, roll: Union[str, int],
                                   notes: str, stress: int = 0):
        """
        Method used to create and insert a div tag with class attribute set to "resistanceRoll".

        :param damage: if the damage will be reduced or avoided
        :param notes: extra notes
        :param pc: who is doing the resistance roll
        :param description: why the user is doing the resistance roll
        :param attribute: what attribute is rolling
        :param roll: roll of the dice
        :param stress: amount of stress gained
        :return: the div Tag
        """
        placeholder = self.get_lang(self.write_resistance_roll.__name__)
        div_tag = self.create_div_tag({"class": "resistanceRoll",
                                       "style": "margin-left: {}%".format(self.get_indentation())})

        div_tag.append(self.create_h2_tag(placeholder["0"]))

        div_tag.append(self.create_p_tag(placeholder["1"].format(
            pc, description)))

        div_tag.append(self.create_p_tag(placeholder["5"].format(damage)))

        if stress > 0:
            div_tag.append(self.create_p_tag(placeholder["2"].format(pc, attribute, roll,
                                                                     placeholder["3"].format(stress))))
        elif stress < 0:
            div_tag.append(self.create_p_tag(placeholder["2"].format(pc, attribute, roll,
                                                                     placeholder["4"].format(-stress))))
        else:
            div_tag.append(self.create_p_tag(placeholder["2"].format(pc, attribute, roll, placeholder["6"])))

        div_tag.append(self.create_p_tag(notes, {"class": "user"}))

        return div_tag

    def create_clock_tag(self, clock: Clock):
        """
        Method used to create a div tag used to represent a clock.

        :param clock: clock to represent
        :return: the div tag
        """
        divider_size = 4

        black = "black {}deg {}deg"
        white = "white {}deg {}deg"
        red = "red {}deg {}deg"
        conic_gradient = ""

        segment_size = int((360 - (divider_size * clock.segments)) / clock.segments)
        count = -2
        for i in range(clock.segments):
            next_count = count + divider_size
            conic_gradient += white.format(count, next_count) + ", "

            count = next_count + segment_size
            if i < clock.progress:
                conic_gradient += red.format(next_count, count) + ", "
            else:
                conic_gradient += black.format(next_count, count) + ", "

        conic_gradient += "white 0"

        style = "background-image: conic-gradient({});".format(conic_gradient)

        clock_tag = self.create_div_tag({"class": "piechart", "style": style})

        return clock_tag

    def create_clock(self, pc: str, new_clock: Clock, old_clock: Clock = None):
        """
        Method used to create and insert a div tag with class attribute set to "clock".

        :param pc: who creates the clock
        :param new_clock: new clock to represent with the div tag
        :param old_clock: old clock used to compare with the new one to know with sentence to use in the paragraph
        :return: the div Tag
        """

        placeholder = self.get_lang(self.write_clock.__name__)

        one_tag = self.create_div_tag({"class": "one"})

        if old_clock is None:
            p_tag = self.create_p_tag(placeholder["0"].format(pc, new_clock.name))
            one_tag.append(p_tag)
        else:
            if new_clock.segments != old_clock.segments:
                p_tag = self.create_p_tag(placeholder["1"].format(pc, new_clock.name))
                one_tag.append(p_tag)
            if new_clock.progress != old_clock.progress:
                p_tag = self.create_p_tag(placeholder["2"].format(pc, new_clock.name,
                                                                  (new_clock.progress - old_clock.progress)))
                one_tag.append(p_tag)
            if new_clock.segments == new_clock.progress:
                p_tag = self.create_p_tag(placeholder["3"].format(pc, new_clock.name))
                one_tag.append(p_tag)

        div_tag = self.create_div_tag({"class": "clock"})
        div_tag.append(one_tag)

        div_tag.append(self.create_clock_tag(new_clock))

        return div_tag

    def create_armor_use_tag(self, pc: str, armor_type: str, notes: str):
        """
        Method used to create and insert a div tag with class attribute set to "armor".

        :param pc: who uses the armor
        :param armor_type: type of the armor
        :param notes: extra notes
        :return: the div Tag
        """
        placeholders = self.get_lang(self.write_armor_use.__name__)

        div_tag = self.create_div_tag({"class": "armor",
                                       "style": "margin-left: {}%".format(self.get_indentation())})

        div_tag.append(self.create_h2_tag(placeholders["0"]))

        div_tag.append(self.create_p_tag(placeholders["1"].format(pc, armor_type)))

        div_tag.append(self.create_p_tag(notes, {"class": "user"}))

        return div_tag

    def create_use_item_tag(self, pc: str, item_name: str, notes: str):
        """
        Method used to create and insert a div tag with class attribute set to "useItem".

        :param pc: who uses the item
        :param item_name: name of the item
        :param notes: extra notes
        :return: the div Tag
        """

        placeholders = self.get_lang(self.write_use_item.__name__)

        div_tag = self.create_div_tag({"class": "useItem",
                                       "style": "margin-left: {}%".format(self.get_indentation())})

        div_tag.append(self.create_h2_tag(placeholders["0"]))

        div_tag.append(self.create_p_tag(placeholders["1"].format(pc, item_name, notes)))

        return div_tag

    def create_end_downtime_tag(self):
        """
        Method used to create and insert a div tag with class attribute set to "endDowntime".

        :return: the div Tag
        """
        placeholders = self.get_lang(self.write_end_downtime.__name__)

        div_tag = self.create_div_tag({"class": "endDowntime"})

        div_tag.append(self.create_h2_tag(placeholders["0"]))

        div_tag.append(self.create_p_tag(placeholders["1"]))

        return div_tag

    def create_change_vice_purveyor_tag(self, pc: str, new_purveyor: str):
        """
        Method used to create and insert a div tag with class attribute set to "changeVicePurveyor".

        :param pc: is the pc of interest.
        :param new_purveyor: is the new purveyor of the pc.
        :return: the div Tag
        """
        placeholders = self.get_lang(self.write_change_vice_purveyor.__name__)

        div_tag = self.create_div_tag({"class": "changeVicePurveyor"})

        div_tag.append(self.create_h2_tag(placeholders["0"]))

        div_tag.append(self.create_p_tag(placeholders["1"].format(pc, new_purveyor)))

        return div_tag

    def create_pc_migration_tag(self, pc: str, migration_pc: str):
        """
        Method used to create and insert a div tag with class attribute set to "pcMigration".

        :param pc: is the pc of interest.
        :param migration_pc: is the new type of the pc.
        :return: the div tag.
        """

        placeholders = self.get_lang(self.write_pc_migration.__name__)

        div_tag = self.create_div_tag({"class": "pcMigration"})

        div_tag.append(self.create_h2_tag(placeholders["0"]))

        div_tag.append(self.create_p_tag(placeholders["1"].format(pc, migration_pc)))

        return div_tag

    def create_change_pc_class_tag(self, pc: str, new_class: str):
        """
        Method used to create and insert a div tag with class attribute set to "changeClass".

        :param pc: is the pc of interest.
        :param new_class: is the new class of the pc.
        :return: the div tag.
        """

        placeholders = self.get_lang(self.write_change_pc_class.__name__)

        div_tag = self.create_div_tag({"class": "changeClass"})

        div_tag.append(self.create_h2_tag(placeholders["0"]))

        div_tag.append(self.create_p_tag(placeholders["1"].format(pc, new_class)))

        return div_tag

    def create_retire_tag(self, pc: str, description: str, choice: str):
        """
        Method used to create and insert a div tag with class attribute set to "retire".

        :param pc: is the pc of interest.
        :param description: is the description of the death or retirement.
        :param choice: if the pcs dies or retire
        :return: the div Tag
        """
        placeholders = self.get_lang(self.write_retire.__name__)

        div_tag = self.create_div_tag({"class": "retire",
                                       "style": "margin-left: {}%".format(self.get_indentation())})

        div_tag.append(self.create_h2_tag(placeholders[choice.lower()]["0"]))

        div_tag.append(self.create_p_tag(placeholders[choice.lower()]["1"].format(pc)))

        div_tag.append(self.create_p_tag(description, {"class": "user"}))

        return div_tag

    def create_end_game_tag(self, notes: str):
        """
        Method used to create and insert a div tag with class attribute set to "endGame".

        :param notes: description of the end of the game
        :return: the div Tag
        """
        placeholders = self.get_lang(self.write_end_game.__name__)

        div_tag = self.create_div_tag({"class": "endGame"})

        div_tag.append(self.create_h2_tag(placeholders["0"]))

        div_tag.append(self.create_p_tag(notes, {"class": "user"}))

        div_tag.append(self.create_h3_tag(placeholders["1"], {"style": "text-align: center"}))

        return div_tag

    def get_indentation(self) -> int:
        """
        Method used to get the percentage indentation based on the value of the attribute indentation

        :return: int representing the percentage indentation
        """
        if self.indentation != 0:
            return int(5 * (math.log(self.indentation) + 1)) + 1
        return 1

    def create_div_tag(self, attrs: dict, log: BeautifulSoup = None):
        """
        Method used to create a "div" tag.

        :param attrs: attributes of the div tag
        :param log: the log representing the html file
        :return: a "div" Tag
        """
        if log is None:
            log = self.log
        return log.new_tag("div", attrs=attrs)

    def create_h1_tag(self, content: str, attrs: dict = None, log: BeautifulSoup = None):
        """
        Method used to create a "h1" tag.

        :param content: content of the "h1" tag
        :param attrs: attributes of the h1 tag. If there are no attributes is set to None
        :param log: the log representing the html file
        :return: a "h1" Tag
        """
        if log is None:
            log = self.log
        if attrs:
            h1_tag = log.new_tag("h1", attrs=attrs)
        else:
            h1_tag = log.new_tag("h1")
        h1_tag.append(BeautifulSoup(content, 'html.parser'))
        return h1_tag

    def create_h2_tag(self, content: str, attrs: dict = None, log: BeautifulSoup = None):
        """
        Method used to create a "h2" tag

        :param content: content of the "h2" tag
        :param attrs: attributes of the h2 tag. If there are no attributes is set to None
        :param log: the log representing the html file
        :return: a "h2" Tag
        """
        if log is None:
            log = self.log
        if attrs:
            h2_tag = log.new_tag("h2", attrs=attrs)
        else:
            h2_tag = log.new_tag("h2")
        h2_tag.append(BeautifulSoup(content, 'html.parser'))
        return h2_tag

    def create_h3_tag(self, content: str, attrs: dict = None, log: BeautifulSoup = None):
        """
        Method used to create a "h3" tag.

        :param content: content of the "h3" tag
        :param attrs: attributes of the h3 tag. If there are no attributes is set to None
        :param log: the log representing the html file
        :return: a "h3" Tag
        """
        if log is None:
            log = self.log
        if attrs:
            h3_tag = log.new_tag("h3", attrs=attrs)
        else:
            h3_tag = log.new_tag("h3")
        h3_tag.append(BeautifulSoup(content, 'html.parser'))
        return h3_tag

    def create_h4_tag(self, content: str, attrs: dict = None, log: BeautifulSoup = None):
        """
        Method used to create a "h4" tag.

        :param content: content of the h4 tag
        :param attrs: attributes of the h4 tag. If there are no attributes is set to None
        :param log: the log representing the html file
        :return: a "h4" Tag
        """
        if log is None:
            log = self.log
        if attrs:
            h4_tag = log.new_tag("h4", attrs=attrs)
        else:
            h4_tag = log.new_tag("h4")
        h4_tag.append(BeautifulSoup(content, 'html.parser'))
        return h4_tag

    def create_p_tag(self, content: str, attrs: dict = None, log: BeautifulSoup = None):
        """
        Method used to create a "p" tag.

        :param content: content of the p tag
        :param attrs: attributes of the p tag. If there are no attributes is set to None
        :param log: the log representing the html file
        :return: a "p" Tag
        """
        if log is None:
            log = self.log
        if attrs:
            p_tag = log.new_tag("p", attrs=attrs)
        else:
            p_tag = log.new_tag("p")
        p_tag.append(BeautifulSoup(content, 'html.parser'))
        return p_tag

    def create_details_tag(self, attrs: dict = None, log: BeautifulSoup = None):
        """
        Method used to create a "details" tag.

        :param attrs: attributes of the details tag. If there are no attributes is set to None
        :param log: the log representing the html file
        :return: a "details" Tag
        """
        if log is None:
            log = self.log
        if attrs:
            d_tag = log.new_tag("details", attrs=attrs)
        else:
            d_tag = log.new_tag("details")
        return d_tag

    def create_summary_tag(self, content: str, attrs: dict = None, log: BeautifulSoup = None):
        """
        Method used to create a "summary" tag.

        :param content: content of the summary tag
        :param attrs: attributes of the summary tag. If there are no attributes is set to None
        :param log: the log representing the html file
        :return: a "summary Tag
        """
        if log is None:
            log = self.log
        if attrs:
            s_tag = log.new_tag("summary", attrs=attrs)
        else:
            s_tag = log.new_tag("summary")
        s_tag.append(BeautifulSoup(content, 'html.parser'))
        return s_tag

    def create_table_tag(self, content: List[Tuple], attrs: dict = None, log: BeautifulSoup = None):
        """
        Method used to create a "table" tag.

        :param content: content of the table tag
        :param attrs: attributes of the table tag. If there are no attributes is set to None
        :param log: the log representing the html file
        :return: a table tag
        """
        if log is None:
            log = self.log
        if attrs is not None:
            table_tag = log.new_tag("table", attrs=attrs)
        else:
            table_tag = log.new_tag("table", attrs={"style": "margin-left: 125px;"})
        tr_tag = log.new_tag("tr")
        for i in range(len(content[0])):
            tr_tag.append(self.create_th_tag(content[0][i], log))
        table_tag.append(tr_tag)
        for i in range(1, len(content)):
            tr_tag = log.new_tag("tr")
            for j in range(len(content[i])):
                if content[i][j] is None:
                    tr_tag.append(self.create_td_tag("", log))
                elif isinstance(content[i][j], bool):
                    if content[i][j]:
                        tr_tag.append(self.create_td_tag("*", log))
                    else:
                        tr_tag.append(self.create_td_tag("", log))
                elif isinstance(content[i][j], int):
                    tr_tag.append(self.create_td_tag(str(content[i][j]), log))
                else:
                    tr_tag.append(self.create_td_tag(content[i][j], log))
            table_tag.append(tr_tag)
        return table_tag

    def create_th_tag(self, content: str, log: BeautifulSoup):
        """
        Method used to create a "th" tag.

        :param content: str representing the content of the th tag
        :param log: the log representing the html file
        :return: a "th" tag
        """
        th_tag = log.new_tag("th")
        th_tag.append(BeautifulSoup(content, 'html.parser'))
        return th_tag

    def create_td_tag(self, content: str, log: BeautifulSoup):
        """
        Method used to create a "td" tag.

        :param content: str representing the content of the td tag
        :param log: the log representing the html file
        :return: a "td" tag
        """
        td_tag = log.new_tag("td")
        td_tag.append(BeautifulSoup(content, 'html.parser'))
        return td_tag

    def write_general(self, tag):
        """
        Method used to write a tag inside the html file of the journal.

        :param tag: tag to write
        """
        if self.score_tag is not None:
            temp_child = self.score_tag.find("div", {"class": "endScore"}, recursive=False)
            if temp_child is None:
                self.score_tag.append(tag)
            else:
                self.score_tag.parent.append(tag)
        else:
            self.log.select_one("body").append(tag)

    def write_title(self, game_name: str):
        """
        Method used to write the title of the game in the attribute journal representing the html file of the journal.

        :param game_name: str representing the name of the game
        """
        self.log.select_one("body").append(self.create_title_tag(game_name))

    def write_note(self, title: str, text: str):
        """
        Method used to write general notes in the attribute journal representing the html file of the journal.

        :param title: str representing the title of the notes
        :param text: str representing the actual notes
        """
        tag = self.create_note_tag(title, text)

        self.write_general(tag)

    def write_fortune_roll(self, pc: str, what: str, goal: str, outcome: int, notes: str):
        """
        Method used to write a fortune roll in the attribute journal representing the html file of the journal.

        :param pc: who does the fortune roll
        :param what: what do they roll
        :param goal: what is their goal
        :param outcome: what is the exposure of the roll
        :param notes: extra notes
        """
        tag = self.create_fortune_roll_tag(pc, what, goal, outcome, notes)

        self.write_general(tag)

    def write_score(self, title: str, category: str, plan_type: str, target: str, plan_details: str,
                    pc_load: List[Tuple[str, int]], outcome: Union[str, int], notes: str):
        """
        Method used to write a score in the attribute journal representing the html file of the journal.

        :param title: name of the score
        :param category: category of the score
        :param plan_type: type of the score's plan
        :param target: the target of the score
        :param plan_details: details of the plan
        :param pc_load: list of tuples made of name of the pc and their load
        :param outcome: position of the engagement roll
        :param notes: extra notes
        """
        tag = self.create_score_tag(title, category, plan_type, target, plan_details, pc_load, outcome, notes)

        self.write_general(tag)

        self.score_tag = tag

    def write_action(self, pc: str, goal: str, action: str, position: str, effect: str, outcome: Union[int, str],
                     notes: str, participants: List[dict] = None, cohort: str = None, assistants: List[str] = None,
                     push: bool = False, devil_bargain: str = None):
        """
        Method used to write an action outcome in the attribute journal representing the html file of the journal.

        :param pc: who does the action roll
        :param goal: goal of the action roll
        :param action: what will the character do
        :param position: starting position of the action
        :param effect: effect of the action of successful
        :param outcome: result of the dice roll
        :param notes: extra notes
        :param participants: if it's a group action made with other players this is the list of their name. None otherwise
        :param cohort: if it's a group action made with a cohort this is the type of the cohort. None otherwise
        :param assistants: from whom the user got help
        :param push: if the user push themselves
        :param devil_bargain: what deal the user made
        """
        tag = self.create_action_tag(pc, goal, action, position, effect, outcome, notes, participants, cohort,
                                     assistants, push, devil_bargain)

        self.write_general(tag)

    def write_end_score(self, outcome: str, notes: str):
        """
        Method used to write the end of the score in the attribute journal representing the html file of the journal.

        :param outcome: exposure of the score
        :param notes: extra notes
        """
        tag = self.create_end_score_tag(outcome, notes)

        self.write_general(tag)

        self.score_tag = self.score_tag.parent

    def write_payoff(self, amount: int, notes: str, distributed: bool = None):
        """
        Method used to write the payoff in the attribute journal representing the html file of the journal.

        :param amount: amount of money obtained during the score
        :param distributed: True if the coin are distributed among the players, False otherwise
        :param notes: extra notes about the payoff
        :return:
        """
        tag = self.create_payoff_tag(amount, distributed, notes)

        self.write_general(tag)

    def write_heat(self, score_nature: str, famous_target: bool, hostility: bool, war: bool,
                   bodies: bool, total_heat: int, wanted: int):
        """
        Method used to write the payoff in the attribute journal representing the html file of the journal.

        :param score_nature: how loud the score was executed
        :param famous_target: True if the target was famous, False otherwise
        :param hostility: True if the score was made in a hostile turf, False otherwise
        :param war: True if the crew is at war, False otherwise
        :param bodies: True if someone was killed, False otherwise
        :param total_heat: amount of heat received
        :param wanted: amount of wanted level received
        """
        execution, exposure = score_nature.split(", ")
        tag = self.create_heat_tag(execution, exposure, famous_target, hostility, war, bodies, total_heat, wanted)

        self.write_general(tag)

    def write_entanglement(self, name: str, description: str):
        """
        Method used to write the entanglement in the attribute journal representing the html file of the journal.

        :param name: name of the entanglement
        :param description: description of the entanglement
        """
        tag = self.create_entanglement_tag(name, description)

        self.write_general(tag)

    def write_secret_entanglement(self, name: str, description: str):
        """
        Method used to write a secret entanglement in the attribute journal representing the html file of the journal.

        :param name: name of the secret entanglement
        :param description: description of the secret entanglement
        """
        tag = self.create_secret_entanglement_tag(name, description)

        self.write_general(tag)

    def write_activity(self, activity_dict: dict):
        """
        Method used to write a downtime activity in the attribute journal representing the html file of the journal.

        :param activity_dict: a dictionary containing the information necessary to call the right method
        """
        method_dict = {'acquire_asset': 'create_acquire_asset_tag', 'crafting': 'create_crafting_tag',
                       'long_term_project': 'create_long_term_project_tag', 'recover': 'create_recover_tag',
                       'reduce_heat': 'create_reduce_heat_tag', 'train': 'create_train_tag',
                       'indulge_vice': 'create_indulge_vice_tag', 'help_cohort': 'create_help_cohort_tag',
                       'replace_cohort': 'create_replace_cohort_tag'}
        method_to_call = getattr(self, method_dict[activity_dict["activity"]])
        activity_dict.pop("activity")
        tag = method_to_call(**activity_dict)

        self.write_general(tag)

    def write_add_claim(self, prison: bool, name: str, description: str):
        """
        Method used to write add claim in the attribute journal representing the html file of the journal.

        :param description: description of the claim
        :param prison: True if the new claim is a lair claim, False if it's a prison claim
        :param name: name of the new claim
        """
        tag = self.create_add_claim_tag(prison, name+" ("+description+")")

        self.write_general(tag)

    def write_incarceration(self, pc: str, outcome: Union[str, int], notes: str):
        """
        Method used to write the incarceration in the attribute journal representing the html file of the journal.

        :param pc: who is going to jail
        :param outcome: what he rolls
        :param notes: extra notes
        """
        tag = self.create_incarceration_tag(pc, outcome, notes)

        self.write_general(tag)

    def write_flashback(self, pc: str, goal: str, stress: int, entail: bool = None):
        """
        Method used to write the flashback in the attribute journal representing
        the html file of the journal.

        :param pc: who does the flashback
        :param goal: goal of the flashback
        :param stress: amount of stress gained
        :param entail: what the flashback entails
        """
        tag = self.create_flashback_tag(pc, goal, stress, entail)

        self.write_general(tag)

    def write_resistance_roll(self, pc: str, description: str, damage: str, attribute: str, outcome: Union[str, int],
                              notes: str, stress: int = 0):
        """
        Method used to write a resistance roll in the attribute journal representing the html file of the journal.

        :param damage: if the damage will be reduced or avoided
        :param notes: extra notes
        :param pc: who is doing the resistance roll
        :param description: why the user is doing the resistance roll
        :param attribute: what attribute is rolling
        :param outcome: roll of the dice
        :param stress: amount of stress gained
        """
        tag = self.create_resistance_roll_tag(pc, description, damage, attribute, outcome, notes, stress)

        self.write_general(tag)

    def write_clock(self, pc: str, new_clock: Clock, old_clock: Clock = None):
        """
        Method used to write a clock in the attribute journal representing the html file of the journal.

        :param pc: who creates the clock
        :param new_clock: new clock to represent with the div tag
        :param old_clock: old clock used to compare with the new one to know with sentence to use in the paragraph
        """
        tag = self.create_clock(pc, new_clock, old_clock)

        self.write_general(tag)

    def write_armor_use(self, pc: str, armor_type: str, notes: str):
        """
        Method used to write the use of an armor in the attribute journal representing the html file of the journal.

        :param pc: who uses the armor
        :param armor_type: type of the armor used
        :param notes: extra notes
        """
        tag = self.create_armor_use_tag(pc, armor_type, notes)

        self.write_general(tag)

    def write_use_item(self, pc: str, item_name: str, notes: str):
        """
        Method used to write the use of an item in the attribute journal representing the html file of the journal.

        :param pc: who uses the item
        :param item_name: name of the item
        :param notes: extra notes
        """
        tag = self.create_use_item_tag(pc, item_name, notes)

        self.write_general(tag)

    def write_end_downtime(self):
        """
        Method used to write the end of downtime in the attribute journal representing the html file of the journal.
        """
        tag = self.create_end_downtime_tag()

        self.write_general(tag)

    def write_change_vice_purveyor(self, pc: str, new_purveyor: str):
        """
        Method used to write the changing of a vice purveyor in the attribute journal representing
        the html file of the journal.

        :param pc: is the pc of interest.
        :param new_purveyor: is the new purveyor of the pc.
        """
        tag = self.create_change_vice_purveyor_tag(pc, new_purveyor)

        self.write_general(tag)

    def write_pc_migration(self, pc: str, migration_pc: str):
        """
        Method used to write the migration of a PC's type in the attribute journal representing
        the html file of the journal.

        :param pc: is the pc of interest.
        :param migration_pc: is the new type of the pc.
        """
        tag = self.create_pc_migration_tag(pc, migration_pc)

        self.write_general(tag)

    def write_change_pc_class(self, pc: str, new_class: str):
        """
        Method used to write the change of a PC's class in the attribute journal representing
        the html file of the journal.

        :param pc: is the pc of interest.
        :param new_class: is the new type of the pc.
        """
        tag = self.create_change_pc_class_tag(pc, new_class)

        self.write_general(tag)

    def write_retire(self, pc: str, description: str, choice: str):
        """
        Method used to write the retirement or death of a pc in the attribute journal representing
        the html file of the journal.

        :param pc: is the pc of interest.
        :param description: is the description of the death or retirement.
        :param choice: if the pcs dies or retire
        """
        tag = self.create_retire_tag(pc, description, choice)

        self.write_general(tag)

    def write_end_game(self, notes: str):
        """
        Method used to write the description of the end of the game in the attribute journal representing
        the html file of the journal.

        :param notes: description of the end of the game
        """
        tag = self.create_end_game_tag(notes)

        self.write_general(tag)

    def __eq__(self, o: object) -> bool:
        return isinstance(o, self.__class__) and o.__dict__ == self.__dict__
