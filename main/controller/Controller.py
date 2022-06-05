import copy
import threading

from character.Human import Human
from character.Owner import Owner
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

        game.journal.write_add_claim(**claim)

        insert_journal(game.identifier, game.journal.get_log_string())

    def game_has_crew(self, game_id: int) -> bool:
        game = self.get_game_by_id(game_id)
        return game.crew is not None

    def get_cohorts_of_crew(self, chat_id: int, user_id: int, dead: bool = False) -> List[Tuple[str, int]]:
        """
        Gives a list of tuple representing the cohorts of the specified crew.

        :param dead: states if the retrieved cohorts should be dead or not.
        :param chat_id: the Telegram id of the user who invoked the action roll.
        :param user_id: the Telegram chat id of the user.
        :return: a list of tuple with a string representing the cohort's types and an int representing its quality
        """
        crew = self.get_game_by_id(query_game_of_user(chat_id, user_id)).crew

        co = []
        for cohort in crew.cohorts:
            if (not dead and cohort.harm < 4) or (dead and cohort.harm >= 4):
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
        return int(pc.stash/10)

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
            name, role = score["target"]["name"].split(", ")
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

    def add_heat_to_crew(self, chat_id: int, user_id: int, heat: dict) -> int:
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
                update_user_characters(user_id, game.identifier, save_to_json(game.get_player_by_id(user_id).characters))
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
        :return: a list of tuple with a string representing the name of the item and an int which is its quality.
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
                        points.append((key+"_points", attr.points))
            update_user_characters(user_id, game.identifier, save_to_json(game.get_player_by_id(user_id).characters))
        insert_crew_json(game.identifier, save_to_json(crew))

        return points

    def get_pc_points(self, chat_id: int, user_id: int, pc_name: str) -> dict:
        game = self.get_game_by_id(query_game_of_user(chat_id, user_id))
        pc = game.get_player_by_id(user_id).get_character_by_name(pc_name)

        points_dict = {"Playbook": pc.playbook.points}
        for attribute in pc.attributes:
            points_dict[attribute.name.capitalize()] = attribute.points

        return points_dict

    def add_action_dots(self, chat_id: int, user_id: int, pc_name: str, new_actions_dict: dict, new_points_dict: dict):
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
        return self.get_game_by_id(game_id).crew.crew_exp.points*2

    def get_crew_upgrades(self, game_id: int) -> List[dict]:
        """
        Gets the upgrades the crew already has.

        :param game_id: identifier of the game
        :return: list of the dictionaries of the upgrades
        """
        upgrades = self.get_game_by_id(game_id).crew.upgrades
        upgrades_dict = []
        for upgrade in upgrades:
            upgrades_dict.append({"name": upgrade.name, "quality": upgrade.quality})
        return upgrades_dict

    def commit_add_upgrade(self, chat_id: int, user_id: int, upgrades: dict, upgrade_points: int):
        """
        Commits the changes made in the model and updates the database.
        :param chat_id: the Telegram chat id of the user.
        :param user_id: the Telegram id of the user.
        :param upgrades: dict containing all the information about the upgrades.
        :param upgrade_points: remaining amount of upgrade points
        """
        game = self.get_game_by_id(query_game_of_user(chat_id, user_id))
        crew = game.crew
        for upgrade in upgrades:
            upg = Upgrade(**upgrade)
            if not crew.upgrades.__contains__(upg):
                crew.upgrades.append(upg)

        crew.crew_exp.points = int(upgrade_points/2)

        insert_crew_json(game.identifier, save_to_json(crew))

    def has_pc_overindulged(self, chat_id: int, user_id: int, pc_name: str, roll_outcome: Union[int, str]) -> bool:
        """
        Checks if the selected pc has overindulged

         :param chat_id: the Telegram id of the user.
        :param user_id: the Telegram chat id of the user.
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

    def __repr__(self) -> str:
        return str(self.games)
