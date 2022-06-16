import copy
import threading

from bs4 import BeautifulSoup

from character.Ghost import Ghost
from character.Hull import Hull
from character.Human import Human
from character.Owner import Owner
from character.Vampire import Vampire
from component.Clock import Clock
from controller.DBreader import *
from controller.DBwriter import *
from game.Game import Game
from game.Player import Player
from game.Score import Score
from organization.Cohort import Cohort
from organization.Crew import Crew
from organization.Upgrade import Upgrade
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
                        friend = human.friend.name + ", " + human.friend.role
                        enemy = human.enemy.name + ", " + human.enemy.role
                        self.add_npc_to_game(friend, game)
                        self.add_npc_to_game(enemy, game)
                        user.characters.append(human)

                    insert_npc_json(game_id, save_to_json(game.NPCs))

                    insert_user_game(player_id, game_id, save_to_json(user.characters), user.is_master)
                    return

            # New user
            new_player = Player(query_users_names(player_id)[0], player_id, is_master)
            if human is not None:
                new_player.characters.append(human)
                friend = human.friend.name + ", " + human.friend.role
                enemy = human.enemy.name + ", " + human.enemy.role
                self.add_npc_to_game(friend, game)
                self.add_npc_to_game(enemy, game)
                insert_npc_json(game_id, save_to_json(game.NPCs))

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

        contact = game.crew.contact.name + ", " + game.crew.contact.role
        self.add_npc_to_game(contact, game)

        insert_npc_json(game_id, save_to_json(game.NPCs))
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

    def get_user_characters_names(self, user_id: int, chat_id: int, all_users: bool = False) -> List[str]:
        """
        Retrieves the list of the PCs' names, in the specified chat.

        :param all_users: if True, all the characters of the name are retrieved.
        :param user_id: the Telegram id of the user.
        :param chat_id: the Telegram chat id of the user.
        :return: a list of strings containing all the names.
        """

        game = self.get_game_by_id(query_game_of_user(chat_id, user_id))
        user = None
        if not all_users:
            user = user_id
        pcs = game.get_pcs_list(user)
        pcs_names = []
        for pc in pcs:
            pcs_names.append(pc.name)

        return pcs_names

    def get_pc_actions_ratings(self, user_id: int, chat_id: int, pc_name: str, attribute: str = None) \
            -> List[Tuple[str, int]]:
        """
        Retrieves all the action with the related rating of the specified PC of the user in the chat.

        :param attribute: if passed only the actions of the specified attribute are retrieved.
        :param user_id: the Telegram id of the user.
        :param chat_id: the Telegram chat id of the user.
        :param pc_name: the name of the target PC.
        :return: a list of tuples with the name of the action and the action's rating in this order.
        """
        game = self.get_game_by_id(query_game_of_user(chat_id, user_id))

        ratings = []
        pcs = game.get_pcs_list()
        for pc in pcs:
            if pc.name.lower() == pc_name.lower():
                for attr in pc.attributes:
                    if attribute == attr.name or attribute is None:
                        for action in attr.actions:
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
        """
        Retrieves the Journal's HTML file of the specified game as a bytes array
        and builds the file's name using the game's title.

        :param game_id: is the identifier of the game.
        :return: a Tuple that contains the bytes of the file and a string that represents its name.
        """
        game = self.get_game_by_id(game_id)

        return game.journal.read_journal(), ("Journal - " + game.title + ".html")

    def get_character_sheet_image(self, chat_id: int, user_id: int, pc_name: str) -> Tuple[bytes, str]:
        """
        Retrieves the PC's sheet PNG file of the specified PC as a bytes array
        and builds the file's name using the PC's name.

        :param chat_id: the Telegram id of the user who invoked the action roll.
        :param user_id: the Telegram chat id of the user.
        :param pc_name: the name of the target PC.
        :return: a Tuple that contains the bytes of the file and a string that represents its name.
        """
        game = self.get_game_by_id(query_game_of_user(chat_id, user_id))

        kwargs = {}
        if game.crew is not None:
            kwargs["crew_name"] = game.crew.name
        return game.get_player_by_id(user_id).get_character_by_name(pc_name).draw_image(**kwargs), (pc_name + ".png")

    def get_crew_sheet_image(self, game_id: int) -> Tuple[bytes, str]:
        """
        Retrieves the Crew's sheet PNG file of the specified game as a bytes array
        and builds the file's name using the Crew's name.

        :param game_id: id of the Game.
        :return: a Tuple that contains the bytes of the file and a string that represents its name.
        """
        game = self.get_game_by_id(game_id)
        return game.crew.draw_image(), (game.crew.name + ".png")

    def get_interactive_map(self, chat_id: int, user_id: int) -> Tuple[bytes, str]:
        """
        Retrieves the map's PNG file of the specified game as a bytes array
        and builds the file's name.

        :param chat_id: the Telegram id of the user who invoked the action roll.
        :param user_id: the Telegram chat id of the user.
        :return: a Tuple that contains the bytes of the file and a string that represents its name.
        """
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

        crew.crew_exp.add_points(-1)

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

    def get_healing_clock(self,  chat_id: int, user_id: int, pc_name: str) -> str:
        """
        Retrieves the healing clock of the selected PC

        :param chat_id: the Telegram id of the user who invoked the action roll.
        :param user_id: the Telegram chat id of the user.
        :param pc_name: the name of the active PC
        :return: the string representation of the healing clock
        """
        game = self.get_game_by_id(query_game_of_user(chat_id, user_id))
        clock = game.get_player_by_id(user_id).get_character_by_name(pc_name).healing
        return "{}: {}/{}".format(clock.name, clock.progress, clock.segments)

    def get_clocks_of_game(self, game_id: int, projects: bool = False) -> List[str]:
        """
        Retrieves the list of clocks of the specified game.

        :param projects: if True only the "project" clocks are retrieved.
        :param game_id: the game's id.
        :return: the list of clocks' names of the specified game
        """
        if projects:
            return ["{}: {}/{}".format(clock.name, clock.progress, clock.segments)
                    for clock in self.get_game_by_id(game_id).get_project_clocks()]
        else:
            return ["{}: {}/{}".format(clock.name, clock.progress, clock.segments)
                    for clock in self.get_game_by_id(game_id).clocks]

    def tick_clock_of_game(self, chat_id: int, user_id: int, old_clock: dict, ticks: int, write: bool = True) \
            -> Tuple[bool, dict]:
        """
        Advances the specified clock of the game, updates the database and write into the journal.

        :param write: if True a parapgraph is added to the journal.
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

        if write:
            game.journal.write_clock(query_users_names(user_id)[0], new_clock, clock_to_tick)

            insert_journal(game.identifier, game.journal.get_log_string())

        return filled, new_clock.__dict__

    def edit_clock_of_game(self, chat_id: int, user_id: int, pc_name: str, old_clock: dict, segments: int):
        game = self.get_game_by_id(query_game_of_user(chat_id, user_id))

        clock_to_edit = Clock(**old_clock)

        if "healing" in clock_to_edit.name.lower():
            player = game.get_player_by_id(user_id)
            player.get_character_by_name(pc_name).healing.edit(segments=segments)
            update_user_characters(user_id, game.identifier, save_to_json(player.characters))
        else:
            for clock in game.clocks:
                if clock_to_edit == clock:
                    clock.edit(segments=segments)
                    insert_clock_json(game.identifier, save_to_json(game.clocks))
                    break

    def add_claim_to_game(self, game_id: int, claim: dict):
        """
        Handles the addiction of a new Claim to the game's crew and write the information in the journal.

        :param game_id: is the identifier of the game.
        :param claim: dictionary that contains all the information needed.
        """
        game = self.get_game_by_id(game_id)

        new_claim = Claim(claim["name"], claim["description"])

        if claim["prison"]:
            game.crew.add_prison_claim(new_claim)
        else:
            game.crew.add_lair_claim(new_claim)

        insert_crew_json(game_id, save_to_json(game.crew))

        game.journal.write_add_claim(**claim)

        insert_journal(game.identifier, game.journal.get_log_string())

    def game_has_crew(self, game_id: int) -> bool:
        """
        Checks if the passed game has a Crew.

        :param game_id: is the identifier of the game.
        :return: True if a Crew exists, False otherwise
        """
        game = self.get_game_by_id(game_id)
        return game.crew is not None

    def get_cohorts_of_crew(self, chat_id: int, user_id: int, dead: bool = False,
                            elite: bool = True) -> List[Tuple[str, int]]:
        """
        Gives a list of tuple representing the cohorts of the specified crew.

        :param elite: if True the elite cohorts are included
        :param dead: states if the retrieved cohorts should be dead or not.
        :param chat_id: the Telegram id of the user who invoked the action roll.
        :param user_id: the Telegram chat id of the user.
        :return: a list of tuple with a string representing the cohort's types and an int representing its quality
        """
        crew = self.get_game_by_id(query_game_of_user(chat_id, user_id)).crew

        co = []
        for cohort in crew.cohorts:
            if (not dead and cohort.harm < 4) or (dead and cohort.harm >= 4):
                if elite or (not elite and not cohort.elite):
                    label = ""
                    if cohort.elite:
                        label += "💠"
                    if cohort.expert:
                        label += "[EXPERT] "
                    else:
                        label += "[GANG] "
                    label += cohort.type[0]
                    for i in range(1, len(cohort.type)):
                        label += ", "
                        label += cohort.type[i]

                    co.append((label, cohort.quality))

        return co

    def get_pc_attribute_rating(self, chat_id: int, user_id: int, pc_name: str) -> List[Tuple[str, int]]:
        """
        Retrieves all the attributes with the related rating of the specified PC of the user in the chat.

        :param chat_id: the Telegram chat id of the user.
        :param user_id: the Telegram id of the user.
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

    def get_pc_lifestyle(self, chat_id: int, user_id: int, pc_name: str) -> Optional[int]:
        """
        Gets the lifestyle of the selected pc.

        :param chat_id: the Telegram chat id of the user.
        :param user_id: the Telegram id of the user.
        :param pc_name: the name of the target PC.
        :return: None if the pc is not an owner, an int representing the lifestyle otherwise.
        """
        game = self.get_game_by_id(query_game_of_user(chat_id, user_id))

        pc = game.get_player_by_id(user_id).get_character_by_name(pc_name)
        if not isinstance(pc, Owner):
            return None
        return int(pc.stash / 10)

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
            if pc.name.lower() == resistance_roll["pc"].lower():
                traumas = pc.add_stress(stress)
                if traumas != 0:
                    trauma_victim = (pc.name, traumas)

        update_user_characters(user_id, game.identifier, save_to_json(game.get_player_by_id(user_id).characters))

        # journal

        game.journal.write_resistance_roll(**resistance_roll, stress=stress)

        insert_journal(game.identifier, game.journal.get_log_string())

        return trauma_victim

    def add_stress_to_pc(self, chat_id: int, user_id: int, pc_name: str, stress: int) -> Tuple[str, int]:
        """
        Adds the given stress to the selected pc of the user and updates the PCs in the DB.

        :param chat_id: the Telegram id of the user.
        :param user_id: the Telegram chat id of the user.
        :param pc_name: the name of the target PC.
        :param stress: the amount of stress to add.
        :return: a list of tuples with the name of the attribute and the attribute's rating in this order.
        """
        game = self.get_game_by_id(query_game_of_user(chat_id, user_id))

        trauma_victim = ()
        for pc in game.get_pcs_list(user_id):
            if pc.name.lower() == pc_name.lower():
                traumas = pc.add_stress(stress)
                if traumas != 0:
                    trauma_victim = (pc.name, traumas)

        update_user_characters(user_id, game.identifier, save_to_json(game.get_player_by_id(user_id).characters))

        return trauma_victim

    def get_pc_type(self, chat_id: int, user_id: int, pc_name: str) -> str:
        """
        Gets the type of the specified pc.

        :param chat_id: the Telegram id of the user.
        :param user_id: the Telegram chat id of the user.
        :param pc_name: the name of the target PC.
        :return: the name of the class
        """
        game = self.get_game_by_id(query_game_of_user(chat_id, user_id))

        for pc in game.get_pcs_list(user_id):
            if pc.name.lower() == pc_name.lower():
                return pc.__class__.__name__

    def add_trauma_to_pc(self, chat_id: int, user_id: int, pc_name: str, trauma: str) -> bool:
        """
        Adds the given trauma to the selected pc of the user and updates the PCs in the DB.

        :param chat_id: the Telegram id of the user.
        :param user_id: the Telegram chat id of the user.
        :param pc_name: the name of the target PC.
        :param trauma: the trauma to add.
        :return: True if the pc has suffered 4 or more traumas, False otherwise
        """
        game = self.get_game_by_id(query_game_of_user(chat_id, user_id))

        is_dead = False
        for pc in game.get_pcs_list(user_id):
            if pc.name.lower() == pc_name.lower():
                is_dead = pc.add_trauma(trauma)
        update_user_characters(user_id, game.identifier, save_to_json(game.get_player_by_id(user_id).characters))
        return is_dead

    def get_factions(self, game_id: int, faction_name: str = None) -> List[str]:
        """
        Gets the list with all the Faction for the specified game. Loads all the faction from the DB and checks, for
        every faction, if it's already present in the game's factions list. If present the faction of the game replaces
        the faction from the DB.

        :param faction_name: if specified, only this faction is retrieved
        :param game_id: represents the ID of the game.
        :return: a list of strings, each one composed by the actual status the players have with the faction, the name
            of the faction and the faction's tier level.
        """

        def get_faction_by_name(name: str, factions_list: List[Faction]) -> Faction:
            for elem in factions_list:
                if elem.name.lower() == name.lower():
                    return elem

        game = self.get_game_by_id(game_id)

        game_factions = game.factions
        db_factions = query_factions(faction_name)

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
        """
        Gets the list with all the NPCs for the specified game. Loads all the NPCs from the DB and checks, for
        every NPC, if it's already present in the game's NPCs list. If present the NPC of the game replaces
        the NPC from the DB.

        :param game_id: represents the ID of the game.
        :return: a list of strings, each one composed by the NPC's Faction's name (if it has a faction), the name
            of the NPC and its role.
        """

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
        """
        Adds a new score to the specified game's list. Calls the method to write the game's journal and updates the DB.

        :param chat_id: the Telegram id of the user.
        :param user_id: the Telegram chat id of the user.
        :param score: dictionary containing all the score's information.
        """
        game = self.get_game_by_id(query_game_of_user(chat_id, user_id))

        pc_load = []
        participants = []
        for key in score["members"].keys():
            for elem in score["members"][key]:
                pc = elem
                load = score["members"][key][elem]

                game.get_player_by_id(key).get_character_by_name(pc).load = load
                pc_load.append((pc, load))
                participants.append(pc)

                update_user_characters(key, game.identifier, save_to_json(game.get_player_by_id(key).characters))
        score.pop("members")

        if score["target"]["type"] == "NPC":
            target = self.add_npc_to_game(score["target"]["name"], game)
        elif score["target"]["type"] == "Faction":
            faction_name = score["target"]["name"].split(": ")[0]
            target = game.get_faction_by_name(faction_name)
            if target is None:
                target = query_factions(faction_name)[0]
                game.factions.append(target)
        else:
            target = score["target"]["name"]

        new_score = Score(score["title"], participants, target=target)
        new_score.calc_target_tier()
        game.scores.append(new_score)

        insert_score_json(game.identifier, save_to_json(game.scores))

        score["target"] = score["target"]["name"]

        # journal
        game.journal.write_score(**score, pc_load=pc_load)
        # game.journal.indentation += 1

        insert_journal(game.identifier, game.journal.get_log_string())

    def add_npc_to_game(self, npc: str, game: Game) -> NPC:
        name, role = npc.split(", ")
        target = game.get_npc_by_name_and_role(name, role)
        if target is None:
            target = query_npcs(name=name, role=role)[0]
            if target.faction is not None and isinstance(target.faction, str):
                npc_faction = game.get_faction_by_name(target.faction)
                if npc_faction is None:
                    npc_faction = query_factions(target.faction)[0]
                    game.factions.append(npc_faction)
                target.faction = npc_faction
            game.NPCs.append(target)
        return target

    def add_heat_to_crew(self, chat_id: int, user_id: int, heat: dict) -> int:
        """
        Applies the effect of the "heat" command to the game's crew and writes the new information in the journal.

        :param chat_id: the Telegram id of the user.
        :param user_id: the Telegram chat id of the user.
        :param heat: dictionary that contains the information needed.
        :return: the actual wanted level of the crew.
        """
        game = self.get_game_by_id(query_game_of_user(chat_id, user_id))
        wanted_level = game.crew.add_heat(heat["total_heat"])

        insert_crew_json(game.identifier, save_to_json(game.crew))

        game.journal.write_heat(**heat, wanted=wanted_level)

        insert_journal(game.identifier, game.journal.get_log_string())

        return wanted_level

    def get_crew_wanted_level(self, game_id: int):
        """
        Gets the crew's wanted level of the selected game.

        :param game_id: the game's id.
        """
        return self.get_game_by_id(game_id).crew.wanted_level

    def get_crew_heat(self, game_id: int):
        """
        Gets the crew's heat of the selected game.

        :param game_id: the game's id.
        """

        return self.get_game_by_id(game_id).crew.heat

    def commit_entanglement(self, game_id: int, entanglement: dict):
        """
        Writes in the journal of the specified game the new entanglement and updates the database.

        :param game_id: the game's id.
        :param entanglement:  dictionary containing all the necessary information about the entanglement.
        """
        game = self.get_game_by_id(game_id)

        secret = entanglement.pop("secret")

        if secret:
            game.journal.write_secret_entanglement(**entanglement)
        else:
            game.journal.write_entanglement(**entanglement)

        insert_journal(game.identifier, game.journal.get_log_string())

    def exists_score(self, chat_id: int, user_id: int) -> bool:
        """
        Checks if the game of the user has an active score.

        :param chat_id: the Telegram id of the user.
        :param user_id: the Telegram chat id of the user.
        :return: True if the game has at least one score, False otherwise.
        """
        game = self.get_game_by_id(query_game_of_user(chat_id, user_id))
        if game.scores:
            return True
        return False

    def get_last_score_rep(self, chat_id: int, user_id: int):
        """
        Gets the Rep that the crew should earn from the last added score.

        :param chat_id: the Telegram id of the user.
        :param user_id: the Telegram chat id of the user.
        :return: the amount of Rep.
        """
        game = self.get_game_by_id(query_game_of_user(chat_id, user_id))

        if len(game.scores) > 1:
            score = game.scores[-1]
        else:
            score = game.scores[0]

        return game.crew.calc_rep(score.target_tier)

    def end_score(self, chat_id: int, user_id: int, end_score: dict) -> int:
        """
        Close the last added score by removing it from the game's scores list.
        Calls the method to write the game's journal and updates the DB.

        :param chat_id: the Telegram chat id of the user.
        :param user_id: the Telegram id of the user.
        :param end_score: dictionary containing all the information of the score's closure.
        :return: the number of coin the players may spend to increase their crew's tier if they completed the Rep
                progress bar.
        """
        game = self.get_game_by_id(query_game_of_user(chat_id, user_id))

        if len(game.scores) > 1:
            game.scores.pop(-1)
        else:
            game.scores.pop(0)

        coin_to_pay = game.crew.add_rep(end_score["rep"])

        insert_score_json(game.identifier, save_to_json(game.scores))
        insert_crew_json(game.identifier, save_to_json(game.crew))
        for u in game.users:
            update_user_characters(u.player_id, game.identifier, save_to_json(u.characters))

        end_score.pop("rep")
        game.journal.write_end_score(**end_score)

        insert_journal(game.identifier, game.journal.get_log_string())

        return coin_to_pay if coin_to_pay is not None else 0

    def can_store_coins(self, game_id: int, coins: int) -> Tuple[bool, bool]:
        """
        Checks which method are available to handle the earned coins for the specified game.

        :param game_id: the game's id.
        :param coins: the number of coin to store.
        :return: a tuple of boolean value: the first one is True when the members can divvy the amount of coins among
            them, the second one is True when the coins can be stored in the crew's vault.
        """
        game = self.get_game_by_id(game_id)

        number_of_crew_members = len(game.get_owners_list())

        coin_per_member = int(coins / number_of_crew_members)
        exceed = coins % number_of_crew_members

        can_store_in_vault = True
        can_divvy = True
        for pc in game.get_owners_list():
            if not pc.can_store_coins(coin_per_member):
                can_divvy = False
                break

        if can_divvy and not game.crew.can_store(exceed):
            can_divvy = False
            can_store_in_vault = False

        if can_store_in_vault and not game.crew.can_store(coins):
            can_store_in_vault = False

        return can_divvy, can_store_in_vault

    def commit_payoff(self, game_id: int, payoff: dict):
        """
        Stores the coins earned with the selected method, writes in the journal of the specified game the new payoff and
        updates the database.

        :param game_id: the game's id.
        :param payoff:  dictionary containing all the necessary information about the payoff.
        """
        game = self.get_game_by_id(game_id)

        coins = payoff["amount"]

        if "distributed" in payoff:
            if payoff["distributed"]:
                number_of_crew_members = len(game.get_owners_list())
                coin_per_member = int(coins / number_of_crew_members)
                exceed = coins % number_of_crew_members

                for owner in game.get_owners_list():
                    owner.store_coins(coin_per_member)
                game.crew.add_coin(exceed)

                for user in game.users:
                    update_user_characters(user.player_id, game_id, save_to_json(user.characters))
            else:
                game.crew.add_coin(coins)

            insert_crew_json(game_id, save_to_json(game.crew))

        game.journal.write_payoff(**payoff)
        insert_journal(game.identifier, game.journal.get_log_string())

    def commit_armor_use(self, chat_id: int, user_id: int, armor_use: dict):
        """
        Calls use_armor method of the user's pc, commit the changes made to the journal and updates the database.

        :param chat_id: the Telegram chat id of the user.
        :param user_id: the Telegram id of the user.
        :param armor_use: dictionary containing all the information about the use of the armor.
        """
        game = self.get_game_by_id(query_game_of_user(chat_id, user_id))

        game.get_player_by_id(user_id).get_character_by_name(armor_use["pc"]).use_armor(armor_use["armor_type"])

        game.journal.write_armor_use(**armor_use)

        update_user_characters(user_id, game.identifier, save_to_json(game.get_player_by_id(user_id).characters))

        insert_journal(game.identifier, game.journal.get_log_string())

    def get_player_coins(self, chat_id: int, user_id: int, pc_name: str) -> \
            Union[Tuple[None, None, int], Tuple[int, int, int]]:
        """
        Gets the coins that compete with the selected user.

        :param chat_id: the Telegram id of the user.
        :param user_id: the Telegram chat id of the user.
        :param pc_name: the name of the user's active pc.
        :return: a Tuple with the coins of the pc (None if the active pc is not an Owner),
            the coins of the pc's stash (None if the active pc is not an Owner)
            and the coins from the crew vault (in this order).
        """
        game = self.get_game_by_id(query_game_of_user(chat_id, user_id))
        crew = game.crew

        if pc_name is None:
            return None, None, crew.coins

        pc = game.get_player_by_id(user_id).get_character_by_name(pc_name)

        if not isinstance(pc, Owner):
            return None, None, crew.coins

        return pc.coin, pc.stash, crew.coins

    def can_pay(self, chat_id: int, user_id: int, pc_name: str, coins_to_pay: int) -> Tuple[bool, bool]:
        """
        Checks if the passed PC, or his Crew, can pay the specified amount of coins.

        :param chat_id: the Telegram id of the user.
        :param user_id: the Telegram chat id of the user.
        :param pc_name: the name of the user's active pc.
        :param coins_to_pay: is the amount of coins to pay.
        :return: a Tuple of two boolean values: the first regards the crew, the second regards the PC's possessions.
        """
        pc_coins, pc_stash, crew_coins = self.get_player_coins(chat_id, user_id, pc_name)

        can_pay_pc = False
        can_pay_crew = False

        if pc_coins is not None and pc_stash is not None:
            pc_stash = int(pc_stash / 2)
            pc_possessions = pc_coins + pc_stash
            if pc_possessions >= coins_to_pay:
                can_pay_pc = True

        if crew_coins >= coins_to_pay:
            can_pay_crew = True

        return can_pay_crew, can_pay_pc

    def pay_with_possessions(self, chat_id: int, user_id: int, pc_name: str, coins_to_pay: int) -> bool:
        """
        Execute a payment of the specified amount of coins, using the PC's possessions.
        The priority order of retrieval is: coin, stash.
        Every coin counts double for the stash, according to the BitD rules.

        :param chat_id: the Telegram id of the user.
        :param user_id: the Telegram chat id of the user.
        :param pc_name: the name of the user's active pc.
        :param coins_to_pay: is the amount of coins to pay.
        :return: True if the payment was effected, False otherwise.
        """
        if self.can_pay(chat_id, user_id, pc_name, coins_to_pay)[1]:
            game = self.get_game_by_id(query_game_of_user(chat_id, user_id))
            pc = game.get_player_by_id(user_id).get_character_by_name(pc_name)

            if isinstance(pc, Owner):
                pc.pay_coins(coins_to_pay)
                return True
            return False
        return False

    def pay_with_crew(self, chat_id: int, user_id: int, pc_name: str, coins_to_pay: int) -> bool:
        """
        Execute a payment of the specified amount of coins, using the Crew's possessions.

        :param chat_id: the Telegram id of the user.
        :param user_id: the Telegram chat id of the user.
        :param pc_name: the name of the user's active pc.
        :param coins_to_pay: is the amount of coins to pay.
        :return: True if the payment was effected, False otherwise.
        """
        if self.can_pay(chat_id, user_id, pc_name, coins_to_pay)[0]:
            game = self.get_game_by_id(query_game_of_user(chat_id, user_id))
            crew = game.crew

            for i in range(coins_to_pay):
                if not crew.add_coin(-1):
                    return False
            return True
        return False

    def check_add_coin(self, chat_id: int, user_id: int, pc_name: str, where: str, coins: int) -> bool:
        """
        Checks if the selected pc can add the specified amount of coins.

        :param chat_id: the Telegram id of the user.
        :param user_id: the Telegram chat id of the user.
        :param pc_name: the name of the user's active pc.
        :param where: specifies where the coins should be stored (coins - stash - vault)
        :param coins: the amount of coins to add
        :return: True if the coins can be added in the selected location, False otherwise
        """
        game = self.get_game_by_id(query_game_of_user(chat_id, user_id))
        crew = game.crew

        if where == "vault":
            return crew.can_store(coins)

        elif pc_name is not None:
            pc = game.get_player_by_id(user_id).get_character_by_name(pc_name)
            if isinstance(pc, Owner):
                if where == "coins":
                    return pc.can_have_coins(coins)
                else:
                    return pc.can_stash_coins(coins)

        return False

    def commit_add_coin(self, chat_id: int, user_id: int, pc_name: str, add_coin: dict):
        """
        Adds (or remove) the selected amount of coins from the crew and/or the pc and updates the database.

        :param chat_id: the Telegram id of the user.
        :param user_id: the Telegram chat id of the user.
        :param pc_name: the name of the user's active pc.
        :param add_coin: dictionary with the information used to modify the coins
        """
        game = self.get_game_by_id(query_game_of_user(chat_id, user_id))

        crew = game.crew
        crew.add_coin(add_coin["vault"])

        if pc_name is not None:
            pc = game.get_player_by_id(user_id).get_character_by_name(pc_name)
            if isinstance(pc, Owner):
                pc.add_coins(add_coin["coins"])
                pc.stash_coins(add_coin["stash"])
                update_user_characters(user_id, game.identifier,
                                       save_to_json(game.get_player_by_id(user_id).characters))
        insert_crew_json(game.identifier, save_to_json(crew))

    def get_vault_capacity_of_crew(self, game_id: int) -> int:
        """
        Gets the vault capacity of the crew.

        :param game_id: identifier of the game.
        :return: an int representing the vault capacity.
        """
        game = self.get_game_by_id(game_id)

        return game.crew.vault_capacity

    def modify_vault_capacity(self, game_id: int, new_capacity: int):
        """
        Modifies the vault capacity of the specified game's crew by replacing the old value with the passed one.

        :param game_id: the game's id.
        :param new_capacity: is the new value of the vault's capacity.
        """
        game = self.get_game_by_id(game_id)

        crew = game.crew
        crew.vault_capacity = new_capacity

        if crew.coins > new_capacity:
            crew.coins = new_capacity

        insert_crew_json(game.identifier, save_to_json(crew))

    def upgrade_crew(self, game_id: int) -> Tuple[bool, int]:
        """
        Upgrades the crew increasing the tier by 1 or changing its hold.

        :param game_id: the game's id.
        :return: a tuple with the actual hold and the crew's tier.
        """
        game = self.get_game_by_id(game_id)

        if not game.crew.add_tier():
            game.crew.change_hold()
        else:
            coins = 2 + game.crew.tier
            for pc in game.get_owners_list():
                for i in range(coins):
                    pc.stash_coins(1)
            for user in game.users:
                update_user_characters(user.player_id, game_id, save_to_json(user.characters))
        insert_crew_json(game.identifier, save_to_json(game.crew))
        return game.crew.hold, game.crew.tier

    def update_factions_status(self, game_id: int, factions: dict):
        """
        Updates the game's factions' status. If the factions passed are not in the game list, their instances
        retrieved from the DB and added with the passed value.

        :param game_id: the game's id.
        :param factions: dictionary thet contains all the factions' names and their status to update.
        """

        def get_faction_by_name(name: str, factions_list: List[Faction]) -> Faction:
            for elem in factions_list:
                if elem.name.lower() == name.lower():
                    return elem

        game = self.get_game_by_id(game_id)

        for key in factions.keys():
            faction = get_faction_by_name(key, game.factions)
            if faction is None:
                game.factions.append(query_factions(name=key)[0])
                faction = get_faction_by_name(key, game.factions)

            faction.status = factions[key]

        insert_faction_json(game.identifier, save_to_json(game.factions))

    def get_pc_class(self, chat_id: int, user_id: int, pc_name: str) -> str:
        """
        Gets the class of the specified pc.

        :param chat_id: the Telegram id of the user.
        :param user_id: the Telegram chat id of the user.
        :param pc_name: the name of the target PC.
        :return: the name of the class
        """
        game = self.get_game_by_id(query_game_of_user(chat_id, user_id))
        pc = game.get_player_by_id(user_id).get_character_by_name(pc_name)
        if isinstance(pc, Human):
            return pc.pc_class
        else:
            return self.get_pc_type(chat_id, user_id, pc_name)

    def get_items(self, game_id: int, pc_class: str) -> List[Item]:
        """
        Gets all the list of items usable by a pc.

        :param game_id: the id of the game.
        :param pc_class: the class of the pc.
        :return: the list of items
        """
        items = query_items(pc_class=pc_class, canon=True)
        items += query_items(common_items=True)
        for item in items:
            item.quality = self.get_crew_tier(game_id)
        items += self.get_game_by_id(game_id).crafted_items
        return items

    def get_items_names(self, game_id: int, pc_class: str) -> List[Tuple[str, int]]:
        """
        Gets the names of all the usable items of a pc.

        :param game_id: the id of the game.
        :param pc_class: the class of the pc.
        :return: a list of tuple with a string representing the name of the item and an int which its quality.
        """
        return [(item.name, item.quality) for item in self.get_items(game_id, pc_class)]

    def get_item_by_name(self, game_id: int, pc_class: str, item_name: str) -> Item:
        """
        Gets a specific item given its name.

        :param game_id: the id of the game.
        :param pc_class: the class of the pc.
        :param item_name: name of the items.
        :return: the item
        """
        items = self.get_items(game_id, pc_class)
        for item in items:
            if item.name == item_name:
                return item

    def get_crew_tier(self, game_id: int) -> int:
        """
        Gets the tier of the crew.

        :param game_id: the id of the game.
        :return: the tier of the crew
        """
        return self.get_game_by_id(game_id).crew.tier

    def get_item_description(self, chat_id: int, user_id: int,
                             item_name: str, pc_name: str) -> Tuple[str, int, int, int]:
        """
        Gets the description of a given item

        :param pc_name:  name of the pc.
        :param chat_id: the Telegram chat id of the user.
        :param user_id: the Telegram id of the user.
        :param item_name: name of the item .
        :return: str representing the description of the item.
        """
        item = self.get_item_by_name(query_game_of_user(chat_id, user_id),
                                     self.get_pc_class(chat_id, user_id, pc_name), item_name)
        return item.description, item.weight, item.usages, item.quality

    def use_item(self, chat_id: int, user_id: int, use_item: dict) -> bool:
        """
        Calls the method use_item of the pc.

        :param chat_id: the Telegram chat id of the user.
        :param user_id: the Telegram id of the user.
        :param use_item: dictionary containing all the information about the use of the armor.
        :return: True if the item is used, False otherwise
        """
        game_id = query_game_of_user(chat_id, user_id)
        pc_class = self.get_pc_class(chat_id, user_id, use_item["pc"])
        pc = self.get_game_by_id(game_id).get_player_by_id(user_id).get_character_by_name(use_item["pc"])
        return pc.use_item(self.get_item_by_name(game_id, pc_class, use_item["item_name"]))

    def commit_use_item(self, game_id: int, user_id: int, use_item: dict):
        """
        Calls write_use_item and updates the database.

        :param game_id: the Telegram chat id of the user.
        :param user_id: the Telegram id of the user.
        :param use_item: dictionary containing all the information about the use of the armor.
        """
        self.get_game_by_id(game_id).journal.write_use_item(**use_item)
        insert_journal(game_id, self.get_game_by_id(game_id).journal.get_log_string())
        update_user_characters(user_id, game_id, save_to_json(
            self.get_game_by_id(game_id).get_player_by_id(user_id).characters))

    def commit_fortune_roll(self, game_id: int, fortune_roll: dict):
        """
        Writes in the game's journal about the fortune roll, then updates the databse.

        :param game_id: the game's id.
        :param fortune_roll: a dictionary with the info about the fortune roll
        """
        game = self.get_game_by_id(game_id)

        game.journal.write_fortune_roll(**fortune_roll)
        insert_journal(game.identifier, game.journal.get_log_string())

    def get_exp(self, chat_id: int, user_id: int, pc_name: str = None, specific: str = None) -> Union[dict, int]:
        """
        Gets the exp of the crew and the pc from the model.

        :param chat_id: the Telegram chat id of the user.
        :param user_id: the Telegram id of the user.
        :param pc_name: name of the pc.
        :param specific: name of the attribute whose exp is needed.
        :return: a dict with all the exp from the model or just a single one
        """
        game = self.get_game_by_id(query_game_of_user(chat_id, user_id))

        exp_dict = {"crew": game.crew.crew_exp.exp}

        if pc_name is not None:
            pc = game.get_player_by_id(user_id).get_character_by_name(pc_name)
            exp_dict["playbook"] = pc.playbook.exp
            for attr in pc.attributes:
                exp_dict[attr.name.lower()] = attr.exp

        if specific is None:
            return exp_dict

        return exp_dict[specific]

    def get_playbook_size(self, chat_id: int, user_id: int, pc_name: str = None, attribute: str = None) -> int:
        """
        Gets the max size of the playbook of each experience attribute from the model.

        :param chat_id: the Telegram chat id of the user.
        :param user_id: the Telegram id of the user.
        :param pc_name: name of the pc.
        :param attribute: name of the attribute whose exp limit is needed.
        :return: the exp limit for the requested attribute.
        """
        game = self.get_game_by_id(query_game_of_user(chat_id, user_id))

        if pc_name is None:
            return game.crew.crew_exp.exp_limit
        else:
            pc = game.get_player_by_id(user_id).get_character_by_name(pc_name)
            if attribute == "playbook":
                return pc.playbook.exp_limit
            else:
                return pc.get_attribute_by_name(attribute).exp_limit

    def commit_add_exp(self, chat_id: int, user_id: int, pc_name: str, add_exp: dict) -> List[Tuple[str, int]]:
        """
        Adds (or remove) the selected amount of exp from the crew and/or the pc and updates the database.

        :param chat_id: the Telegram chat id of the user.
        :param user_id: the Telegram id of the user.
        :param pc_name: the name of the user's active pc.
        :param add_exp: dictionary with the information used to modify the coins.
        :return: list of tuples containing the attributes whose points are increased and by how much.
        """
        game = self.get_game_by_id(query_game_of_user(chat_id, user_id))

        points = []

        crew = game.crew
        if crew.crew_exp.add_exp(add_exp["crew"]):
            points.append(("crew_points", crew.crew_exp.points))

        if pc_name is not None:
            pc = game.get_player_by_id(user_id).get_character_by_name(pc_name)
            if pc.playbook.add_exp(add_exp["playbook"]):
                points.append(("playbook_points", pc.playbook.points))
            for key in add_exp.keys():
                attr = pc.get_attribute_by_name(key)
                if attr:
                    if attr.add_exp(add_exp[key]):
                        points.append((key + "_points", attr.points))
            update_user_characters(user_id, game.identifier, save_to_json(game.get_player_by_id(user_id).characters))
        insert_crew_json(game.identifier, save_to_json(crew))

        return points

    def get_pc_points(self, chat_id: int, user_id: int, pc_name: str) -> dict:
        """
        Retrieves all the specified PC's points.

        :param chat_id: the Telegram chat id of the user.
        :param user_id: the Telegram id of the user.
        :param pc_name: the name of the user's active pc.
        :return: a dictionary where the keys are "Playbook", "Insight", "Prowess" and "Resolve" and the values are their
                available points.
        """
        game = self.get_game_by_id(query_game_of_user(chat_id, user_id))
        pc = game.get_player_by_id(user_id).get_character_by_name(pc_name)

        points_dict = {"Playbook": pc.playbook.points}
        for attribute in pc.attributes:
            points_dict[attribute.name.capitalize()] = attribute.points

        return points_dict

    def add_action_dots(self, chat_id: int, user_id: int, pc_name: str, new_actions_dict: dict, new_points_dict: dict):
        """
        Handles the addition and removal of the action dots of the specified PC. The new configuration of dots is
        evaluated via the subtraction of the configuration passed and the old configuration.
        This method handles the action points, too.

        :param chat_id: the Telegram chat id of the user.
        :param user_id: the Telegram id of the user.
        :param pc_name: the name of the user's active pc.
        :param new_actions_dict: represents the dictionary of all the PC's actions and their ratings.
        :param new_points_dict: represents the dictionary of all the PC's action points.
        """
        game = self.get_game_by_id(query_game_of_user(chat_id, user_id))
        pc = game.get_player_by_id(user_id).get_character_by_name(pc_name)

        pc_action_dots = self.get_pc_actions_ratings(user_id, chat_id, pc_name)
        old_action_dots = {}
        for elem in pc_action_dots:
            old_action_dots[elem[0].capitalize()] = elem[1]

        actions_to_add = {key: new_actions_dict[key] - old_action_dots.get(key, 0) for key in new_actions_dict}
        # Transforming the dict into a list of tuples
        action_dots = list(actions_to_add.items())
        for action in action_dots:
            pc.add_action_dots(*action)

        new_points_dict.pop("Playbook")
        for key in new_points_dict.keys():
            for attribute in pc.attributes:
                if key.lower() == attribute.name.lower():
                    attribute.points = new_points_dict[key]

        update_user_characters(user_id, game.identifier, save_to_json(game.get_player_by_id(user_id).characters))

    def get_crew_type(self, game_id: int) -> str:
        """
        Gets the type of the crew.

        :param game_id: identifier of the game
        :return: the crew type
        """
        return self.get_game_by_id(game_id).crew.type

    def get_crew_upgrade_points(self, game_id: int) -> int:
        """
        Gets the available upgrade points.

        :param game_id: identifier of the game
        :return: the upgrade points
        """
        return self.get_crew_exp_points(game_id) * 2

    def get_crew_exp_points(self, game_id: int) -> int:
        """
        Gets the available exp points of the crew.

        :param game_id: identifier of the game
        :return: the exp points
        """
        return self.get_game_by_id(game_id).crew.crew_exp.points

    def get_crew_upgrades(self, game_id: int) -> List[dict]:
        """
        Gets the upgrades the crew already has.

        :param game_id: identifier of the game
        :return: list of the dictionaries of the upgrades
        """
        upgrades = self.get_game_by_id(game_id).crew.upgrades
        upgrades_dict = []
        for upgrade in upgrades:
            upgrades_dict.append({"name": upgrade.name, "quality": upgrade.quality, "tot_quality": upgrade.tot_quality})
        return upgrades_dict

    def commit_add_upgrade(self, chat_id: int, user_id: int, upgrades: List[dict], upgrade_points: int):
        """
        Commits the changes made in the model and updates the database.

        :param chat_id: the Telegram chat id of the user.
        :param user_id: the Telegram id of the user.
        :param upgrades: list containing all the information about the upgrades.
        :param upgrade_points: remaining amount of upgrade points
        """
        def contains(temp):
            for up_dict in upgrades:
                if up_dict["name"] == temp["name"]:
                    return up_dict
            return None

        game = self.get_game_by_id(query_game_of_user(chat_id, user_id))
        crew = game.crew

        old_upgrades = self.get_crew_upgrades(game.identifier)

        for upgrade in old_upgrades:
            up = contains(upgrade)
            if up is not None:
                up["quality"] = up["quality"] - upgrade["quality"]
            else:
                upgrades.append(
                    {"name": upgrade["name"], "quality": -upgrade["quality"], "tot_quality": upgrade["tot_quality"]})

        for elem in upgrades:
            quality = elem["quality"]
            if quality > 0:
                for i in range(quality):
                    crew.add_upgrade(elem["name"])
            elif quality < 0:
                quality = -quality
                for i in range(quality):
                    crew.remove_upgrade(elem["name"])

        crew.crew_exp.points = int(upgrade_points / 2)

        insert_crew_json(game.identifier, save_to_json(crew))

    def has_pc_overindulged(self, chat_id: int, user_id: int, pc_name: str, roll_outcome: Union[int, str]) -> bool:
        """
        Checks if the selected pc has overindulged

        :param chat_id: the Telegram chat id of the user.
        :param user_id: the Telegram id of the user.
        :param pc_name: the name of the user's active pc.
        :param roll_outcome: the outcome of the roll during the downtime activity "indulge vice"
        :return: True if the pc has overindulged, False otherwise (or if he rolled a "CRIT")
        """
        game = self.get_game_by_id(query_game_of_user(chat_id, user_id))
        pc = game.get_player_by_id(user_id).get_character_by_name(pc_name)

        if isinstance(roll_outcome, int):
            return pc.stress_level - roll_outcome < 0
        else:
            return False

    def commit_downtime_activity(self, chat_id: int, user_id: int, downtime_info: dict) -> dict:
        """
        Applies the effects of the downtime activity passed: modifies the pc
        (and eventually the crew or the elements of the game) and updates the database

        :param chat_id: the Telegram chat id of the user.
        :param user_id: the Telegram id of the user.
        :param downtime_info: a dictionary containing the info of the activity
        :return: a dictionary containing the information that needs to be notified to the user
        """

        def payment(coins: int):
            if "payment" in downtime_info:
                if downtime_info["payment"] == 1:
                    self.pay_with_crew(chat_id, user_id, pc.name, coins)
                    insert_crew_json(game.identifier, save_to_json(game.crew))
                elif downtime_info["payment"] == 2:
                    self.pay_with_possessions(chat_id, user_id, pc.name, coins)

                downtime_info.pop("payment")

        game = self.get_game_by_id(query_game_of_user(chat_id, user_id))
        user = game.get_player_by_id(user_id)
        pc = user.get_character_by_name(downtime_info["pc"])

        activity = downtime_info["activity"]

        return_dict = {}

        if activity == "acquire_asset":
            payment(self.calc_coins_acquire_asset(
                downtime_info["quality"], downtime_info["extra_quality"], game.crew.tier))

        elif activity == "crafting":
            payment(downtime_info["extra_quality"])
            if downtime_info["quality"] + downtime_info["extra_quality"] >= downtime_info["minimum_quality"]:
                game.crafted_items.append(
                    Item(downtime_info["item"], downtime_info["item_description"],
                         quality=int(downtime_info["quality"]) + int(downtime_info["extra_quality"])))
                insert_crafted_item_json(game.identifier, save_to_json(game.crafted_items))

        elif activity == "long_term_project":
            ticks = self.calc_value_of_outcome(downtime_info["outcome"])
            downtime_info.pop("outcome")
            downtime_info["tick"] = ticks

            filled, new_clock = self.tick_clock_of_game(chat_id, user_id, downtime_info["clock"],
                                                        ticks, False)
            downtime_info["clock"] = Clock(**new_clock)
            if filled:
                return_dict["filled"] = downtime_info["clock"].name

        elif activity == "recover":
            traumas = 0
            if "npc" in downtime_info:
                self.add_npc_to_game(downtime_info["npc"], game)
                insert_npc_json(game.identifier, save_to_json(game.NPCs))
            elif "healer" in downtime_info:
                if downtime_info["healer"].split(":")[0].lower() == downtime_info["pc"].lower():
                    traumas = pc.add_stress(2)
            elif "cohort" in downtime_info:
                pass
            else:
                traumas = pc.add_stress(1)

            ticks = self.calc_value_of_outcome(downtime_info["outcome"])
            return_dict["time_healed"] = pc.tick_healing_clock(ticks)
            if traumas > 0:
                return_dict["traumas"] = traumas
            downtime_info["tick"] = ticks
            downtime_info["segments"] = pc.healing.segments
            downtime_info.pop("outcome")

        elif activity == "reduce_heat":
            heat = self.calc_value_of_outcome(downtime_info["outcome"])
            game.crew.add_heat(-heat)
            downtime_info["heat"] = heat
            insert_crew_json(game.identifier, save_to_json(game.crew))

        elif activity == "train":
            points = 1 + (
                    downtime_info["attribute"].lower() in [upgrade.name.lower() for upgrade in game.crew.upgrades])
            attr = pc.get_attribute_by_name(downtime_info["attribute"])
            if attr is None:
                pc.playbook.add_exp(points)
            else:
                attr.add_exp(points)
            downtime_info["points"] = points

        elif activity == "indulge_vice":
            if isinstance(downtime_info["outcome"], str):
                pc.stress_level = 0
            else:
                pc.clear_stress(downtime_info["outcome"])

            if "overindulge" in downtime_info:
                consequence = downtime_info["overindulge"]["consequence"]
                if consequence != "trouble":
                    downtime_info[consequence] = downtime_info["overindulge"]["notes"]
                downtime_info.pop("overindulge")
                if consequence == "brag":
                    return_dict["wanted_level"] = game.crew.add_heat(2)
                    insert_crew_json(game.identifier, save_to_json(game.crew))
                elif consequence == "lost":
                    pc.recover()
                elif consequence == "tapped":
                    if isinstance(pc, Owner):
                        pc.vice.remove_purveyor()
                else:
                    downtime_info["trouble"] = True

        elif activity == "help_cohort":
            cohorts_alive = []
            for cohort in game.crew.cohorts:
                if cohort.harm < 4:
                    cohorts_alive.append(cohort)
            cohort = cohorts_alive[downtime_info["cohort"]]
            cohort.add_harm(-2)
            downtime_info["cohort"] = self.get_cohorts_of_crew(chat_id, user_id)[downtime_info["cohort"]][0]
            downtime_info["harm"] = cohort.harm
            insert_crew_json(game.identifier, save_to_json(game.crew))

        elif activity == "replace_cohort":
            cohorts_dead = []
            for cohort in game.crew.cohorts:
                if cohort.harm >= 4:
                    cohorts_dead.append(cohort)
            cohort = cohorts_dead[downtime_info["cohort"]]
            cohort.harm = 0
            downtime_info["cohort"] = self.get_cohorts_of_crew(chat_id, user_id)[downtime_info["cohort"]][0]
            payment(game.crew.tier + 2)
            insert_crew_json(game.identifier, save_to_json(game.crew))

        pc.downtime_activities.append(activity)
        update_user_characters(user_id, game.identifier, save_to_json(user.characters))

        game.journal.write_activity(downtime_info)
        insert_journal(game.identifier, game.journal.get_log_string())
        return return_dict

    def calc_coins_acquire_asset(self, reached_quality: int, extra_quality: int, crew_tier: int) -> int:
        coins = extra_quality
        if reached_quality + extra_quality > crew_tier + 2:
            coins += reached_quality + extra_quality - (crew_tier + 2)
        return coins

    def calc_value_of_outcome(self, outcome: Union[int, str], values=None) -> int:
        if values is None:
            values = [5, 1, 2, 3]
        vCrit, v1, v2, v3 = values
        if isinstance(outcome, str):
            value = vCrit
        elif 1 <= outcome <= 3:
            value = v1
        elif 4 <= outcome <= 5:
            value = v2
        else:
            value = v3

        return value

    def get_crew_special_ability(self, chat_id: int, user_id: int) -> List[str]:
        """
        Gets the specific abilities for a given crew sheet.

        :param chat_id: the Telegram chat id of the user.
        :param user_id: the Telegram id of the user.
        :return: a list of str containing the names of the special abilities.
        """
        crew = self.get_game_by_id(query_game_of_user(chat_id, user_id)).crew
        crew_abilities = crew.abilities
        abilities_dict = []
        for ab in crew_abilities:
            abilities_dict.append(ab.__dict__)

        abilities = query_special_abilities(crew.type, as_dict=True)
        return self.remove_duplicate_abilities(abilities, abilities_dict)

    def remove_duplicate_abilities(self, abilities: List[dict], to_remove: List[dict]) -> List[str]:
        """
        Removes the abilities contained in to_remove from abilities.

        :param abilities: list containing all the abilities.
        :param to_remove: list containing the abilities to remove.
        :return: list of abilities cleaned from abilities in to_remove.
        """
        new_abilities = []
        for ability in abilities:
            if not to_remove.__contains__(ability):
                new_abilities.append(ability["name"])
        return new_abilities

    def get_pc_special_ability(self, chat_id: int, user_id: int, pc_name: str) -> List[str]:
        """
        Gets the specific abilities for a given character sheet.

        :param chat_id: the Telegram chat id of the user.
        :param user_id: the Telegram id of the user.
        :param pc_name: name of the pc used to find the character sheet.
        :return: a list of str containing the names of the special abilities.
        """
        game = self.get_game_by_id(query_game_of_user(chat_id, user_id))
        pc = game.get_player_by_id(user_id).get_character_by_name(pc_name)
        abilities_dict = []
        for ab in pc.abilities:
            abilities_dict.append(ab.__dict__)

        pc_abilities = query_special_abilities(self.get_pc_class(chat_id, user_id, pc_name), as_dict=True)
        abilities = self.remove_duplicate_abilities(pc_abilities, abilities_dict)

        if self.get_pc_type(chat_id, user_id, pc_name).casefold() != "Hull".casefold():
            abilities.append("Veteran")

        return abilities

    def is_vampire(self, chat_id: int, user_id: int, pc_name: str) -> bool:
        """
        Checks if your character is a Vampire.

        :param chat_id: the Telegram chat id of the user.
        :param user_id: the Telegram id of the user.
        :param pc_name: name of the pc used to find the character sheet.
        :return: True if the character is a Vampire, False otherwise.
        """
        game = self.get_game_by_id(query_game_of_user(chat_id, user_id))
        pc = game.get_player_by_id(user_id).get_character_by_name(pc_name)
        return isinstance(pc, Vampire)

    def is_hull(self, chat_id: int, user_id: int, pc_name: str) -> bool:
        """
        Checks if your character is a Hull.

        :param chat_id: the Telegram chat id of the user.
        :param user_id: the Telegram id of the user.
        :param pc_name: name of the pc used to find the character sheet.
        :return: True if the character is a Hull, False otherwise.
        """
        game = self.get_game_by_id(query_game_of_user(chat_id, user_id))
        pc = game.get_player_by_id(user_id).get_character_by_name(pc_name)
        return isinstance(pc, Hull)

    def get_all_abilities(self, chat_id: int, user_id: int, selection: int, pc_name: str) -> List[str]:
        """
        Method used to get all the special abilities for a character or crew.

        :param chat_id: the Telegram chat id of the user.
        :param user_id: the Telegram id of the user.
        :param selection: allows to get the abilities for character or crew.
        :param pc_name: name of the pc used to find the character sheet.
        :return: a list of str containing the names of the special abilities.
        """
        game = self.get_game_by_id(query_game_of_user(chat_id, user_id))
        if selection == 2:
            pc = game.get_player_by_id(user_id).get_character_by_name(pc_name)
            abilities = query_special_abilities(pc=True, as_dict=True)
            pc_abilities = pc.abilities
            abilities_dict = []
            for ab in pc_abilities:
                abilities_dict.append(ab.__dict__)
            return self.remove_duplicate_abilities(abilities, abilities_dict)
        elif selection == 1:
            crew = game.crew
            abilities = query_special_abilities(pc=False, as_dict=True)
            crew_abilities = crew.abilities
            abilities_dict = []
            for ab in crew_abilities:
                abilities_dict.append(ab.__dict__)
            return self.remove_duplicate_abilities(abilities, abilities_dict)

    def get_strictures(self, chat_id: int, user_id: int, pc_name: str) -> List[str]:
        """
        Method used to get all the strictures for a Vampire.

        :param chat_id: the Telegram chat id of the user.
        :param user_id: the Telegram id of the user.
        :param pc_name: name of the pc used to find the character sheet.
        :return: a list of str containing the names of the strictures.
        """
        game = self.get_game_by_id(query_game_of_user(chat_id, user_id))
        pc = game.get_player_by_id(user_id).get_character_by_name(pc_name)
        abilities = query_special_abilities(stricture=True, as_dict=True)
        pc_abilities = []
        if isinstance(pc, Vampire):
            pc_abilities = pc.strictures
        abilities_dict = []
        for ab in pc_abilities:
            abilities_dict.append(ab.__dict__)
        return self.remove_duplicate_abilities(abilities, abilities_dict)

    def get_frame_features(self, chat_id: int, user_id: int, pc_name: str) -> List[str]:
        """
        Method used to get all the frame features for a Hull.

        :param chat_id: the Telegram chat id of the user.
        :param user_id: the Telegram id of the user.
        :param pc_name: name of the pc used to find the character sheet.
        :return: a list of str containing the names of the frame features.
        """
        game = self.get_game_by_id(query_game_of_user(chat_id, user_id))
        pc = game.get_player_by_id(user_id).get_character_by_name(pc_name)
        abilities = []
        pc_abilities = []
        if isinstance(pc, Hull):
            abilities = query_special_abilities(frame_feature=pc.frame, as_dict=True)
            pc_abilities = pc.frame_features
        abilities_dict = []
        for ab in pc_abilities:
            abilities_dict.append(ab.__dict__)
        return self.remove_duplicate_abilities(abilities, abilities_dict)

    def commit_add_ability(self, chat_id: int, user_id: int, add_ability: dict, pc_name: str = None):
        """
        Commits the changes made in the model and updates the database.

        :param chat_id: the Telegram chat id of the user.
        :param user_id: the Telegram id of the user.
        :param add_ability: dict of the conversation.
        :param pc_name: name of the character to update the right pc from the model.
        """
        game = self.get_game_by_id(query_game_of_user(chat_id, user_id))

        if pc_name is not None:
            pc = game.get_player_by_id(user_id).get_character_by_name(pc_name)
            if add_ability["selection"] == 2:
                pc.abilities.append(query_special_abilities(special_ability=add_ability["ability"])[0])
                pc.playbook.points -= 1
            elif isinstance(pc, Vampire) and add_ability["selection"] == 3:
                pc.strictures.append(query_special_abilities(special_ability=add_ability["ability"])[0])
            elif isinstance(pc, Hull) and add_ability["selection"] == 4:
                pc.frame_features.append(query_special_abilities(special_ability=add_ability["ability"])[0])
            update_user_characters(user_id, game.identifier, save_to_json(game.get_player_by_id(user_id).characters))
        else:
            game.crew.abilities.append(query_special_abilities(special_ability=add_ability["ability"])[0])
            game.crew.crew_exp.points -= 1
            insert_crew_json(game.identifier, save_to_json(game.crew))

    def commit_add_cohort_harm(self, game_id: int, cohort_harm_info: dict):
        """
        Adds the given harm to the selected cohort and updates the crew in the DB.

        :param game_id: the id of the game.
        :param cohort_harm_info: a dictionary with the info used to add the harm
        """

        crew = self.get_game_by_id(game_id).crew

        cohorts_alive = []
        for cohort in crew.cohorts:
            if cohort.harm < 4:
                cohorts_alive.append(cohort)
        cohort = cohorts_alive[cohort_harm_info["cohort"]]
        cohort.add_harm(cohort_harm_info["harm"])

        insert_crew_json(game_id, save_to_json(crew))

    def commit_add_harm(self, chat_id: int, user_id: int, harm_info: dict) -> Optional[int]:
        """
        Adds the given harm to the selected pc and updates it in the DB.

        :param chat_id: the Telegram chat id of the user.
        :param user_id: the Telegram id of the user.
        :param harm_info: a dictionary with the info used to add the harm
        :return: an int representing the level where the harm is added if different from the one specified
        """
        game = self.get_game_by_id(query_game_of_user(chat_id, user_id))
        user = game.get_player_by_id(user_id)
        pc = user.get_character_by_name(harm_info["pc"])
        harm_info.pop("pc")
        level = pc.add_harm(**harm_info)

        update_user_characters(user_id, game.identifier, save_to_json(user.characters))

        if level != harm_info["level"]:
            return level

    def end_downtime(self, game_id: int) -> Dict[str, int]:
        """
        Applies the effects of the closure of the downtime activities.
        Adds to the PCs who didn't indulge their vice in downtime an amount of stress equals to the number of their
        trauma.

        :param game_id: identifier of the game
        :return: a dictionary where the keys are the name of the PCs who filled their stress bar and the values are the
                numbers of trauma they suffer.
        """
        game = self.get_game_by_id(game_id)

        trauma_suffers = {}
        for player in game.users:
            for pc in player.characters:
                if "indulge_vice" not in pc.downtime_activities:
                    trauma = pc.add_stress(len(pc.traumas))
                    if trauma > 0:
                        trauma_suffers[pc.name] = trauma
                        update_user_characters(player.player_id, game.identifier, save_to_json(player.characters))

        game.journal.write_end_downtime()

        insert_journal(game.identifier, game.journal.get_log_string())

        return trauma_suffers

    def change_vice_purveyor(self, chat_id: int, user_id: int, change_purveyor: Dict[str, str]):
        """
        Adds the new purveyor in to the vice of the pc of this user.

        :param chat_id: the Telegram chat id of the user.
        :param user_id: the Telegram id of the user.
        :param change_purveyor: dictionary that contains all the information needed (the PC's name and the new purveyor)
        """
        game = self.get_game_by_id(query_game_of_user(chat_id, user_id))
        pc = game.get_player_by_id(user_id).get_character_by_name(change_purveyor["pc"])
        if isinstance(pc, Human):
            pc.vice.add_purveyor(change_purveyor["new_purveyor"])

        update_user_characters(user_id, game.identifier, save_to_json(game.get_player_by_id(user_id).characters))

        game.journal.write_change_vice_purveyor(**change_purveyor)

        insert_journal(game.identifier, game.journal.get_log_string())

    def commit_pc_migration(self, chat_id: int, user_id: int, migration: Dict[str, str]):
        """
        Applies the effect of a PC migration to another type of Character.

        :param chat_id: the Telegram chat id of the user.
        :param user_id: the Telegram id of the user.
        :param migration: dictionary that contains all the information needed (the PC's name and the migration type)
        """
        game = self.get_game_by_id(query_game_of_user(chat_id, user_id))
        game.get_player_by_id(user_id).migrate_character_type(migration["pc"], migration["migration_pc"])

        pc = game.get_player_by_id(user_id).get_character_by_name(migration["pc"])
        if "ghost_enemies" in migration and isinstance(pc, Ghost):
            pc.enemies_rivals = migration["ghost_enemies"]
            migration.pop("ghost_enemies")
        if "hull_functions" in migration and isinstance(pc, Hull):
            pc.functions = migration["hull_functions"]
            migration.pop("hull_functions")

        update_user_characters(user_id, game.identifier, save_to_json(game.get_player_by_id(user_id).characters))

        game.journal.write_pc_migration(**migration)

    def add_rep_to_crew(self, game_id: int, reputation: int) -> Optional[int]:
        crew = self.get_game_by_id(game_id).crew
        coins = crew.add_rep(reputation)

        insert_crew_json(game_id, save_to_json(crew))
        return coins

    def commit_add_cohort_armor(self, game_id: int, cohort_armor_info: dict):
        """
        Adds the given armor to the selected cohort and updates the crew in the DB.

        :param game_id: the id of the game.
        :param cohort_armor_info: a dictionary with the info used to add the harm
        """
        game = self.get_game_by_id(game_id)
        crew = self.get_game_by_id(game_id).crew

        cohorts_alive = []
        for cohort in crew.cohorts:
            if cohort.harm < 4:
                cohorts_alive.append(cohort)
        cohort = cohorts_alive[cohort_armor_info["cohort"]]
        cohort.add_armor(cohort_armor_info["armor"])

        insert_crew_json(game_id, save_to_json(crew))
        insert_journal(game.identifier, game.journal.get_log_string())

    def commit_change_pc_class(self, chat_id: int, user_id: int, class_change: Dict[str, str]):
        """
        Applies the effect of a PC class change.

        :param chat_id: the Telegram chat id of the user.
        :param user_id: the Telegram id of the user.
        :param class_change: dictionary that contains all the information needed (the PC's name and the new class)
        """
        game = self.get_game_by_id(query_game_of_user(chat_id, user_id))
        game.get_player_by_id(user_id).change_character_class(class_change["pc"], class_change["new_class"])

        update_user_characters(user_id, game.identifier, save_to_json(game.get_player_by_id(user_id).characters))

        game.journal.write_change_pc_class(**class_change)

        insert_journal(game.identifier, game.journal.get_log_string())

    def retire(self, chat_id: int, user_id: int, retire: dict):
        """
        Remove the selected pc from the model, adds a tag in the journal and updates it in the DB.

        :param chat_id: the Telegram chat id of the user.
        :param user_id: the Telegram id of the user.
        :param retire: a dictionary with the info used to retire
        """
        game = self.get_game_by_id(query_game_of_user(chat_id, user_id))
        player = game.get_player_by_id(user_id)
        player.characters.remove(player.get_character_by_name(retire["pc"]))

        game.journal.write_retire(**retire)

        insert_journal(game.identifier, game.journal.get_log_string())

        update_user_characters(user_id, game.identifier, save_to_json(player.characters))

    def commit_flashback(self, chat_id: int, user_id: int, flashback: dict) -> Optional[int]:
        """
        Adds the stress to pay to the pc who is performing the flashback, then updates the database

        :param chat_id: the Telegram id of the user.
        :param user_id: the Telegram chat id of the user.
        :param flashback: a dictionary with the info of the flashback
        """
        game = self.get_game_by_id(query_game_of_user(chat_id, user_id))
        player = game.get_player_by_id(user_id)

        traumas = player.get_character_by_name(flashback["pc"]).add_stress(flashback["stress"])

        update_user_characters(user_id, game.identifier, save_to_json(player.characters))

        game.journal.write_flashback(**flashback)
        insert_journal(game.identifier, game.journal.get_log_string())

        if traumas > 0:
            return traumas

    def get_npcs_contacts(self, game_id: int) -> List[str]:
        """
        Get the NPCs that are friend, enemies or servants of the PCs of the crew, or the crew's contact.

        :param game_id: id of the Game.
        :return: a list of strings representing the name of the NPCs affiliated with the crew and its members.
        """
        game = self.get_game_by_id(game_id)

        contacts = {game.crew.contact.name + ", " + game.crew.contact.role}

        for pc in game.get_pcs_list():
            if isinstance(pc, Human):
                contacts.add(pc.friend.name + ", " + pc.friend.role)
                contacts.add(pc.enemy.name + ", " + pc.enemy.role)
            elif isinstance(pc, Vampire):
                for servant in pc.dark_servants:
                    contacts.add(servant.name + ", " + servant.role)

        return list(contacts)

    def commit_incarceration_roll(self, game_id: int, incarceration: dict) -> dict:
        """
        Applies the effects of the incarceration roll to the game: clears the crew's heat, reduces its wanted level, and
        depending on the roll result, increase the rep of the crew.

        :param game_id: id of the Game.
        :param incarceration: a dictionary containing the info about the roll
        :return: a dictionary (eventually an empty) with the some info used to notify the user of some changes .
        """
        game = self.get_game_by_id(game_id)

        crew = game.crew

        crew.clear_heat()
        crew.add_wanted_level(-1)
        return_dict = {}

        if isinstance(incarceration["outcome"], str):
            coins = crew.add_rep(3)
            return_dict["coins"] = coins
            return_dict["prison_claim"] = 1
            return_dict["status"] = 1
        elif incarceration["outcome"] == 6:
            return_dict["prison_claim"] = 1
            return_dict["status"] = 1
            insert_crew_json(game_id, save_to_json(crew))
        elif incarceration["outcome"] <= 3 and incarceration["type"] != "npc":
            return_dict["traumas"] = 1

        incarceration.pop("type")

        game.journal.write_incarceration(**incarceration)
        insert_journal(game.identifier, game.journal.get_log_string())

        return return_dict

    def commit_add_note(self, chat_id: int, user_id: int, add_note: dict):
        """
        Writes the new note in the journal and updates the database.

        :param chat_id: the Telegram chat id of the user.
        :param user_id: the Telegram id of the user.
        :param add_note: dictionary that contains all the information needed (note title and text).
        """
        game = self.get_game_by_id(query_game_of_user(chat_id, user_id))
        game.journal.write_note(**add_note)

        insert_journal(game.identifier, game.journal.get_log_string())

    def get_note(self, chat_id: int, user_id: int, position: int) -> str:
        """
        Gets the text of the note in the specified position.

        :param chat_id: the Telegram chat id of the user.
        :param user_id: the Telegram id of the user.
        :param position: position of the note.
        :return: the text of the note.
        """
        soup = BeautifulSoup(self.get_game_by_id(query_game_of_user(chat_id, user_id)).journal.read_note(position),
                             'html.parser')
        return soup.get_text()

    def commit_edit_note(self, chat_id: int, user_id: int, edit_note: dict):
        """
        Modifies the note in the journal in the given position and updates the database.

        :param chat_id: the Telegram chat id of the user.
        :param user_id: the Telegram id of the user.
        :param edit_note: dictionary that contains all the information needed (note position and new text).
        """
        game = self.get_game_by_id(query_game_of_user(chat_id, user_id))
        game.journal.edit_note(**edit_note)
        insert_journal(game.identifier, game.journal.get_log_string())

    def end_game(self, game_id: int, notes: str) -> List[Tuple[bytes, str]]:
        """
        Writes the final notes in the journal, sends the game files to the users,
        then Removes a game from the list of games and deletes it from the database.

        :param game_id: id of the Game.
        :param notes: final notes to write in the journal.
        :return: a list of Tuples that contains the bytes of the files and a string that represents their names.
        """
        game = self.get_game_by_id(game_id)

        game.journal.write_end_game(notes)
        insert_journal(game.identifier, game.journal.get_log_string())

        game_obj = [self.get_journal_of_game(game_id)]
        try:
            game_obj.append(self.get_crew_sheet_image(game_id))
        except:
            pass
        for user in game.users:
            for pc in user.characters:
                game_obj.append(self.get_character_sheet_image(game.chat_id, user.player_id, pc.name))

        delete_game(game_id)

        self.games.remove(game)

        return game_obj

    def commit_change_frame_size(self, chat_id: int, user_id: int, pc_name: str, frame_size: str):
        """
        Changes thhe frame size of the selected pc.

        :param pc_name: the name of the users' active pc
        :param frame_size: then selected frame size.
        :param chat_id: the Telegram chat id of the user.
        :param user_id: the Telegram id of the user.
        """

        game = self.get_game_by_id(query_game_of_user(chat_id, user_id))

        player = game.get_player_by_id(user_id)
        pc = player.get_character_by_name(pc_name)

        if isinstance(pc, Hull):
            pc.select_frame(frame_size)
            update_user_characters(user_id, game.identifier, save_to_json(player.characters))

    def is_pc_name_already_present(self, game_id: int, pc_name: str) -> bool:
        """
        Checks if the name selected is already taken by another pc in the game.

        :param game_id: the id of the game.
        :param pc_name: the name of the pc.
        :return: True if the name is already present, False otherwise
        """
        game = self.get_game_by_id(game_id)

        if pc_name.lower() in [pc.name.lower() for pc in game.get_pcs_list()]:
            return True
        return False

    def commit_add_cohort_type(self, game_id: int, cohort_type_info: dict):
        """
        Adds the given type to the selected cohort and updates the crew in the DB.

        :param game_id: the id of the game.
        :param cohort_type_info: a dictionary with the info used to add the harm
        """
        game = self.get_game_by_id(game_id)
        crew = self.get_game_by_id(game_id).crew

        cohorts_alive = []
        for cohort in crew.cohorts:
            if cohort.harm < 4:
                cohorts_alive.append(cohort)
        cohort = cohorts_alive[cohort_type_info["cohort"]]
        cohort.type.append(cohort_type_info["type"])

        crew.crew_exp.add_points(-1)

        insert_crew_json(game_id, save_to_json(crew))
        insert_journal(game.identifier, game.journal.get_log_string())

    def get_game_npcs(self, game_id: int) -> List[str]:
        game = self.get_game_by_id(game_id)
        return [npc.name + ", " + npc.role for npc in game.NPCs]

    def add_servant(self, chat_id: int, user_id: int, info: dict):
        """
        Adds a new dark servant to the selected pc.

        :param info: dictionary with the info about the new servant
        :param chat_id: the Telegram chat id of the user.
        :param user_id: the Telegram id of the user.
        """

        game = self.get_game_by_id(query_game_of_user(chat_id, user_id))

        player = game.get_player_by_id(user_id)
        pc = player.get_character_by_name(info["pc"])

        servant = self.add_npc_to_game(info["servant"], game)
        if isinstance(pc, Vampire):
            pc.dark_servants.append(servant)
            update_user_characters(user_id, game.identifier, save_to_json(player.characters))

        insert_npc_json(game.identifier, save_to_json(game.NPCs))

    def change_journal_language(self, game_id: int, lang: str):
        """
        Changes the journal language of the selected game and updates the database

        :param game_id: the game's id
        :param lang: the name of the file containing the language
        """
        game = self.get_game_by_id(game_id)

        game.journal.change_lang(lang)

        insert_lang(game_id, lang)

    def promote_cohort_of_crew(self, game_id: int, cohort_index: int):
        """
        Set the selected cohort to elite and updates the database.

        :param game_id: the game's id
        :param cohort_index: int representing the cohort to promote
        """
        crew = self.get_game_by_id(game_id).crew

        not_elite_cohorts = []
        for cohort in crew.cohorts:
            if not cohort.elite:
                not_elite_cohorts.append(cohort)

        not_elite_cohorts[cohort_index].elite = True

        insert_crew_json(game_id, save_to_json(crew))

    def __repr__(self) -> str:
        return str(self.games)
