import json
import math
from typing import List, Union, Literal

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
        self.score_tags = []
        self.write_heading()

    def edit_note(self, note: str, number: int = 1):
        """
        Allows to change a specified note, depending on its position inside the list of description.

        :param note: is the new note that will be written
        :param number: is the position of the note. It's given starting from the most recent to the oldest one,
        meaning the note 1 is the last note written
        """
        # TODO:

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

    def write_heading(self):
        """
        Method used to write all the heading in the attribute journal representing the html file of the journal.
        """
        doctype = Doctype('html')
        self.log.append(doctype)

        html_tag = self.log.new_tag("html", lang="en")

        head_tag = self.log.new_tag("head")
        html_tag.append(head_tag)

        meta_tag = self.log.new_tag("meta", charset="UTF-8")
        head_tag.append(meta_tag)

        head_tag.append(BeautifulSoup('''<link rel="preconnect" href="https://fonts.googleapis.com"> 
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin> 
        <link href="https://fonts.googleapis.com/css2?family=Merienda+One&family=Mochiy+Pop+One&family=Rye&family=Syne+Mono&family=Vast+Shadow&display=swap" rel="stylesheet">''',
                                      'html.parser'))

        title_tag = self.log.new_tag("title")
        title_tag.string = "Blades in The Dark - Journal"
        head_tag.append(title_tag)

        style_tag = self.log.new_tag("style")
        style_tag.append('''
            body{
                background-color: rgb(0, 0, 0);
	            width: 80%; padding-left: 10%;
            }
            div {
                background-color: rgb(35, 37, 43);
            	border-radius: 10px;
            	border: 2px solid rgb(224, 233, 241);
            	margin: 1%;
            	border-style: dotted;
            }
            h1{
            	color: rgb(167, 85, 34);
				font-family: "Rye";
				font-size: 45px;
				font-weight: bold;
				text-align: center;
            	padding-left: 2%;
            }
            h2{
            	color: #e3ded9; padding-left: 1%;
            	border-bottom: 4px solid rgb(167, 85, 34);
            	margin-right: 50%;
            	border-bottom-style: groove;
            	margin-left: 1%;
				font-family: 'Marker Felt';
            }
            h3{
            	color: #b5abab;
            	padding-left: 2%;
				font-family: "Mochiy Pop One";
            }
            h4{
            	color: #c3afaf;
            	padding-left: 2%;
				font-family: "Merienda One";
            }
            p{
            	color: #ffffff;
            	font-family: "Syne Mono";
            	padding-left: 5%
            }
            ul{
            	color: #FFFFFF; 
            	font-family: "Comic Sans MS",sans-serif;
            }
            summary{
            	color: #a9a9a9;
            }
            table, th, td{
            	border: 1px solid #ffffff; 
            	margin-left: 125px
            }
            th, td{
            	text-align: center; 
            	padding-left: 20px; 
            	padding-right: 20px; 
            	padding-block: 10px
            }
            th{
            	color: #FFFFFF
            }
            .secret{
            	color: #2f2f2f;
            	background-color:#2f2f2f;
            }
            .secret:hover{
            	color: white;
            }
			.state{
				font-family: "Vast Shadow";
				font-size: xx-large;
				margin-bottom: 5%;
				margin-top: 1%;
				color: rgb(161, 64, 0);
				text-align: center;
				border-bottom: 4px solid rgb(167, 85, 34);
			}
			.piechart {
            	width: 60px;
            	height: 60px;
            	border-radius: 50%;
				border: solid white 1px;
				align-self: center;
        	}
			.center {
				width: 10px;
				height: 10px;
				border-radius: 50%;
				background-color: black;
				position: relative;
				margin: 25px;
				border: none;
			}
			.clock {
				height:auto;
				display:flex;
			} 
			.one {
				width:70%;
				margin:10px;
				border: none;
			} 
        ''')

        head_tag.append(style_tag)

        self.log.append(html_tag)

        self.log.select_one("html").append(self.log.new_tag("body"))

    def create_title_tag(self, game_name: str):
        """
        Method used to write the title of the game in the attribute journal representing the html file of the journal.

        :param game_name: str representing the name of the game
        """
        placeholder = self.get_lang(self.write_title.__name__)
        title_tag = self.log.new_tag("h1")
        title_tag.string = placeholder["0"].format(game_name)

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

    def create_general_notes_tag(self, title: str, notes: str):
        """
        Method used to create and insert a div tag with class attribute set to "generalNotes".

        :param title: str representing the title of the notes
        :param notes: str representing the actual notes
        :return: the div Tag
        """
        div_tag = self.create_div_tag({"class": "generalNotes"})

        div_tag.append(self.create_h2_tag(title))

        div_tag.append(self.create_p_tag(notes))

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

    def create_score_tag(self, name: str, plan_type: str, details: str, pc_load: List, position: str, notes: str):
        """
        Method used to create and insert a div tag with class attribute set to "score".

        :param name: name of the score
        :param plan_type: type of the score's plan
        :param details: details of the plan
        :param pc_load: list of tuples made of name of the pc and their load
        :param position: position of the engagement roll
        :param notes: extra notes
        :return: the div Tag
        """
        placeholder = self.get_lang(self.write_score.__name__)
        div_tag = self.create_div_tag({"class": "score",
                                       "style": "margin-left: {}%".format(self.get_indentation())})

        div_tag.append(self.create_h2_tag(placeholder["0"].format(name)))

        div_tag.append(self.create_h3_tag(placeholder["1"]))

        div_tag.append(self.create_p_tag(plan_type))

        div_tag.append(self.create_h3_tag(placeholder["2"]))

        div_tag.append(self.create_p_tag(details))

        div_tag.append(self.create_h3_tag(placeholder["3"]))

        table_tag = self.log.new_tag("table")
        tr_tag = self.log.new_tag("tr")
        th_tag = self.log.new_tag("th")
        th_tag.string = placeholder["4"]
        tr_tag.append(th_tag)
        th_tag = self.log.new_tag("th")
        th_tag.string = placeholder["5"]
        tr_tag.append(th_tag)
        table_tag.append(tr_tag)

        for i in range(len(pc_load)):
            tr_tag = self.log.new_tag("tr")
            th_tag = self.log.new_tag("th")
            th_tag.string = pc_load[i][0]
            tr_tag.append(th_tag)
            th_tag = self.log.new_tag("th")
            th_tag.string = str(pc_load[i][1])
            tr_tag.append(th_tag)
            table_tag.append(tr_tag)

        div_tag.append(table_tag)

        div_tag.append(self.create_h3_tag(placeholder["6"]))

        div_tag.append(self.create_p_tag(placeholder["7"].format(position)))

        div_tag.append(self.create_p_tag(notes, {"class": "user"}))

        self.indentation += 1

        return div_tag

    def create_action_roll_tag(self, pc: str, goal: str, action: str, position: str, effect: str, outcome: int,
                               notes: str, assistants: List[str] = None, push: bool = False, devils: str = None):
        """F
        Method used to create and insert a div tag with class attribute set to "actionRoll".

        :param pc: who does the action roll
        :param goal: goal of the action roll
        :param action: what will the character do
        :param position: starting position of the action
        :param effect: effect of the action if successful
        :param outcome: outcome of the dice roll
        :param notes: extra notes
        :param assistants: from whom the user got help
        :param push: if the user push themselves
        :param devils: what deal the user made
        :return: the div Tag
        """
        placeholder = self.get_lang(self.write_action_roll.__name__)
        div_tag = self.create_div_tag({"class": "actionRoll",
                                       "style": "margin-left: {}%".format(self.get_indentation())})

        div_tag.append(self.create_h2_tag(placeholder["0"]))

        div_tag.append(self.create_h4_tag(placeholder["1"]))

        div_tag.append(
            self.create_p_tag(placeholder["2"].format(pc, goal, action)))

        div_tag.append(self.create_p_tag(placeholder["3"].format(position, effect)))

        if assistants:
            temp = assistants[0]
            for i in range(1, len(assistants)):
                temp += ", " + assistants[i]
            div_tag.append(
                self.create_p_tag(placeholder["4"].format(pc, temp)))
        if push:
            div_tag.append(self.create_p_tag(placeholder["5"].format(pc)))
        if devils:
            div_tag.append(self.create_p_tag(placeholder["6"].format(pc, devils)))

        div_tag.append(self.create_h4_tag(placeholder["7"]))

        div_tag.append(self.create_p_tag(placeholder["8"].format(outcome)))

        try:
            lang = self.get_lang("results")["action_roll"][position.lower()]
        except:
            lang = self.get_lang("results")["action_roll"]["others"]

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

        div_tag.append(self.create_p_tag(placeholder["2"].format(
            amount, placeholder[str(3 + int(distributed))]
        )))

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

        div_tag.append(self.create_p_tag(description))

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

        details_tag = self.log.new_tag("details")

        summary_tag = self.log.new_tag("summary")
        summary_tag.append(BeautifulSoup(placeholder["1"], 'html.parser'))
        details_tag.append(summary_tag)

        details_tag.append(self.create_p_tag(name))

        details_tag.append(self.create_p_tag(description))

        div_tag.append(details_tag)

        self.log.select_one("body").append(div_tag)

        return div_tag

    def create_activity_tag(self, pc: str,
                            activity: Literal['acquire_assets', 'crafting', 'long_term_project', 'recover',
                                              'reduce_heat', 'train', 'indulge_vice', 'help_cohort',
                                              'replace_cohort'],
                            extra_info: str = None, rolls: int = 0, extra_roll=None,
                            overindulge: Literal['brag', 'lost', 'tapped', 'attracted trouble'] = None,
                            extra_overindulge: str = "", notes: str = ""):
        """
        Method used to create and insert a div tag with class attribute set to "activity".

        :param pc: who does the downtime activity
        :param activity: type of activity. Choose from: 'acquire_assets', 'crafting', 'long_term_project', 'recover',
        'reduce_heat', 'train', 'indulge_vice', 'help_cohort', 'replace_cohort'
        :param extra_info: extra information about the activity
        :param rolls: result of the roll
        :param extra_roll: extra information obtained by the roll (e.g. quality, name of the new cohort,
        amount of stress)
        :param overindulge: if the activity was 'indulge_vice' this the type. Choose from: 'Brag', 'Lost', 'Tapped',
        'Attracted trouble'
        :param extra_overindulge: extra information about how they overindulged
        :param notes: extra notes
        :return: the div Tag
        """
        placeholder = self.get_lang(self.write_activity.__name__)
        activity = activity.lower()
        div_tag = self.create_div_tag({"class": "activity"})

        div_tag.append(self.create_h2_tag(placeholder["default"]["0"]))

        div_tag.append(self.create_p_tag(placeholder["default"]["1"].format(pc, placeholder[activity]["0"], "({})".
                                                                            format(extra_info) if extra_info else "")))

        div_tag.append(self.create_p_tag(placeholder["default"]["2"].format(
            rolls, placeholder[activity]["1"].format(extra_roll))))

        if activity == "indulge_vice" and overindulge:
            div_tag.append(self.create_p_tag(placeholder[activity]["2"]))
            overindulge = overindulge.lower()

            if overindulge == "brag":
                div_tag.append(self.create_p_tag(placeholder[activity]["3"].format(extra_overindulge)))
            elif overindulge == "lost":
                div_tag.append(self.create_p_tag(placeholder[activity]["4"].format(extra_overindulge)))
            elif overindulge == "tapped":
                div_tag.append(self.create_p_tag(placeholder[activity]["5"].format(extra_overindulge)))
            elif overindulge == "attracted trouble":
                div_tag.append(self.create_p_tag(placeholder[activity]["6"].format(extra_overindulge)))

        div_tag.append(self.create_p_tag(notes, {"class": "user"}))

        return div_tag

    def create_add_claim_tag(self, lair: bool, claim_name: str):
        """
        Method used to create and insert a div tag with class attribute set to "addClaim".

        :param lair: True if the new claim is a lair claim, False if it's a prison claim
        :param claim_name: name of the new claim
        :return: the div Tag
        """
        placeholder = self.get_lang(self.write_add_claim.__name__)
        div_tag = self.create_div_tag({"class": "addClaim",
                                       "style": "margin-left: {}%".format(self.get_indentation())})

        div_tag.append(self.create_h4_tag(placeholder["0"]))

        div_tag.append(self.create_p_tag(placeholder["1"].format(placeholder[str(2 + lair)], claim_name)))

        return div_tag

    def create_incarceration_tag(self, pc: str, roll: Union[str, int], extra_info: str, notes: str):
        """
        Method used to create and insert a div tag with class attribute set to "incarceration".

        :param pc: who is going to jail
        :param roll: what he rolls
        :param extra_info: if the roll is equal or higher than 6 (CRITICAL) it's the name of the new prison claim,
        otherwise is the name of the trauma
        :param notes: extra notes
        :return: the div Tag
        """
        placeholder = self.get_lang(self.write_incarceration.__name__)
        div_tag = self.create_div_tag({"class": "incarceration"})

        div_tag.append(self.create_h2_tag(placeholder["0"]))

        div_tag.append(self.create_p_tag(placeholder["1"].format(pc)))

        div_tag.append(self.create_p_tag(placeholder["2"].format(roll)))

        p_tag = self.log.new_tag("p")
        p_tag.string = notes
        div_tag.append(self.create_p_tag(notes, {"class": "user"}))

        if (isinstance(roll, str) and roll == "CRITICAL") or (isinstance(roll, int) and roll >= 6):
            self.indentation += 1
            div_tag.append(self.create_add_claim_tag(False, extra_info))
            self.indentation -= 1

        elif isinstance(roll, int) and 1 <= roll < 3:
            div_tag.append(self.create_p_tag(placeholder["3"].format(
                pc, extra_info)))

        return div_tag

    def create_flashback_tag(self, pc: str, notes: str, roll: Union[str, int], roll_info: str,
                             downtime_flashback: bool):
        """
        Method used to create and insert a div tag with class attribute set to "flashback".

        :param pc: who has the flashback
        :param notes: description of the flashback
        :param roll: roll of the dice
        :param roll_info: type of roll made by the user
        :param downtime_flashback: True if it is a downtime flashback, False otherwise
        :return: the div Tag
        """
        placeholder = self.get_lang(self.write_flashback.__name__)
        div_tag = self.create_div_tag({"class": "flashback"})

        div_tag.append(self.create_h2_tag(placeholder["0"]))

        div_tag.append(self.create_p_tag(placeholder["1"].format(pc, placeholder["3"] if downtime_flashback else "")))

        div_tag.append(self.create_p_tag('"{}"'.format(notes), {"class": "user"}))

        div_tag.append(self.create_p_tag(placeholder["2"].format(pc, roll_info, roll)))

        return div_tag

    def create_resistance_roll_tag(self, pc: str, description: str, attribute: str, roll: Union[str, int],
                                   stress: int = 0):
        """
        Method used to create and insert a div tag with class attribute set to "resistanceRoll".

        :param pc: who is doing the resistance roll
        :param description: why the user is doing the resistance roll
        :param attribute: what attribute is rolling
        :param roll: roll of the dice
        :param stress: amount of stress gained
        :return: the div Tag
        """
        placeholder = self.get_lang(self.write_resistance_roll.__name__)
        div_tag = self.create_div_tag({"class": "resistanceRoll"})

        div_tag.append(self.create_h2_tag(placeholder["0"]))

        div_tag.append(self.create_p_tag(placeholder["1"].format(
            pc, description)))

        if stress > 0:
            div_tag.append(self.create_p_tag(placeholder["2"].format(pc, attribute, roll,
                                                                     placeholder["3"].format(stress))))
        elif stress < 0:
            div_tag.append(self.create_p_tag(placeholder["2"].format(pc, attribute, roll,
                                                                     placeholder["4"].format(-stress))))
        else:
            div_tag.append(self.create_p_tag(placeholder["2"].format(pc, attribute, roll, "")))

        return div_tag

    def create_group_action_tag(self, pc: str, goal: str, action: str, roll: int, notes: str, position: str,
                                effect: str,
                                players: List[str] = None, cohort: str = None, helper: str = None, push: bool = False,
                                devils: str = None):
        """
        Method used to create and insert a div tag with class attribute set to "groupAction".

        :param pc: who starts the group action
        :param goal: goal of the group action
        :param action: action used to roll the group action
        :param roll: result of the dice roll
        :param notes: extra notes
        :param position: starting position of the group action
        :param effect: effect of the group action
        :param players: if it's a group action made with other players this is the list of their name. None otherwise
        :param cohort: if it's a group action made with a cohort this is the type of the cohort. None otherwise
        :param helper: if someone helps this is their name. None otherwise
        :param push: True if the user pushed themselves. False otherwise
        :param devils: if a devil's bargain has been made this is its description. None otherwise
        :return: the div Tag
        """
        placeholder = self.get_lang(self.write_group_action.__name__)
        div_tag = self.create_div_tag({"class": "groupAction"})

        div_tag.append(self.create_h2_tag(placeholder["0"]))

        div_tag.append(self.create_p_tag(placeholder["1"].format(pc, goal)))

        if players:
            div_tag.append(self.create_p_tag(placeholder["2"].format(" ".join(players))))
        elif cohort:
            div_tag.append(self.create_p_tag(placeholder["3"].format(pc, cohort)))

        div_tag.append(self.create_p_tag(placeholder["4"].format(position, effect)))

        if helper:
            div_tag.append(self.create_p_tag(placeholder["5"].format(helper)))

        if push:
            div_tag.append(self.create_p_tag(placeholder["6"]))

        if devils:
            div_tag.append(self.create_p_tag(placeholder["7"].format(devils)))

        div_tag.append(self.create_p_tag(placeholder["8"].format(action, roll)))

        div_tag.append(self.create_p_tag(notes, {"class": "user"}))

        return div_tag

    def create_clock(self, pc: str, new_clock: Clock, old_clock: Clock = None):
        """
        Method used to create and insert a div tag with class attribute set to "clock".

        :param pc: who creates the clock
        :param new_clock: new clock to represent with the div tag
        :param old_clock: old clock used to compare with the new one to know with sentence to use in the paragraph
        :return: the div Tag
        """

        placeholder = self.get_lang(self.write_clock.__name__)

        # This first part is used to draw the clock with a div tag
        divider_size = 4

        black = "black {}deg {}deg"
        white = "white {}deg {}deg"
        red = "red {}deg {}deg"
        conic_gradient = ""

        segment_size = int((360 - (divider_size * new_clock.segments)) / new_clock.segments)
        count = 0
        for i in range(new_clock.segments - 1):
            next_count = count + divider_size
            conic_gradient += white.format(count, next_count) + ", "

            count = next_count + segment_size
            if i < new_clock.progress:
                conic_gradient += red.format(next_count, count) + ", "
            else:
                conic_gradient += black.format(next_count, count) + ", "

        next_count = count + divider_size
        conic_gradient += white.format(count, next_count) + ", "

        count = next_count + segment_size
        if new_clock.segments == new_clock.progress:
            conic_gradient += red.format(next_count, count)
        else:
            conic_gradient += black.format(next_count, count)

        style = "background-image: conic-gradient({});".format(conic_gradient)

        # This part is used to create the div tag
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

        clock_tag = self.create_div_tag({"class": "piechart", "style": style})

        div_tag.append(clock_tag)

        return div_tag

    def get_indentation(self) -> int:
        """
        Method used to get the percentage indentation based on the value of the attribute indentation

        :return: int representing the percentage indentation
        """
        if self.indentation != 0:
            return int(5 * (math.log(self.indentation) + 1)) + 1
        return 1

    def create_div_tag(self, attrs: dict):
        """
        Method used to create a "div" tag.

        :param attrs: attributes of the div tag
        :return: a "div" Tag
        """
        return self.log.new_tag("div", attrs=attrs)

    def create_h2_tag(self, content: str, attrs: dict = None):
        """
        Method used to create a "h2" tag

        :param content: content of the "h2" tag
        :param attrs: attributes of the h2 tag. If there are no attributes is set to None
        :return: a "h2" Tag
        """
        if attrs:
            h2_tag = self.log.new_tag("h2", attrs=attrs)
        else:
            h2_tag = self.log.new_tag("h2")
        h2_tag.append(BeautifulSoup(content, 'html.parser'))
        return h2_tag

    def create_h3_tag(self, content: str, attrs: dict = None):
        """
        Method used to create a "h3" tag.

        :param content: content of the "h3" tag
        :param attrs: attributes of the h3 tag. If there are no attributes is set to None
        :return: a "h3" Tag
        """
        if attrs:
            h3_tag = self.log.new_tag("h3", attrs=attrs)
        else:
            h3_tag = self.log.new_tag("h3")
        h3_tag.append(BeautifulSoup(content, 'html.parser'))
        return h3_tag

    def create_h4_tag(self, content: str, attrs: dict = None):
        """
        Method used to create a "h4" tag.

        :param content: content of the h4 tag
        :param attrs: attributes of the h4 tag. If there are no attributes is set to None
        :return: a "h4" Tag
        """
        if attrs:
            h4_tag = self.log.new_tag("h4", attrs=attrs)
        else:
            h4_tag = self.log.new_tag("h4")
        h4_tag.append(BeautifulSoup(content, 'html.parser'))
        return h4_tag

    def create_p_tag(self, content: str, attrs: dict = None):
        """
        Method used to create a "p" tag.

        :param content: content of the p tag
        :param attrs: attributes of the p tag. If there are no attributes is set to None
        :return: a "p" Tag
        """
        if attrs:
            p_tag = self.log.new_tag("p", attrs=attrs)
        else:
            p_tag = self.log.new_tag("p")
        p_tag.append(BeautifulSoup(content, 'html.parser'))
        return p_tag

    def write_general(self, tag):
        """
        Method used to write a tag inside the html file of the journal.

        :param tag: tag to write
        """
        if self.score_tags:
            temp = self.score_tags[len(self.score_tags) - 1]
            temp_child = temp.find("div", {"class": "endScore"}, recursive=False)
            if temp_child is None:
                temp.append(tag)
            else:
                temp.parent.append(tag)
        else:
            self.log.select_one("body").append(tag)

    def write_title(self, game_name: str):
        """
        Method used to write the title of the game in the attribute journal representing the html file of the journal.

        :param game_name: str representing the name of the game
        """
        self.log.select_one("body").append(self.create_title_tag(game_name))

    def write_general_notes(self, title: str, notes: str):
        """
        Method used to write general notes in the attribute journal representing the html file of the journal.

        :param title: str representing the title of the notes
        :param notes: str representing the actual notes
        """
        tag = self.create_general_notes_tag(title, notes)

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

    def write_score(self, name: str, plan_type: str, details: str, pc_load: List, position: str, notes: str):
        tag = self.create_score_tag(name, plan_type, details, pc_load, position, notes)
        """
        Method used to write a score in the attribute journal representing the html file of the journal.

        :param name: name of the score
        :param plan_type: type of the score's plan
        :param details: details of the plan
        :param pc_load: list of tuples made of name of the pc and their load
        :param position: position of the engagement roll
        :param notes: extra notes
        """
        self.write_general(tag)

        self.score_tags.append(tag)

    def write_action_roll(self, pc: str, goal: str, action: str, position: str, effect: str, outcome: int,
                          notes: str, assistants: List[str] = None, push: bool = False, devil_bargain: str = None):
        """
        Method used to write an action outcome in the attribute journal representing the html file of the journal.

        :param pc: who does the action roll
        :param goal: goal of the action roll
        :param action: what will the character do
        :param position: starting position of the action
        :param effect: effect of the action of successful
        :param outcome: result of the dice roll
        :param notes: extra notes
        :param assistants: from whom the user got help
        :param push: if the user push themselves
        :param devil_bargain: what deal the user made
        """
        tag = self.create_action_roll_tag(pc, goal, action, position, effect, outcome,
                                          notes, assistants, push, devil_bargain)

        self.write_general(tag)

    def write_end_score(self, outcome: str, notes: str):
        """
        Method used to write the end of the score in the attribute journal representing the html file of the journal.

        :param outcome: exposure of the score
        :param notes: extra notes
        """
        tag = self.create_end_score_tag(outcome, notes)

        self.write_general(tag)

        self.score_tags.pop(len(self.score_tags) - 1)

    def write_payoff(self, amount: int, distributed: bool, notes: str):
        """
        Method used to write the payoff in the attribute journal representing the html file of the journal.

        :param amount: amount of money obtained during the score
        :param distributed: True if the coin are distributed among the players, False otherwise
        :param notes: extra notes about the payoff
        :return:
        """
        tag = self.create_payoff_tag(amount, distributed, notes)

        self.write_general(tag)

    def write_heat(self, execution: str, exposure: str, famous_target: bool, hostile: bool, war: bool,
                   bodies: bool, heat: int, wanted: int):
        """
        Method used to write the payoff in the attribute journal representing the html file of the journal.

        :param execution: how loud the score was executed
        :param exposure: type of exposure received
        :param famous_target: True if the target was famous, False otherwise
        :param hostile: True if the score was made in a hostile turf, False otherwise
        :param war: True if the crew is at war, False otherwise
        :param bodies: True if someone was killed, False otherwise
        :param heat: amount of heat received
        :param wanted: amount of wanted level received
        """
        tag = self.create_heat_tag(execution, exposure, famous_target, hostile, war, bodies, heat, wanted)

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

    def write_activity(self, pc: str,
                       activity: Literal['acquire_assets', 'crafting', 'long_term_project', 'recover',
                                         'reduce_heat', 'train', 'indulge_vice', 'help_cohort',
                                         'replace_cohort'],
                       extra_info: str = None, rolls: int = 0, extra_roll=None,
                       overindulge: str = None, extra_overindulge: str = "", notes: str = ""):
        """
        Method used to write a downtime activity in the attribute journal representing the html file of the journal.

        :param pc: who does the downtime activity
        :param activity: type of activity. Choose from: 'acquire_assets', 'crafting', 'long_term_project', 'recover',
        'reduce_heat', 'train', 'indulge_vice', 'help_cohort', 'replace_cohort'
        :param extra_info: extra information about the activity
        :param rolls: result of the roll
        :param extra_roll: extra information obtained by the roll (e.g. quality, name of the new cohort,
        amount of stress)
        :param overindulge: if the activity was 'indulge_vice' this the type. Choose from: 'Brag', 'Lost', 'Tapped',
        'Attracted trouble'
        :param extra_overindulge: extra information about how they overindulged
        :param notes: extra notes
        """
        tag = self.create_activity_tag(pc, activity, extra_info, rolls,
                                       extra_roll, overindulge, extra_overindulge, notes)

        self.write_general(tag)

    def write_add_claim(self, lair: bool, claim_name: str):
        """
        Method used to write add claim in the attribute journal representing the html file of the journal.

        :param lair: True if the new claim is a lair claim, False if it's a prison claim
        :param claim_name: name of the new claim
        """
        tag = self.create_add_claim_tag(lair, claim_name)

        self.write_general(tag)

    def write_incarceration(self, pc: str, roll: Union[str, int], extra_info: str, notes: str):
        """
        Method used to write the incarceration in the attribute journal representing the html file of the journal.

        :param pc: who is going to jail
        :param roll: what he rolls
        :param extra_info: if the roll is equal or higher than 6 (CRITICAL) it's the name of the new prison claim,
        otherwise is the name of the trauma
        :param notes: extra notes
        """
        tag = self.create_incarceration_tag(pc, roll, extra_info, notes)

        self.write_general(tag)

    def write_flashback(self, pc: str, notes: str, roll: Union[str, int], roll_info: str,
                        downtime_flashback: bool):
        """
        Method used to write a flashback in the attribute journal representing the html file of the journal.

        :param pc: who has the flashback
        :param notes: description of the flashback
        :param roll: roll of the dice
        :param roll_info: type of roll made by the user
        :param downtime_flashback: True if it is a downtime flashback, False otherwise
        """
        tag = self.create_flashback_tag(pc, notes, roll, roll_info, downtime_flashback)

        self.write_general(tag)

    def write_resistance_roll(self, pc: str, description: str, attribute: str, roll: Union[str, int],
                              stress: int = 0):
        """
        Method used to write a resistance roll in the attribute journal representing the html file of the journal.

        :param pc: who is doing the resistance roll
        :param description: why the user is doing the resistance roll
        :param attribute: what attribute is rolling
        :param roll: roll of the dice
        :param stress: amount of stress gained
        """
        tag = self.create_resistance_roll_tag(pc, description, attribute, roll, stress)

        self.write_general(tag)

    def write_group_action(self, pc: str, goal: str, action: str, roll: int, notes: str, position: str,
                           effect: str, players: List[str] = None, cohort: str = None, helper: str = None,
                           push: bool = None, devils: str = None):
        """
        Method used to write a group action in the attribute journal representing the html file of the journal.

        :param pc: who starts the group action
        :param goal: goal of the group action
        :param action: action used to roll the group action
        :param roll: result of the dice roll
        :param notes: extra notes
        :param position: starting position of the group action
        :param effect: effect of the group action
        :param players: if it's a group action made with other players this is the list of their name. None otherwise
        :param cohort: if it's a group action made with a cohort this is the type of the cohort. None otherwise
        :param helper: if someone helps this is their name. None otherwise
        :param push: True if the user pushed themselves. False otherwise
        :param devils: if a devil's bargain has been made this is its description. None otherwise
        """
        tag = self.create_group_action_tag(pc, goal, action, roll, notes, position,
                                           effect, players, cohort, helper, push, devils)

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

    def __eq__(self, o: object) -> bool:
        return isinstance(o, self.__class__) and o.__dict__ == self.__dict__
