import copy
import threading

from character.Human import Human
from component.Clock import Clock
from controller.DBreader import *
from controller.DBwriter import *
from game.Game import Game
from game.Player import Player
from organization.Cohort import Cohort
from organization.Crew import Crew
from utility.FilesLoader import load_games
from utility.ISavable import save_to_json
from utility.htmlFactory import MapFactory


class Controller:

    def __init__(self) -> None:
        self.games = load_games()
        self.lock_add_game = threading.Lock()

    def get_game_by_id(self, game_id: int) -> Game:
        """
        Gets the instance of the game with the specified id.

        :param game_id: the game's id.
        :return: the selected Game.
        """
        for game in self.games:
            if game.identifier == game_id:
                return game

    def add_game(self, chat_id: int, title: str = None) -> int:
        """
        Creates a new Game and adds it to self.games

        :param title: the title of the new Game
        :param chat_id: the id of the telegram chat where the game is created.
        :return: the id of the game in the Data Base
        """
        self.lock_add_game.acquire()
        new_game = Game(title=title, chat_id=chat_id)

        insert_game(new_game.identifier, new_game.title, new_game.chat_id)
        new_game.journal.write_title(title)
        insert_journal(new_game.identifier, new_game.journal.get_log_string())

        self.games.append(new_game)

        self.lock_add_game.release()
        return new_game.identifier

    def update_user_in_game(self, player_id: int, chat_id: int, game_title: str,
                            is_master: bool = False, pc: dict = None):
        """
        Adds a new user to the specified Game's list of player. If the user was already present, is updated with the new
        information or changes. In any case the Data Base is updated too.

        :param player_id: telegram id of the user to update.
        :param chat_id: identifier of the origin chat of the Game.
        :param game_title: name of the Game where the player is/needs to be added
        :param is_master: bool that state if the player should be set to master. If True the old master is removed from
                        his role and eventually removed from the list if he had no characters.
        :param pc: dict containing all the information about a pc. If None, no pc is added to the player.
        """
        game_id = query_game_ids(chat_id, game_title)[0]
        human = None
        if pc is not None:
            action_dots = pc.pop("action_dots")
            human = Human.from_json(pc)

            # Transforming the dict into a list of tuples
            action_dots = list(action_dots.items())
            for action in action_dots:
                human.add_action_dots(*action)

        game = self.get_game_by_id(game_id)
        if game is not None:

            # Old master
            if is_master:
                master = game.get_master()
                if master is not None:
                    master.is_master = False
                    if not master.characters:
                        game.users.remove(master)
                        delete_user_game(master.player_id, game_id)
                    else:
                        insert_user_game(master.player_id, game_id, save_to_json(master.characters),
                                         master.is_master)

            # User already present
            for user in game.users:
                if user.player_id == player_id:

                    if is_master:
                        user.is_master = is_master
                    if human is not None:
                        user.characters.append(human)

                    insert_user_game(player_id, game_id, save_to_json(user.characters), user.is_master)
                    return

            # New user
            new_player = Player(query_users_names(player_id)[0], player_id, is_master)
            if human is not None:
                new_player.characters.append(human)
            game.users.append(new_player)

            insert_user_game(player_id, game_id, save_to_json(new_player.characters), is_master)

    def update_crew_in_game(self, player_id: int, chat_id: int, crew: dict):
        """
        Adds the new crew to the specified Game. If the crew was already present it is replaced.
        In any case the Data Base is updated too.

        :param player_id: telegram id of the user to update.
        :param chat_id: identifier of the origin chat of the Game.
        :param crew: dict containing all the information about a crew.
        """
        game_id = query_game_of_user(chat_id, player_id)

        upgrades = []
        if "upgrades" in crew:
            upgrades = crew.pop("upgrades")

        cohorts = []
        if "cohorts" in crew:
            cohorts = crew.pop("cohorts")

        game = self.get_game_by_id(game_id)

        if game is not None:
            game.crew = Crew.from_json(crew)

        for upgrade in upgrades:
            name = exists_upgrade(upgrade["name"])
            if name is not None:
                for i in range(upgrade["quality"]):
                    game.crew.add_upgrade(name)

        for cohort in cohorts:
            game.crew.cohorts.append(Cohort(**cohort))

        insert_crew_json(game_id, save_to_json(game.crew))

    def get_game_state(self, game_id: int) -> int:
        """
        Gets the state of the selected game.

        :param game_id: the game's id.
        :return: the state of the selected Game.
        """
        return self.get_game_by_id(game_id).state

    def can_start_game(self, game_id: int) -> bool:
        """
        Checks if the selected Game can start.
        The Game needs to fulfill the INIT phase requirements: must have a master, a crew and at least one PC

        :param game_id: the game's id.
        :return: True if the selected Game can start, False otherwise.
        """
        game = self.get_game_by_id(game_id)
        if game.get_master() is not None and game.crew is not None and game.get_pcs_list():
            return True
        return False

    def change_state(self, game_id: int, new_state: int):
        """
        Changes the current state of the game to the selected one.

        :param game_id: the game's id.
        :param new_state: the destination state.
        """
        game = self.get_game_by_id(game_id)

        game.scores.clear()
        game.journal.indentation = 0

        for player in game.users:
            for pc in player.characters:
                pc.clear_consumable()

        game.state = new_state
        game.journal.write_phase(new_state)
        insert_state(game_id, new_state)

    def get_user_characters_names(self, user_id: int, chat_id: int) -> List[str]:
        """
        Retrieves the list of the PCs' names of the specified user, in the specified chat.

        :param user_id: the Telegram id of the user.
        :param chat_id: the Telegram chat id of the user.
        :return: a list of strings containing all the names.
        """

        game = self.get_game_by_id(query_game_of_user(chat_id, user_id))

        pcs = game.get_pcs_list(user_id)
        pcs_names = []
        for pc in pcs:
            pcs_names.append(pc.name)

        return pcs_names

    def get_pc_actions_ratings(self, user_id: int, chat_id: int, pc_name: str) -> List[Tuple[str, int]]:
        """
        Retrieves all the action with the related rating of the specified PC of the user in the chat.

        :param user_id: the Telegram id of the user.
        :param chat_id: the Telegram chat id of the user.
        :param pc_name: the name of the target PC.
        :return: a list of tuples with the name of the action and the action's rating in this order.
        """
        game = self.get_game_by_id(query_game_of_user(chat_id, user_id))

        ratings = []
        pcs = game.get_pcs_list(user_id)
        for pc in pcs:
            if pc.name.lower() == pc_name.lower():
                for attribute in pc.attributes:
                    for action in attribute.actions:
                        ratings.append((action.name, action.rating))

                return ratings

    def get_pc_action_rating(self, user_id: int, chat_id: int, pc_name: str, action: str) -> Tuple[str, int]:
        actions_ratings = self.get_pc_actions_ratings(user_id, chat_id, pc_name)

        for elem in actions_ratings:
            if elem[0].lower() == action.lower():
                return elem

    def is_master(self, user_id: int, chat_id: int) -> bool:
        """
        Check if the specified user is the master of his game in the specified chat.

        :param user_id: the Telegram id of the user.
        :param chat_id: the Telegram chat id of the user.
        :return: True if the user is the GM, False otherwise.
        """
        game = self.get_game_by_id(query_game_of_user(chat_id, user_id))
        master = game.get_master()

        if master.player_id == user_id:
            return True
        return False

    def commit_action(self, chat_id: int, user_id: int, action_roll: dict) -> List[Tuple[str, int]]:
        """
        Applies the effects of the passed action to the interested game:
        adds the stress to the eventual assistants and
        to the performer of the action;
        sends the information to the Journal and updates PCs and Journal in the DB.

        :param chat_id: the Telegram id of the user who invoked the action roll.
        :param user_id: the Telegram chat id of the user.
        :param action_roll: dictionary containing all the necessary information about the roll.
        :return: a list of tuples with the names of the PCs and the numbers of their suffered trauma in this order.
        """

        game = self.get_game_by_id(query_game_of_user(chat_id, user_id))
        action_roll.pop("bonus_dice")

        trauma_victims = []

        # work on assistants: split id and name
        # assistants gets +1 stress
        if "assistants" in action_roll:
            assistants = action_roll.pop("assistants")

            pcs_names = []
            for assistant in assistants:
                user = game.get_player_by_id(assistant[0])
                traumas = user.get_character_by_name(assistant[1]).add_stress(1)
                pcs_names.append(assistant[1])
                if traumas > 0:
                    trauma_victims.append((assistant[1], traumas))
                update_user_characters(user.player_id, game.identifier, save_to_json(user.characters))

            action_roll["assistants"] = pcs_names

        # if Push +2 stress
        if action_roll["push"]:
            user = game.get_player_by_id(user_id)
            traumas = user.get_character_by_name(action_roll["pc"]).add_stress(2)
            if traumas > 0:
                trauma_victims.append((action_roll["pc"], traumas))
            update_user_characters(user_id, game.identifier, save_to_json(user.characters))

        # groupActionCohort
        if "cohort" in action_roll:
            action_roll["cohort"] = action_roll["cohort"][0]

        # groupAction
        if "participants" in action_roll:
            participants_journal = []
            participants = action_roll["participants"]
            for pc_name in participants:
                # if Push +2 stress
                if participants[pc_name]["push"]:
                    user = game.get_player_by_id(participants[pc_name]["id"])
                    traumas = user.get_character_by_name(pc_name).add_stress(2)
                    update_user_characters(participants[pc_name]["id"], game.identifier, save_to_json(user.characters))
                    if traumas > 0:
                        trauma_victims.append((pc_name, traumas))
                # if outcome<4 +1 stress to the leader
                if participants[pc_name]["outcome"] < 4 and participants[pc_name]["outcome"] != "CRIT":
                    user = game.get_player_by_id(user_id)
                    traumas = user.get_character_by_name(action_roll["pc"]).add_stress(1)
                    update_user_characters(user.player_id, game.identifier, save_to_json(user.characters))
                    if traumas > 0:
                        trauma_victims.append((action_roll["pc"], traumas))

                participants[pc_name].pop("id")
                participants[pc_name].pop("bonus_dice")
                participants[pc_name]["name"] = pc_name
                participants_journal.append(participants[pc_name])

            action_roll["participants"] = participants_journal

        # journal

        game.journal.write_action(**action_roll)

        insert_journal(game.identifier, game.journal.get_log_string())

        return trauma_victims

    def get_journal_of_game(self, game_id: int) -> Tuple[bytes, str]:
        game = self.get_game_by_id(game_id)

        return game.journal.read_journal(), ("Journal - " + game.title + ".html")

    def get_character_sheet_image(self, chat_id: int, user_id: int, pc_name: str) -> Tuple[bytes, str]:
        game = self.get_game_by_id(query_game_of_user(chat_id, user_id))

        kwargs = {}
        if game.crew is not None:
            kwargs["crew_name"] = game.crew.name
        return game.get_player_by_id(user_id).get_character_by_name(pc_name).draw_image(**kwargs), (pc_name + ".png")

    def get_crew_sheet_image(self, chat_id: int, user_id: int) -> Tuple[bytes, str]:
        game = self.get_game_by_id(query_game_of_user(chat_id, user_id))
        return game.crew.draw_image(), (game.crew.name + ".png")

    def get_interactive_map(self, chat_id: int, user_id: int) -> Tuple[bytes, str]:
        game = self.get_game_by_id(query_game_of_user(chat_id, user_id))
        players = game.users
        players_names = []
        for player in players:
            players_names.append(player.name)

        return MapFactory.modify(players_names), ("DoskvolMap.html")

    def add_cohort_in_crew(self, game_id: int, cohort: dict):
        """
        Adds the given cohort to the crew of the specified game and updates the crew in the Data Base.

        :param game_id: the game's id.
        :param cohort: aa dictionary representing with the parameters used to build a Cohort
        """
        crew = self.get_game_by_id(game_id).crew

        crew.add_cohort(Cohort(**cohort))

        insert_crew_json(game_id, save_to_json(crew))

    def add_clock_to_game(self, chat_id: int, user_id: int, clock: dict):
        """
        Adds the given clock to the game's list of clock, updates the clocks in the Data Base
        and write into the Journal.

        :param chat_id: the Telegram id of the user who invoked the action roll.
        :param user_id: the Telegram chat id of the user.
        :param clock: a dictionary representing the parameters used to build a Clock
        """
        game = self.get_game_by_id(query_game_of_user(chat_id, user_id))

        new_clock = game.create_clock(**clock)

        insert_clock_json(game.identifier, save_to_json(game.clocks))

        game.journal.write_clock(query_users_names(user_id)[0], new_clock)

        insert_journal(game.identifier, game.journal.get_log_string())

    def get_clocks_of_game(self, game_id: int) -> List[str]:
        """
        Retrieves the list of clocks of the specified game.

        :param game_id: the game's id.
        :return: the list of clocks' names of the specified game
        """
        return ["{}: {}/{}".format(clock.name, clock.progress, clock.segments)
                for clock in self.get_game_by_id(game_id).clocks]

    def tick_clock_of_game(self, chat_id: int, user_id: int, old_clock: dict, ticks: int) -> Tuple[bool, dict]:
        """
        Advances the specified clock of the game, updates the database and write into the journal.

        :param chat_id: the Telegram id of the user who invoked the action roll.
        :param user_id: the Telegram chat id of the user.
        :param old_clock: a dictionary representing the Clock to tick
        :param ticks: the number of ticks to add to the clock
        :return: a tuple with a bool (True if the clock has been completed)
        and a dictionary representing the modified Clock.
        """
        game = self.get_game_by_id(query_game_of_user(chat_id, user_id))

        clock_to_tick = Clock(**old_clock)

        game.tick_clock(clock_to_tick, ticks)

        new_clock = copy.deepcopy(clock_to_tick)
        filled = new_clock.tick(ticks)

        insert_clock_json(game.identifier, save_to_json(game.clocks))

        game.journal.write_clock(query_users_names(user_id)[0], new_clock, clock_to_tick)

        insert_journal(game.identifier, game.journal.get_log_string())

        return filled, new_clock.__dict__

    def add_claim_to_game(self, game_id: int, claim: dict):
        game = self.get_game_by_id(game_id)

        new_claim = Claim(claim["name"], claim["description"])

        if claim["prison"]:
            game.crew.add_prison_claim(new_claim)
        else:
            game.crew.add_lair_claim(new_claim)

        insert_crew_json(game_id, save_to_json(game.crew))

        claim.pop("description")

        game.journal.write_add_claim(**claim)

        insert_journal(game.identifier, game.journal.get_log_string())

    def game_has_crew(self, game_id: int) -> bool:
        game = self.get_game_by_id(game_id)
        return game.crew is not None

    def get_cohorts_of_crew(self, chat_id: int, user_id: int) -> List[Tuple[str, int]]:
        """
        Gives a list of tuple representing the cohorts of the specified crew.

        :param chat_id: the Telegram id of the user who invoked the action roll.
        :param user_id: the Telegram chat id of the user.
        :return: a list of tuple with a string representing the cohort's types and an int representing its quality
        """
        crew = self.get_game_by_id(query_game_of_user(chat_id, user_id)).crew

        co = []
        for cohort in crew.cohorts:
            label = ""
            if cohort.elite:
                label += "💠"
            if cohort.expert:
                label += "expert: "
            else:
                label += "gang: "
            label += cohort.type[0]
            for i in range(1, len(cohort.type)):
                label += ", "
                label += cohort.type[i]

            co.append((label, cohort.quality))

        return co

    def get_pc_attribute_rating(self, chat_id: int, user_id: int, pc_name: str) -> List[Tuple[str, int]]:
        """
        Retrieves all the attributes with the related rating of the specified PC of the user in the chat.

        :param chat_id: the Telegram id of the user.
        :param user_id: the Telegram chat id of the user.
        :param pc_name: the name of the target PC.
        :return: a list of tuples with the name of the attribute and the attribute's rating in this order.
        """
        game = self.get_game_by_id(query_game_of_user(chat_id, user_id))

        attributes_ratings = []

        pcs = game.get_pcs_list(user_id)
        for pc in pcs:
            if pc.name.lower() == pc_name.lower():
                for attribute in pc.attributes:
                    attributes_ratings.append((attribute.name, attribute.attribute_level()))
                return attributes_ratings

    def commit_resistance_roll(self, chat_id: int, user_id: int, resistance_roll: dict) -> Tuple[str, int]:
        """
        Applies the effects of the passed action to the interested game:
        adds the stress to the eventual assistants and to the performer of the action;
        sends the information to the Journal and updates PCs and Journal in the DB.

        :param chat_id: the Telegram id of the user who invoked the action roll.
        :param user_id: the Telegram chat id of the user.
        :param resistance_roll: dictionary containing all the necessary information about the roll.
        :return: a list of tuples with the names of the PCs and the numbers of their suffered trauma in this order.
        """

        game = self.get_game_by_id(query_game_of_user(chat_id, user_id))
        resistance_roll.pop("bonus_dice")

        trauma_victim = ()
        if isinstance(resistance_roll["outcome"], int):
            stress = 6 - resistance_roll["outcome"]
        else:
            stress = -1

        for pc in game.get_pcs_list(user_id):
            if pc.name == resistance_roll["pc"]:
                traumas = pc.add_stress(stress)
                if traumas != 0:
                    trauma_victim = (pc.name, traumas)

        update_user_characters(user_id, game.identifier, save_to_json(game.get_player_by_id(user_id).characters))

        # journal

        game.journal.write_resistance_roll(**resistance_roll, stress=stress)

        insert_journal(game.identifier, game.journal.get_log_string())

        return trauma_victim

    def get_factions(self, game_id: int) -> List[str]:
        def get_faction_by_name(name: str, factions_list: List[Faction]) -> Faction:
            for elem in factions_list:
                if elem.name.lower() == name.lower():
                    return elem

        game = self.get_game_by_id(game_id)

        game_factions = game.factions
        db_factions = query_factions()

        # replacing the factions that already exist in the game
        for i in range(len(db_factions)):
            existing_faction = get_faction_by_name(db_factions[i].name, game_factions)
            if existing_faction is not None:
                db_factions[i] = existing_faction

        factions = []
        for faction in db_factions:
            faction_string = ""
            if faction.status > 0:
                faction_string += "+{} \uD83D\uDD35 - ".format(faction.status)
            elif faction.status == 0:
                faction_string += "{} \u26AA\uFE0F - ".format(faction.status)
            elif faction.status < 0:
                faction_string += "{} \uD83D\uDD34 - ".format(faction.status)
            faction_string += "{}: {}".format(faction.name, faction.tier)
            factions.append(faction_string)

        return factions

    def get_npcs(self, game_id: int) -> List[str]:
        def get_npcs_by_name_and_role(name: str, role: str, npcs_list: List[NPC]) -> NPC:
            for elem in npcs_list:
                if elem.name.lower() == name.lower() and elem.role.lower() == role.lower():
                    return elem

        game = self.get_game_by_id(game_id)

        game_npcs = game.NPCs
        db_npcs = query_npcs()

        # replacing the factions that already exist in the game
        for i in range(len(db_npcs)):
            existing_npc = get_npcs_by_name_and_role(db_npcs[i].name, db_npcs[i].role, game_npcs)
            if existing_npc is not None:
                db_npcs[i] = existing_npc

        npcs = []
        for npc in db_npcs:
            npc_string = ""
            if npc.faction is not None:
                try:
                    npc_string += "[{}] - ".format(npc.faction.name)
                except:
                    npc_string += "[{}] - ".format(npc.faction)
            else:
                npc_string += "[ ] - "
            npc_string += "{}, {}".format(npc.name, npc.role)
            npcs.append(npc_string)

        return npcs

    def add_new_score(self, chat_id: int, user_id: int, score: dict):
        game = self.get_game_by_id(query_game_of_user(chat_id, user_id))

        pc_load = []
        for key in score["members"].keys():
            for elem in score["members"][key]:
                pc = elem
                load = score["members"][key][elem]

                game.get_player_by_id(key).get_character_by_name(pc).load = load
                pc_load.append((pc, load))

                update_user_characters(key, game.identifier, save_to_json(game.get_player_by_id(key).characters))
        score.pop("members")

        score["target"] = score["target"]["name"]

        # journal
        game.journal.write_score(**score, pc_load=pc_load)
        # game.journal.indentation += 1

        insert_journal(game.identifier, game.journal.get_log_string())

    def __repr__(self) -> str:
        return str(self.games)
