import copy

from telegram.utils import helpers
from bot.BotUtils import *
from utility import DiceRoller


def start(update: Update, context: CallbackContext) -> None:
    """
    Welcomes the user sending him messages with credits and the bot's starting instruction.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    """
    placeholders = get_lang(context, start.__name__)

    update.message.reply_text(placeholders["0"])
    update.message.reply_text(placeholders["1"].format("©"))
    update.message.reply_text(placeholders["2"])


def help_msg(update: Update, context: CallbackContext) -> None:
    """
    Sends the help messages (the full help section or a specific description specified in the context).

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    """
    placeholders = get_lang(context, help_msg.__name__)

    if not context.args:
        update.message.reply_text(placeholders["default"]["0"], parse_mode=ParseMode.HTML)
        for i in range(1, len(placeholders["default"])):
            update.message.reply_text(placeholders["default"][str(i)], parse_mode=ParseMode.HTML, quote=False)
    else:
        try:
            update.message.reply_text(placeholders["commands"][context.args[0].lower()], parse_mode=ParseMode.HTML)
        except:
            auto_delete_message(update.message.reply_text(placeholders["commands"]["error"].format(context.args[0]),
                                                          parse_mode=ParseMode.HTML))


def start_login(update: Update, context: CallbackContext) -> None:
    """
    Sets up the login phase by sending the user aaa clickable message with a special payload.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    """
    placeholders = get_lang(context, start_login.__name__)

    url = helpers.create_deep_linked_url(context.bot.username, "login-BladesInTheDark-BotTelegram")

    update.effective_chat.send_message(
        placeholders["0"].format(url),
        reply_to_message_id=update.message.message_id, parse_mode=ParseMode.HTML)


# ------------------------------------------conv_login------------------------------------------------------------------
def login(update: Update, context: CallbackContext) -> int:
    """
    Handles the user's login by checking if he is already registered

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: next conversation's state.
    """

    placeholders = get_lang(context, login.__name__)

    update.message.delete()

    if not exists_user(get_user_id(update)):
        update.message.reply_text(placeholders["0"])
    else:
        update.message.reply_text(placeholders["1"])

    return 0


def login_receive_username(update: Update, context: CallbackContext) -> int:
    """
    Registers the user's username.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: ConversationHandler.END.
    """
    placeholders = get_lang(context, login_receive_username.__name__)

    if insert_user(get_user_id(update), update.message.text):
        update.message.reply_text(placeholders["0"])
    else:
        update.message.reply_text(placeholders["1"])

    return ConversationHandler.END


# ------------------------------------------conv_login------------------------------------------------------------------

# ------------------------------------------conv_createPC---------------------------------------------------------------

def create_pc(update: Update, context: CallbackContext) -> int:
    """
    Handles the creation of a PC checking if the user is already registered.
    It builds the inline keyboard that will be used during conv_createPC.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: next conversation's state.
    """
    if not user_is_registered(update, context):
        return ConversationHandler.END

    placeholders = get_lang(context, create_pc.__name__)
    user_id = get_user_id(update)

    url = helpers.create_deep_linked_url(context.bot.username)

    if update.message.chat.type != "private":
        update.effective_chat.send_message(placeholders["0"].format(query_users_names(get_user_id(update))[0], url),
                                           reply_to_message_id=update.message.message_id,
                                           parse_mode=ParseMode.HTML)

    query_menu = update.message.bot.sendMessage(text=placeholders["1"], chat_id=user_id,
                                                reply_markup=custom_kb(placeholders["keyboard"],
                                                                       inline=True, split_row=3))

    context.user_data.setdefault("create_pc", {})["keyboard"] = copy.deepcopy(placeholders["keyboard"])
    context.user_data["create_pc"]["pc"] = {}
    context.user_data["create_pc"]["query_menu"] = query_menu

    return 0


def create_pc_state_switcher(update: Update, context: CallbackContext) -> int:
    """
    Handles the callback query from the Inline keyboard by redirecting the user in the correct state of the creation
    and sending him the associated message.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: next conversation's state.
    """
    placeholders = get_lang(context, create_pc_state_switcher.__name__)
    keyboards = placeholders["keyboards"]

    keyboards.append(query_character_sheets(canon=True, spirit=False))

    vices = []
    for vice in query_vice(as_dict=True, character_class="Human"):
        if isinstance(vice, dict):
            vices.append(vice["name"])
    keyboards.append(vices)

    return query_state_switcher(update, context, "create_pc", placeholders, keyboards)


def create_pc_name(update: Update, context: CallbackContext) -> int:
    """
    Sends the btn_label associated with this state ("name") to store_value_and_update_kb method.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.:
    :return: the state of the conversation switcher.
    """
    placeholders = get_lang(context, create_pc_name.__name__)
    if update.message.text.lower() in get_user_pc(context):
        auto_delete_message(update.message.reply_text(placeholders["0"].format(update.message.text),
                                                      parse_mode=ParseMode.HTML), 8.0)
    store_value_and_update_kb(update, context, tags=["create_pc", "pc", "name"], value=update.message.text, split_row=3)
    update.message.delete()

    return 0


def create_pc_alias(update: Update, context: CallbackContext) -> int:
    """
    Sends the btn_label associated with this state ("alias") to store_value_and_update_kb method.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.:
    :return: the state of the conversation switcher.
    """
    store_value_and_update_kb(update, context, tags=["create_pc", "pc", "alias"],
                              value=update.message.text, split_row=3)
    update.message.delete()

    return 0


def create_pc_look(update: Update, context: CallbackContext) -> int:
    """
    Sends the btn_label associated with this state ("look") to store_value_and_update_kb method.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.:
    :return: the state of the conversation switcher.
    """
    store_value_and_update_kb(update, context, tags=["create_pc", "pc", "look"], value=update.message.text, split_row=3)
    update.message.delete()

    return 0


def create_pc_heritage(update: Update, context: CallbackContext) -> int:
    """
    Sends the btn_label associated with this state ("heritage") to store_value_and_update_kb method.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.:
    :return: the state of the conversation switcher.
    """
    store_value_and_update_kb(update, context, tags=["create_pc", "pc", "heritage"],
                              value=update.message.text, split_row=3)
    update.message.delete()

    return 0


def create_pc_background(update: Update, context: CallbackContext) -> int:
    """
    Sends the btn_label associated with this state ("background") to store_value_and_update_kb method.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.:
    :return: the state of the conversation switcher.
    """
    store_value_and_update_kb(update, context, tags=["create_pc", "pc", "background"],
                              value=update.message.text, split_row=3)
    update.message.delete()

    return 0


def create_pc_vice_name(update: Update, context: CallbackContext) -> int:
    """
    Stores the vice name in the user_data and advances the conversation to
    the next state that regards the description of vice.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.:
    :return: the next state of the conversation.
    """
    context.user_data["create_pc"]["message"].delete()

    add_tag_in_telegram_data(context, ["create_pc", "pc", "vice", "name"], update.message.text)

    placeholders = get_lang(context, create_pc_vice_name.__name__)

    context.user_data["create_pc"]["message"] = update.message.reply_text(placeholders["0"])
    update.message.delete()

    return 9


def create_pc_vice_description(update: Update, context: CallbackContext) -> int:
    """
    Stores the vice description in the user_data and advances the conversation to
    the next state that regards the description of vice.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.:
    :return: the next state of the conversation.
    """
    add_tag_in_telegram_data(context, ["create_pc", "pc", "vice", "description"], update.message.text)

    placeholders = get_lang(context, create_pc_vice_description.__name__)

    context.user_data["create_pc"]["message"].edit_text(placeholders["0"])
    update.message.delete()

    return 10


def create_pc_vice_purveyor(update: Update, context: CallbackContext) -> int:
    """
    Sends the tags associated with this state ("vice" and "purveyor") to store_value_and_update_kb method.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.:
    :return: the state of the conversation switcher.
    """
    store_value_and_update_kb(update, context, tags=["create_pc", "pc", "vice", "purveyor"],
                              value=update.message.text, btn_label="vice", split_row=3)
    update.message.delete()

    return 0


def create_pc_description(update: Update, context: CallbackContext) -> int:
    """
    Sends the btn_label associated with this state ("description") to store_value_and_update_kb method.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.:
    :return: the state of the conversation switcher.
    """
    store_value_and_update_kb(update, context, tags=["create_pc", "pc", "description"],
                              value=update.message.text, btn_label="notes", split_row=3)
    update.message.delete()

    return 0


def create_pc_class(update: Update, context: CallbackContext) -> int:
    """
    Calls a DBmanager method to check if the received class exists and, if so,
    sends the btn_label associated with this state ("class") to store_value_and_update_kb method.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the state of the conversation switcher.
    """
    placeholders = get_lang(context, create_pc_class.__name__)

    if exists_character(update.message.text):
        store_value_and_update_kb(update, context, tags=["create_pc", "pc", "pc_class"],
                                  value=update.message.text, btn_label="class", split_row=3)
        update.message.delete()

        return 0
    else:
        invalid_state_choice(update, context, "create_pc", placeholders)
        return 7


def create_pc_end(update: Update, context: CallbackContext) -> int:
    """
    Ends the conversation when /done or /cancel is received.
    If /done it check if all the necessary fields of the conversation have been filled and, if so,
    it stores the completed PC in the user_data.
    If /cancel it deletes the information collected so far.
    In any case, it exits the conversation.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: ConversationHandler.END.
    """
    command = update.message.text
    placeholders = get_lang(context, create_pc_end.__name__)

    dict_create_pc = context.user_data["create_pc"]

    if "done".casefold() in command:
        if {"name", "alias", "look", "heritage", "background", "pc_class", "vice"}.issubset(
                dict_create_pc["pc"].keys()):
            add_tag_in_telegram_data(context, tags=["myPCs", dict_create_pc["pc"]["name"].lower()],
                                     value=dict_create_pc["pc"])
        else:
            auto_delete_message(update.message.reply_text(placeholders["0"]))
            update.message.delete()
            return 0

    delete_conv_from_telegram_data(context, "create_pc")

    return end_conv(update, context)


# ------------------------------------------conv_createPC---------------------------------------------------------------


# ------------------------------------------conv_createGame-------------------------------------------------------------

def create_game(update: Update, context: CallbackContext) -> int:
    """
    Handles the creation of a Game checking if the user is already registered.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: next conversation's state.
    """
    if not user_is_registered(update, context):
        return ConversationHandler.END

    placeholders = get_lang(context, create_game.__name__)
    context.user_data.setdefault("create_game", {})["message"] = update.message.reply_text(placeholders["0"])

    return 0


def create_game_title(update: Update, context: CallbackContext) -> int:
    """
    Handles the choice of the Game's title and adds it to the Controller's games list

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: ConversationHandler.END
    """
    placeholders = get_lang(context, create_game_title.__name__)

    for d in query_games_info(update.message.chat_id):
        if update.message.text.lower() == d["title"].lower():
            context.user_data.setdefault("create_game", {})["message"] = update.message.reply_text(
                placeholders["1"].format(update.message.text), parse_mode=ParseMode.HTML)
            return 0

    game_id = controller.add_game(update.message.chat_id, update.message.text)

    update.message.reply_text(placeholders["0"].format(update.message.text, game_id), parse_mode=ParseMode.HTML,
                              quote=False)

    delete_conv_from_telegram_data(context, "create_game")
    return end_conv(update, context)


# ------------------------------------------conv_createGame-------------------------------------------------------------


# ------------------------------------------conv_join-------------------------------------------------------------------


def join(update: Update, context: CallbackContext) -> int:
    """
    Retrieves all the game available for the chat of invocation.
    Checks if the user is registered.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    if not user_is_registered(update, context):
        return ConversationHandler.END

    placeholders = get_lang(context, join.__name__)

    titles = []
    for elem in query_games_info(update.message.chat_id):
        titles.append(elem["title"])

    if not titles:
        update.message.reply_text(placeholders["1"])
        return ConversationHandler.END

    context.user_data.setdefault("join", {})["message"] = update.message.reply_text(placeholders["0"],
                                                                                    reply_markup=custom_kb(titles))
    context.user_data["join"]["invocation_message"] = update.message

    return 0


def join_game_name(update: Update, context: CallbackContext) -> int:
    """
    Handles the game selected by the user by checking if is valid.
    If the game exists it sends the ReplyKeyboard with the list of the user's PCs and the option to join as Master.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, join_game_name.__name__)
    context.user_data["join"]["message"].delete()

    titles = []
    for elem in query_games_info(update.message.chat_id):
        titles.append(elem["title"])

    if update.message.text not in titles:
        auto_delete_message(update.message.reply_text(placeholders["0"].format(update.message.text),
                                                      parse_mode=ParseMode.HTML), 10)

        update.message.delete()
        return ConversationHandler.END

    game_of_user = query_game_of_user(update.message.chat_id, get_user_id(update))
    if game_of_user is not None and game_of_user != query_game_ids(update.message.chat_id, update.message.text)[0]:
        auto_delete_message(update.message.reply_text(placeholders["2"].format(
            query_games_info(game_id=game_of_user)[0]["title"]),
            parse_mode=ParseMode.HTML, quote=False), 10)

        update.message.delete()
        return ConversationHandler.END

    context.user_data["join"]["game_name"] = update.message.text

    buttons = get_user_pc(context)
    buttons.append("as Master")
    context.user_data["join"]["message"] = context.user_data["join"]["invocation_message"].reply_text(
        placeholders["1"], reply_markup=custom_kb(buttons))

    update.message.delete()
    return 1


def join_add_player(update: Update, context: CallbackContext) -> int:
    """
    Checks the validity of user's selection.
    If the user's choice is to join "as Master", his necessary data are forwarded to update_user_in_game method
    of the controller.
    If the user decides to join as a player, the conversation goes on with the completion phase of the selected PC.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation (end_conv() if the user joins as Master).
    """
    placeholders = get_lang(context, join_add_player.__name__)
    context.user_data["join"]["message"].delete()

    if update.message.text not in get_user_pc(context) and update.message.text.lower() != "as master":
        update.message.delete()
        buttons = get_user_pc(context)
        buttons.append("as Master")
        context.user_data["join"]["message"] = context.user_data["join"]["invocation_message"].reply_text(
            placeholders["err"], reply_markup=custom_kb(buttons))
        return 1

    if controller.is_pc_name_already_present(
            query_game_ids(update.message.chat_id, context.user_data["join"]["game_name"])[0], update.message.text):
        update.message.delete()
        buttons = get_user_pc(context)
        buttons.append("as Master")
        context.user_data["join"]["message"] = context.user_data["join"]["invocation_message"].reply_text(
            placeholders["err2"], reply_markup=custom_kb(buttons))
        return 1

    if update.message.text.lower() == "as master":
        controller.update_user_in_game(get_user_id(update), update.message.chat_id,
                                       context.user_data["join"]["game_name"], True)

        update.message.reply_text(placeholders["0"].format(query_users_names(get_user_id(update))[0],
                                                           context.user_data["join"]["game_name"]),
                                  parse_mode=ParseMode.HTML,
                                  quote=False)
        delete_conv_from_telegram_data(context, "join")
        return end_conv(update, context)
    else:

        context.user_data["join"]["pc"] = {}
        context.user_data["join"]["pc"].update(context.user_data["myPCs"][update.message.text.lower()])

        context.user_data["join"]["chat_id"] = update.message.chat_id

        join_complete_pc(update, context)
        return 2


def join_complete_pc(update: Update, context: CallbackContext):
    """
    Redirects the user in his private chat by sending him a clickable link if the conversation started in a group chat,
    and sends him the Inline Keyboard for the PC's attribute selection.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    """
    placeholders = get_lang(context, join_complete_pc.__name__)
    user_id = get_user_id(update)

    url = helpers.create_deep_linked_url(context.bot.username)

    if update.message.chat.type != "private":
        update.effective_chat.send_message(placeholders["0"].format(query_users_names(get_user_id(update))[0],
                                                                    context.user_data["join"]["pc"]["name"], url),
                                           parse_mode=ParseMode.HTML)

    query_menu = update.message.bot.sendMessage(text=placeholders["1"], chat_id=user_id,
                                                reply_markup=custom_kb(placeholders["keyboard"],
                                                                       inline=True, split_row=2))

    context.user_data.setdefault("join", {})["keyboard"] = copy.deepcopy(placeholders["keyboard"])
    context.user_data["join"]["query_menu"] = query_menu

    update.message.delete()


def join_complete_pc_state_switcher(update: Update, context: CallbackContext) -> int:
    """
    Handles the callback query from the Inline keyboard by redirecting the user in the correct state of the completion
    and sending him the associated message.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: next conversation's state.
    """
    placeholders = get_lang(context, join_complete_pc_state_switcher.__name__)

    keyboards = []

    abilities = []
    for ability in query_special_abilities(sheet=context.user_data["join"]["pc"]["pc_class"], as_dict=True):
        if isinstance(ability, dict):
            abilities.append(ability["name"])
    keyboards.append(abilities)

    keyboards.append(query_attributes(only_names=True))

    strange_friends = []
    for npc in query_char_strange_friends(pc_class=context.user_data["join"]["pc"]["pc_class"], as_dict=True):
        if isinstance(npc, dict):
            strange_friends.append(npc["name"] + ", " + npc["role"])
    keyboards.append(strange_friends)
    keyboards.append(strange_friends)

    return query_state_switcher(update, context, "join", placeholders, keyboards, index_inlines=[1], starting_state=3)


def join_complete_pc_ability(update: Update, context: CallbackContext) -> int:
    """
    If the user chooses a valid option, sends the information associated with this state ("ability")
    to store_value_and_update_kb method.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.:
    :return: the state of the conversation switcher.
    """
    placeholders = get_lang(context, join_complete_pc_ability.__name__)

    ability = query_special_abilities(special_ability=update.message.text, as_dict=True)

    if ability:
        update.message.delete()
        store_value_and_update_kb(update, context, tags=["join", "pc", "abilities"], value=ability,
                                  btn_label="ability", lang_source="join_complete_pc", split_row=2)

        return 2
    else:
        invalid_state_choice(update, context, "join", placeholders)
        return 4


def join_complete_pc_dots(update: Update, context: CallbackContext) -> int:
    """
    Builds the keyboard of the selected attribute.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.:
    :return: the state of the conversation switcher.
    """
    placeholders = get_lang(context, join_complete_pc_dots.__name__)

    query = update.callback_query
    query.answer()

    choice = query.data
    context.user_data["join"]["selected_attribute"] = choice

    initial_dots = dict((x, y) for x, y in query_initial_dots(context.user_data["join"]["pc"]["pc_class"]))
    context.user_data["join"].setdefault("action_dots", initial_dots)
    action_dots = context.user_data["join"]["action_dots"]

    if calc_total_dots(action_dots) == 7:
        action_dots = initial_dots
        context.user_data["join"]["action_dots"] = action_dots

    buttons = create_central_buttons_action_dots(action_dots, choice)

    context.user_data["join"]["message"].edit_text(text=placeholders["0"].format(7 - calc_total_dots(action_dots)),
                                                   reply_markup=build_plus_minus_keyboard(buttons))
    return 7


def create_central_buttons_action_dots(action_dots: dict, attribute_selected: str):
    """
    Utility method used to create the buttons with the name of the actions and their number of dots associated with the
    selected attributes.

    :param action_dots: is the dict that contains the actions and their dots.
    :param attribute_selected: is the user's chosen attribute
    """
    buttons = []
    for action in query_action_list(attr=attribute_selected, as_list=True):
        action = str(action).lower().capitalize()
        if action in action_dots:
            buttons.append("{}: {}".format(action, action_dots[action]))
        else:
            buttons.append("{}: 0".format(action))
    return buttons


def calc_total_dots(action_dots: dict) -> int:
    """
    Utility method used to calculate the amount of action dots spent by the user so far.

    :param action_dots: is the dictionary of the actions.
    :return: the amount of spent action dots.
    """
    total = 0
    for key in action_dots:
        total += action_dots[key]
    return total


def join_complete_pc_action_selection(update: Update, context: CallbackContext) -> int:
    """
    Handles the selection of the addition or removal of a specific action by the player
    or the information request about a specific action.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.:
    :return: the state of the conversation switcher.
    """
    placeholders = get_lang(context, join_complete_pc_dots.__name__)

    query = update.callback_query
    query.answer()

    action_dots = context.user_data["join"]["action_dots"]

    choice = query.data
    if "+" in choice or "-" in choice:
        choice = choice.split(" ")

        action_dots.setdefault(choice[0], 0)
        action_dots[choice[0]] += int(choice[1])

        if action_dots[choice[0]] < 0:
            action_dots[choice[0]] = 0
        if action_dots[choice[0]] > 4:
            action_dots[choice[0]] = 4

        attribute = context.user_data["join"]["selected_attribute"]
        buttons = create_central_buttons_action_dots(action_dots, attribute)

        if calc_total_dots(action_dots) == 7:
            store_value_and_update_kb(update, context, tags=["join", "pc", "action_dots"], value=action_dots,
                                      btn_label="Action Dots", lang_source="join_complete_pc", split_row=2)
            return 2

        context.user_data["join"]["message"].delete()
        context.user_data["join"]["message"] = context.bot.sendMessage(chat_id=get_user_id(update),
                                                                       text=placeholders["0"].format(
                                                                           7 - calc_total_dots(action_dots)),
                                                                       reply_markup=build_plus_minus_keyboard(buttons))

        return 7

    elif choice == "BACK":
        context.user_data["join"]["message"].delete()
        context.user_data["join"]["message"] = context.bot.sendMessage(chat_id=get_user_id(update),
                                                                       text=placeholders["1"].format(
                                                                           7 - calc_total_dots(action_dots)),
                                                                       reply_markup=custom_kb(
                                                                           query_attributes(only_names=True),
                                                                           inline=True))
        return 4

    else:

        description = query_actions(choice)[0][1]
        auto_delete_message(context.bot.sendMessage(chat_id=get_user_id(update),
                                                    text=description,
                                                    ), description)
        return 7


def join_complete_pc_friend(update: Update, context: CallbackContext) -> int:
    """
    If the user chooses a valid option, sends the information associated with this state ("Friend")
    to store_value_and_update_kb method.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.:
    :return: the state of the conversation switcher.
    """
    placeholders = get_lang(context, join_complete_pc_friend.__name__)

    friend: List[dict] = query_char_strange_friends(pc_class=context.user_data["join"]["pc"]["pc_class"],
                                                    strange_friend=update.message.text.split(",")[0], as_dict=True)

    if friend:
        update.message.delete()
        store_value_and_update_kb(update, context, tags=["join", "pc", "friend"], value=friend[0],
                                  lang_source="join_complete_pc", split_row=2)

        return 2
    else:
        invalid_state_choice(update, context, "join", placeholders)
        return 6


def join_complete_pc_enemy(update: Update, context: CallbackContext) -> int:
    """
    If the user chooses a valid option, sends the information associated with this state ("Enemy")
    to store_value_and_update_kb method.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.:
    :return: the state of the conversation switcher.
    """
    placeholders = get_lang(context, join_complete_pc_enemy.__name__)

    enemy: List[dict] = query_char_strange_friends(pc_class=context.user_data["join"]["pc"]["pc_class"],
                                                   strange_friend=update.message.text.split(",")[0], as_dict=True)

    if enemy:
        update.message.delete()
        store_value_and_update_kb(update, context, tags=["join", "pc", "enemy"], value=enemy[0],
                                  lang_source="join_complete_pc", split_row=2)

        return 2
    else:
        invalid_state_choice(update, context, "join", placeholders)
        return 6


def join_end(update: Update, context: CallbackContext) -> int:
    """
    Ends the conversation when /done or /cancel is received.
    If /done it check if all the necessary fields of the conversation have been filled and, if so,
    it updates the player list pf characters with the completed PC in the controller and database.
    If /cancel it deletes the information collected so far.
    In any case, it exits the conversation.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: ConversationHandler.END.
    """
    command = update.message.text
    placeholders = get_lang(context, join_end.__name__)

    if "done".casefold() in command:
        complete_dict = {"name", "alias", "look", "heritage", "background", "pc_class", "vice",
                         "abilities", "action_dots", "friend", "enemy"}

        if complete_dict.issubset(context.user_data["join"]["pc"].keys()):

            controller.update_user_in_game(get_user_id(update), context.user_data["join"]["chat_id"],
                                           context.user_data["join"]["game_name"], pc=context.user_data["join"]["pc"])

            context.bot.sendMessage(chat_id=context.user_data["join"]["chat_id"],
                                    text=placeholders["0"].format(
                                        query_users_names(get_user_id(update))[0],
                                        context.user_data["join"]["game_name"],
                                        context.user_data["join"]["pc"]["name"]),
                                    parse_mode=ParseMode.HTML)

            context.user_data.setdefault(
                "active_PCs", {})[context.user_data["join"]["chat_id"]] = context.user_data["join"]["pc"]["name"]

        else:
            auto_delete_message(update.message.reply_text(placeholders["1"]))
            update.message.delete()
            return 0

    delete_conv_from_telegram_data(context, "join")

    return end_conv(update, context)


# ------------------------------------------conv_join-------------------------------------------------------------------


# ------------------------------------------conv_create_crew------------------------------------------------------------


def create_crew(update: Update, context: CallbackContext) -> int:
    """
    Handles the creation of a crew checking if the user has already joined a game.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: next conversation's state.
    """
    placeholders = get_lang(context, create_crew.__name__)

    if query_game_of_user(update.message.chat_id, get_user_id(update)) is None:
        update.message.reply_text(placeholders["1"])
        return end_conv(update, context)

    context.user_data.setdefault("create_crew", {})["message"] = update.message.reply_text(
        text=placeholders["0"], reply_markup=custom_kb(query_crew_sheets(True)))

    context.user_data["create_crew"]["invocation_message"] = update.message

    return 0


def create_crew_type(update: Update, context: CallbackContext) -> int:
    """
    Stores the chosen crew type in the user_data
    It builds the inline keyboard that will be used during conv_createPC.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: next conversation's state.
    """
    placeholders = get_lang(context, create_crew_type.__name__)
    context.user_data["create_crew"]["message"].delete()

    if not exists_crew(update.message.text):
        context.user_data["create_crew"]["message"] = context.user_data["create_crew"]["invocation_message"].reply_text(
            placeholders["0"],
            reply_markup=custom_kb(
                query_crew_sheets(True)))

        update.message.delete()
        return 0

    query_menu = context.user_data["create_crew"]["invocation_message"].reply_text(text=placeholders["1"],
                                                                                   reply_markup=custom_kb(
                                                                                       placeholders["keyboard"],
                                                                                       inline=True, split_row=3))

    context.user_data["create_crew"]["keyboard"] = copy.deepcopy(placeholders["keyboard"])
    context.user_data["create_crew"]["crew"] = {"type": update.message.text}
    context.user_data["create_crew"]["query_menu"] = query_menu

    starting_upgrade, starting_cohort = query_starting_upgrades_and_cohorts(
        context.user_data["create_crew"]["crew"]["type"])

    context.user_data["create_crew"]["crew"].setdefault("upgrades", starting_upgrade)
    context.user_data["create_crew"].setdefault("upgrades", starting_upgrade)

    context.user_data["create_crew"]["crew"].setdefault("cohorts", starting_cohort)

    update.message.delete()

    return 1


def create_crew_state_switcher(update: Update, context: CallbackContext) -> int:
    """
    Handles the callback query from the Inline keyboard by redirecting the user in the correct state of the creation
    and sending him the associated message.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: next conversation's state.
    """
    placeholders = get_lang(context, create_crew_state_switcher.__name__)
    keyboards = copy.deepcopy(placeholders["keyboards"])

    crew_type = context.user_data["create_crew"]["crew"]["type"]

    keyboards.append(query_upgrade_groups())

    abilities = []
    for ability in query_special_abilities(crew_type, as_dict=True):
        if isinstance(ability, dict):
            abilities.append(ability["name"])

    keyboards.append(abilities)

    contacts = []
    for npc in query_crew_contacts(crew_type, as_dict=True):
        if isinstance(npc, dict):
            contacts.append(npc["name"] + ", " + npc["role"])
    keyboards.append(contacts)

    return query_state_switcher(update, context, "create_crew", placeholders, keyboards, reply_in_group=True,
                                starting_state=2, index_inlines=[4], split_inline_row=2)


def create_crew_name(update: Update, context: CallbackContext) -> int:
    """
    Sends the btn_label associated with this state ("name") to store_value_and_update_kb method.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.:
    :return: the state of the conversation switcher.
    """
    store_value_and_update_kb(update, context, tags=["create_crew", "crew", "name"],
                              lang_source="create_crew_type",
                              value=update.message.text, split_row=3, reply_in_group=True)
    update.message.delete()

    return 1


def create_crew_reputation(update: Update, context: CallbackContext) -> int:
    """
    Sends the btn_label associated with this state ("reputation") to store_value_and_update_kb method.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.:
    :return: the state of the conversation switcher.
    """
    store_value_and_update_kb(update, context, tags=["create_crew", "crew", "reputation"],
                              lang_source="create_crew_type",
                              value=update.message.text, split_row=3, reply_in_group=True)
    update.message.delete()

    return 1


def create_crew_description(update: Update, context: CallbackContext) -> int:
    """
    Sends the btn_label associated with this state ("reputation") to store_value_and_update_kb method.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.:
    :return: the state of the conversation switcher.
    """
    store_value_and_update_kb(update, context, tags=["create_crew", "crew", "description"],
                              lang_source="create_crew_type",
                              btn_label="notes",
                              value=update.message.text, split_row=3, reply_in_group=True)
    update.message.delete()

    return 1


def create_crew_lair_location(update: Update, context: CallbackContext) -> int:
    """
    Stores the lair location in the user_data and advances the conversation to
    the next state that regards the description of the lair.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.:
    :return: the next state of the conversation.
    """
    context.user_data["create_crew"]["message"].delete()

    add_tag_in_telegram_data(context, ["create_crew", "crew", "lair", "location"], update.message.text)

    placeholders = get_lang(context, create_crew_lair_location.__name__)

    context.user_data["create_crew"]["message"] = update.message.reply_text(placeholders["0"])
    update.message.delete()

    return 9


def create_crew_lair_description(update: Update, context: CallbackContext) -> int:
    """
    Sends the tags associated with this state ("lair" and "description") to store_value_and_update_kb method.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.:
    :return: the state of the conversation switcher.
    """
    store_value_and_update_kb(update, context, tags=["create_crew", "crew", "lair", "description"],
                              lang_source="create_crew_type",
                              btn_label="lair",
                              value=update.message.text, split_row=3, reply_in_group=True)
    update.message.delete()

    return 1


def create_crew_upgrades(update: Update, context: CallbackContext) -> int:
    """
    Builds the keyboard of the selected group of upgrades.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.:
    :return: the state of the conversation switcher.
    """
    placeholders = get_lang(context, create_crew_upgrades.__name__)

    query = update.callback_query
    query.answer()

    choice = query.data
    context.user_data["create_crew"]["selected_group"] = choice

    upgrades = context.user_data["create_crew"]["upgrades"]

    if calc_total_upgrade_points(upgrades + context.user_data["create_crew"]["crew"]["cohorts"]) == 4:
        starting_upgrade, starting_cohort = query_starting_upgrades_and_cohorts(
            context.user_data["create_crew"]["crew"]["type"])

        context.user_data["create_crew"]["upgrades"] = starting_upgrade
        upgrades = context.user_data["create_crew"]["upgrades"]

    if choice.lower() == "specific":
        buttons = create_central_buttons_upgrades(upgrades, choice, context.user_data["create_crew"]["crew"]["type"])
    else:
        buttons = create_central_buttons_upgrades(upgrades, choice)

    context.user_data["create_crew"]["message"].edit_text(
        text=placeholders["0"].format(
            4 - calc_total_upgrade_points(upgrades + context.user_data["create_crew"]["crew"]["cohorts"])),
        reply_markup=build_plus_minus_keyboard(buttons))

    return 10


def create_crew_upgrade_selection(update: Update, context: CallbackContext) -> int:
    """
    Handles the selection of the addition or removal of a specific upgrade by the player
    or the information request about a specific upgrade.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.:
    :return: the state of the conversation switcher.
    """
    placeholders = get_lang(context, create_crew_upgrades.__name__)

    query = update.callback_query
    query.answer()

    upgrades = context.user_data["create_crew"]["upgrades"]

    choice = query.data
    if "+" in choice or "-" in choice:
        choice = choice.split(" ")
        name = choice[0]
        for i in range(1, len(choice) - 1):
            name += " {}".format(choice[i])

        upgrade = None
        for upg in upgrades:
            if upg["name"] == name:
                upg["quality"] += int(choice[-1])
                if upg["quality"] == 0:
                    upgrades.remove(upg)
                else:
                    upgrade = upg
                break

        if upgrade is None and "+" in choice[-1]:
            upgrades.append({"name": name, "quality": 1})
            upgrade = upgrades[-1]

        if upgrade is not None:
            if upgrade["quality"] < 0:
                upgrade["quality"] = 0

            tot_quality = query_upgrades(upgrade["name"])[0]["tot_quality"]
            if upgrade["quality"] > tot_quality:
                upgrade["quality"] = tot_quality

        group = context.user_data["create_crew"]["selected_group"]
        if group.lower() == "specific":
            buttons = create_central_buttons_upgrades(upgrades, group, context.user_data["create_crew"]["crew"]["type"])
        else:
            buttons = create_central_buttons_upgrades(upgrades, group)

        if calc_total_upgrade_points(upgrades + context.user_data["create_crew"]["crew"]["cohorts"]) == 4:
            store_value_and_update_kb(update, context, tags=["create_crew", "crew", "upgrades"], value=upgrades,
                                      btn_label="Upgrades", lang_source="create_crew_type",
                                      split_row=3, reply_in_group=True)
            return 1

        context.user_data["create_crew"]["message"].delete()
        context.user_data["create_crew"]["message"] = context.user_data["create_crew"]["invocation_message"].reply_text(
            text=placeholders["0"].format(
                4 - calc_total_upgrade_points(
                    upgrades + context.user_data["create_crew"]["crew"]["cohorts"])),
            reply_markup=build_plus_minus_keyboard(
                buttons))
        return 10

    elif choice == "BACK":
        context.user_data["create_crew"]["message"].delete()
        context.user_data["create_crew"]["message"] = context.user_data["create_crew"]["invocation_message"].reply_text(
            text=placeholders["1"].format(
                4 - calc_total_upgrade_points(upgrades + context.user_data["create_crew"]["crew"]["cohorts"])),
            reply_markup=custom_kb(
                query_upgrade_groups(),
                inline=True, split_row=2))
        return 6

    else:

        description = query_upgrades(upgrade=choice)[0]["description"]
        auto_delete_message(context.user_data["create_crew"]["invocation_message"].reply_text(
            text=description,
        ), description)
        return 10


def create_central_buttons_upgrades(upgrades: List[dict], group_selected: str, crew_sheet: str = None):
    """
    Utility method used to create the buttons with the name of the upgrades and their quality, associated with the
    selected group.

    :param upgrades: is the dict that contains the upgrades and their quality.
    :param group_selected: is the user's chosen group.
    :param crew_sheet: the type of the crew.
    """
    upgrades_names = []
    upgrades_quality = []
    for elem in upgrades:
        if "type" not in elem:
            upgrades_names.append(elem["name"].lower())
            upgrades_quality.append(elem["quality"])

    buttons = []
    for upgrade in query_upgrades(group=group_selected, crew_sheet=crew_sheet):

        if upgrade["name"].lower() in upgrades_names:
            buttons.append("{}: {}/{}".format(upgrade["name"],
                                              upgrades_quality[
                                                  upgrades_names.index(upgrade["name"].lower())],
                                              upgrade["tot_quality"]))
        else:
            buttons.append("{}: 0/{}".format(upgrade["name"], upgrade["tot_quality"]))
    return buttons


def calc_total_upgrade_points(upgrades: List[dict]) -> int:
    """
    Utility method used to calculate the amount of upgrades selected by the user so far.

    :param upgrades: is the dictionary of the upgrades.
    :return: the amount of the selected upgrades.
    """
    total = 0
    for upgrade in upgrades:
        if "quality" in upgrade:
            total += upgrade["quality"]
        else:
            total += 1
    return total


def create_crew_ability(update: Update, context: CallbackContext) -> int:
    """
    If the user chooses a valid option, sends the information associated with this state ("ability")
    to store_value_and_update_kb method.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.:
    :return: the state of the conversation switcher.
    """
    placeholders = get_lang(context, create_crew_ability.__name__)

    ability = query_special_abilities(special_ability=update.message.text, as_dict=True)

    if ability:
        update.message.delete()
        store_value_and_update_kb(update, context, tags=["create_crew", "crew", "abilities"], value=ability,
                                  btn_label="Special ability", lang_source="create_crew_type",
                                  split_row=3, reply_in_group=True)

        return 1
    else:
        invalid_state_choice(update, context, "create_crew", placeholders)
        return 7


def create_crew_contact(update: Update, context: CallbackContext) -> int:
    """
    Sends the btn_label associated with this state ("contact") to store_value_and_update_kb method.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.:
    :return: the state of the conversation switcher.
    """
    placeholders = get_lang(context, create_crew_contact.__name__)

    contact: List[dict] = query_crew_contacts(context.user_data["create_crew"]["crew"]["type"],
                                              update.message.text.split(",")[0], as_dict=True)

    if contact:
        update.message.delete()
        store_value_and_update_kb(update, context, tags=["create_crew", "crew", "contact"], value=contact[0],
                                  lang_source="create_crew_type", split_row=3, reply_in_group=True)

        return 1
    else:
        invalid_state_choice(update, context, "create_crew", placeholders)
        return 8


def create_crew_end(update: Update, context: CallbackContext) -> int:
    """
    Ends the conversation when /done or /cancel is received.
    If /done it check if all the necessary fields of the conversation have been filled and, if so,
    it updates the game's crew in the controller and stores it in the database.
    If /cancel it deletes the information collected so far.
    In any case, it exits the conversation.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: ConversationHandler.END.
    """
    command = update.message.text
    placeholders = get_lang(context, create_crew_end.__name__)

    if "done".casefold() in command:
        complete_dict = {"type", "name", "reputation", "lair", "abilities", "contact"}

        if complete_dict.issubset(context.user_data["create_crew"]["crew"].keys()):

            controller.update_crew_in_game(get_user_id(update), update.effective_message.chat_id,
                                           context.user_data["create_crew"]["crew"])

            context.bot.sendMessage(chat_id=update.effective_message.chat_id,
                                    text=placeholders["0"].format(context.user_data["create_crew"]["crew"]["name"]),
                                    parse_mode=ParseMode.HTML)
        else:
            auto_delete_message(update.message.reply_text(placeholders["1"]))
            update.message.delete()
            return 0

    delete_conv_from_telegram_data(context, "create_crew")

    return end_conv(update, context)


# ------------------------------------------conv_createCrew-------------------------------------------------------------

# ------------------------------------------conv_pcSelection------------------------------------------------------------

def pc_selection(update: Update, context: CallbackContext) -> int:
    """
    Checks if the user is in a game in this chat and if so, it builds the InlineKeyboard with all the player's PCs of
    the game.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, pc_selection.__name__)

    if query_game_of_user(update.message.chat_id, get_user_id(update)) is None:
        update.message.reply_text(placeholders["1"])
        return end_conv(update, context)

    query_menu = update.effective_message.reply_text(placeholders["0"],
                                                     reply_markup=custom_kb(
                                                         controller.get_user_characters_names(get_user_id(update),
                                                                                              update.message.chat_id),
                                                         inline=True))

    context.user_data.setdefault("pc_selection", {})["query_menu"] = query_menu
    context.user_data["pc_selection"]["invocation_message"] = update.message

    return 0


def pc_selection_choice(update: Update, context: CallbackContext) -> int:
    """
    Handles the selection of the new PC of the user and stores it in the user_data

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: call to pc_selection_end method.
    """
    placeholders = get_lang(context, pc_selection_choice.__name__)

    query = update.callback_query
    query.answer()

    choice = query.data

    context.user_data.setdefault("active_PCs", {})[update.effective_message.chat_id] = choice

    context.user_data["pc_selection"]["invocation_message"].reply_text(placeholders["0"].format(
        query_games_info(game_id=query_game_of_user(update.effective_message.chat_id, get_user_id(update)))[0]["title"],
        choice), parse_mode=ParseMode.HTML)

    return pc_selection_end(update, context)


def pc_selection_end(update: Update, context: CallbackContext) -> int:
    """
    Ends the conversation when /cancel is received or when the finel state is reached,
    then deletes the information collected so far from the command dict and exits the conversation.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: ConversationHandler.END.
    """

    context.user_data.pop("pc_selection")

    return end_conv(update, context)


# ------------------------------------------conv_pcSelection------------------------------------------------------------


# ------------------------------------------conv_actionRoll-------------------------------------------------------------


def group_action(update: Update, context: CallbackContext) -> int:
    """
    Checks if the user controls a PC in this chat and starts the conversation of the group action.
    Adds the dict "action_roll" in chat_data and stores the ID of the invoker, his active PC and the tag "group_action"
    in it. Finally, sends the goal request.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    if "active_PCs" in context.user_data and update.effective_message.chat_id in context.user_data["active_PCs"]:

        placeholders = get_lang(context, action_roll.__name__)

        if query_game_of_user(update.message.chat_id, get_user_id(update)) is None:
            update.message.reply_text(placeholders["1"])
            return end_conv(update, context)

        message = update.message.reply_text(text=placeholders["0"], parse_mode=ParseMode.HTML)
        add_tag_in_telegram_data(context, location="chat", tags=["action_roll", "message"], value=message)

        add_tag_in_telegram_data(context, location="chat", tags=["action_roll", "invocation_message"],
                                 value=update.message)

        pc_name = context.user_data["active_PCs"][update.effective_message.chat_id]
        add_tag_in_telegram_data(context, location="chat", tags=["action_roll", "invoker"], value=get_user_id(update))
        add_tag_in_telegram_data(context, location="chat", tags=["action_roll", "roll", "pc"],
                                 value=pc_name)

        add_tag_in_telegram_data(context, location="chat", tags=["action_roll", "group_action"], value=[])
        add_tag_in_telegram_data(context, location="chat", tags=["action_roll", "roll", "participants"], value={})

        return 0


def group_action_cohort(update: Update, context: CallbackContext) -> int:
    """
    Checks if the user controls a PC in this chat and starts the conversation of the group action cohort.
    Adds the dict "action_roll" in chat_data and stores the ID of the invoker and his active PC in it.
    Finally, sends the cohort inline keyboard.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    if "active_PCs" in context.user_data and update.effective_message.chat_id in context.user_data["active_PCs"]:

        placeholders = get_lang(context, group_action_cohort.__name__)

        if is_user_not_in_game(update, placeholders["1"]):
            return end_conv(update, context)

        chat_id = update.effective_message.chat_id
        user_id = get_user_id(update)
        cohorts = controller.get_cohorts_of_crew(chat_id, user_id)

        if not cohorts:
            placeholders = get_lang(context, "missing_cohorts")
            auto_delete_message(update.message.reply_text(placeholders["0"]), 15)
            return end_conv(update, context)

        cohorts_labels = []
        for cohort in cohorts:
            cohorts_labels.append(cohort[0])

        message = update.message.reply_text(text=placeholders["0"], parse_mode=ParseMode.HTML,
                                            reply_markup=custom_kb(cohorts_labels, True, 1,
                                                                   callback_data=cohorts))
        add_tag_in_telegram_data(context, location="chat", tags=["action_roll", "message"], value=message)

        add_tag_in_telegram_data(context, location="chat", tags=["action_roll", "invocation_message"],
                                 value=update.message)

        add_tag_in_telegram_data(context, location="chat", tags=["action_roll", "invoker"], value=user_id)
        add_tag_in_telegram_data(context, location="chat", tags=["action_roll", "roll", "pc"],
                                 value=context.user_data["active_PCs"][chat_id])

        return 10


def group_action_cohort_choice(update: Update, context: CallbackContext) -> int:
    """
    Stores the chosen cohort in the chat_data and advances the conversation to
    the next state that regards the goal of the action.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """

    placeholders = get_lang(context, action_roll.__name__)
    context.chat_data["action_roll"]["message"].delete()

    query = update.callback_query
    query.answer()

    choice = tuple(query.data)

    message = context.chat_data["action_roll"]["invocation_message"].reply_text(
        text=placeholders["0"], parse_mode=ParseMode.HTML)
    add_tag_in_telegram_data(context, location="chat", tags=["action_roll", "message"], value=message)

    add_tag_in_telegram_data(context, location="chat", tags=["action_roll", "roll", "cohort"],
                             value=choice)

    return 0


def action_roll(update: Update, context: CallbackContext) -> int:
    """
    Checks if the user controls a PC in this chat and starts the conversation of the action roll.
    Adds the dict "action_roll" in chat_data and stores the ID of the invoker and his active PC in it.
    Finally sends the goal request.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    if "active_PCs" in context.user_data and update.effective_message.chat_id in context.user_data["active_PCs"]:

        placeholders = get_lang(context, action_roll.__name__)

        if query_game_of_user(update.message.chat_id, get_user_id(update)) is None:
            update.message.reply_text(placeholders["1"])
            return end_conv(update, context)

        message = update.message.reply_text(text=placeholders["0"], parse_mode=ParseMode.HTML)
        add_tag_in_telegram_data(context, location="chat", tags=["action_roll", "message"], value=message)

        add_tag_in_telegram_data(context, location="chat", tags=["action_roll", "invocation_message"],
                                 value=update.message)

        add_tag_in_telegram_data(context, location="chat", tags=["action_roll", "invoker"], value=get_user_id(update))
        add_tag_in_telegram_data(context, location="chat", tags=["action_roll", "roll", "pc"],
                                 value=context.user_data["active_PCs"][update.effective_message.chat_id])

        return 0


def action_roll_goal(update: Update, context: CallbackContext):
    """
    Stores the goal's description in the chat_data and sends the keyboard with all the PC's action and their ratings.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    if get_user_id(update) == context.chat_data["action_roll"]["invoker"]:
        context.chat_data["action_roll"]["message"].delete()

        placeholders = get_lang(context, action_roll_goal.__name__)

        add_tag_in_telegram_data(context, location="chat", tags=["action_roll", "roll", "goal"],
                                 value=update.message.text)

        if "group_action" in context.chat_data["action_roll"]:
            auto_delete_message(context.chat_data["action_roll"]["invocation_message"].reply_text(
                text=get_lang(context, group_action.__name__)["0"].format(
                    context.chat_data["action_roll"]["roll"]["pc"], update.message.text),
                parse_mode=ParseMode.HTML), 25)

        chat_id = update.message.chat_id
        action_ratings = controller.get_pc_actions_ratings(get_user_id(update),
                                                           chat_id, context.user_data["active_PCs"][chat_id])

        buttons = ["{}: {}".format(action[0], action[1]) for action in action_ratings]
        context.chat_data["action_roll"]["message"] = context.chat_data["action_roll"]["invocation_message"].reply_text(
            placeholders["0"],
            parse_mode=ParseMode.HTML,
            reply_markup=custom_kb(buttons))

        update.message.delete()

        return 0


def action_roll_rating(update: Update, context: CallbackContext) -> int:
    """
    Stores the chosen action in the chat_data and transfers the conversation to the Master
    with a request of reply for the GM in the chat.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    context.chat_data["action_roll"]["message"].delete()
    placeholders = get_lang(context, action_roll_rating.__name__)

    add_tag_in_telegram_data(context, location="chat", tags=["action_roll", "roll", "action"],
                             value=update.message.text)

    context.chat_data["action_roll"]["message"] = context.chat_data["action_roll"]["invocation_message"].reply_text(
        placeholders["0"].format(context.chat_data["action_roll"]["roll"]["pc"],
                                 context.chat_data["action_roll"]["roll"]["goal"],
                                 context.chat_data["action_roll"]["roll"]["action"]), parse_mode=ParseMode.HTML)

    add_tag_in_telegram_data(context, tags=["action_roll", "GM_question"],
                             value={"text": placeholders["1"], "reply_markup": custom_kb(placeholders["keyboard"])},
                             location="chat")
    update.message.delete()
    return 1


def master_reply(update: Update, context: CallbackContext) -> int:
    """
    Filters all the updates except for the master's. When the GM replies it sends in the chat the position request.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    if controller.is_master(get_user_id(update), update.effective_message.chat_id):
        command = update.message.text
        command = command.split("/reply_")[1].split("@")[0]

        context.chat_data[command]["message"].delete()

        context.chat_data[command]["message"] = update.message.reply_text(
            **context.chat_data[command]["GM_question"])

        add_tag_in_telegram_data(context, location="chat", tags=[command, "master_message"],
                                 value=update.message)

        return 0


def action_roll_position(update: Update, context: CallbackContext) -> int:
    """
    Stores the position decided by the GM in the chat_data and sends the effect level request.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    context.chat_data["action_roll"]["message"].delete()

    placeholders = get_lang(context, action_roll_position.__name__)

    add_tag_in_telegram_data(context, location="chat", tags=["action_roll", "roll", "position"],
                             value=update.message.text)

    context.chat_data["action_roll"]["message"] = context.chat_data["action_roll"]["master_message"].reply_text(
        placeholders["0"], reply_markup=custom_kb(placeholders["keyboard"]))

    update.message.delete()
    return 1


def action_roll_effect(update: Update, context: CallbackContext) -> int:
    """
    Stores the effect decided by the GM in the chat_data and brings back the conversation to the invoker of the command
    (if /actionRoll) or to the first participant of the group action.
    Sends the keyboard with the "Push Yourself", "Devil's Bargain" and "No Thanks" option.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation depending on the nature of the action.
    """
    context.chat_data["action_roll"]["message"].delete()

    add_tag_in_telegram_data(context, location="chat", tags=["action_roll", "roll", "bonus_dice"], value=0)

    placeholders = get_lang(context, action_roll_effect.__name__)

    add_tag_in_telegram_data(context, location="chat", tags=["action_roll", "roll", "effect"],
                             value=update.message.text)

    auto_delete_message(
        update.message.reply_text(placeholders["0"].format(context.chat_data["action_roll"]["roll"]["pc"],
                                                           context.chat_data["action_roll"]["roll"]["goal"]),
                                  quote=False, parse_mode=ParseMode.HTML), 20)

    if "group_action" in context.chat_data["action_roll"] and context.chat_data["action_roll"]["group_action"]:
        context.chat_data["action_roll"]["message"] = context.chat_data["action_roll"]["invocation_message"].reply_text(
            placeholders["2"].format(context.chat_data["action_roll"]["group_action"][0][1]),
            parse_mode=ParseMode.HTML, reply_markup=custom_kb(buttons=placeholders["keyboard"],
                                                              callback_data=placeholders[
                                                                  "callbacks"],
                                                              inline=True, split_row=1))
        update.message.delete()
        return 20

    else:
        context.chat_data["action_roll"]["message"] = context.chat_data["action_roll"]["invocation_message"].reply_text(
            placeholders["1"], reply_markup=custom_kb(buttons=placeholders["keyboard"],
                                                      callback_data=placeholders["callbacks"],
                                                      inline=True, split_row=1))

        update.message.delete()
        if "group_action" in context.chat_data["action_roll"]:
            context.chat_data["action_roll"].pop("group_action")
        if "participants" in context.chat_data["action_roll"]["roll"]:
            context.chat_data["action_roll"]["roll"].pop("participants")
            auto_delete_message(context.chat_data["action_roll"]["invocation_message"].reply_text(
                placeholders["3"]), 15)

        return 2


def action_roll_assistance(update: Update, context: CallbackContext) -> None:
    """
    Stores the PC of the user who decided to assist the invoker's PC in the chat_data if the sender of this command has
    actually a PC and if the pc is not already in the action.
    This command can be executed in any time of the action roll's conversation.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    """
    placeholders = get_lang(context, action_roll_assistance.__name__)

    user_id = get_user_id(update)
    chat_id = update.effective_message.chat_id
    invoker_id = context.chat_data["action_roll"]["invoker"]
    pc_name = context.user_data["active_PCs"][chat_id]
    if user_id != invoker_id or (user_id == invoker_id and context.chat_data["action_roll"]["roll"]["pc"] != pc_name):
        if query_game_of_user(chat_id, user_id) == query_game_of_user(chat_id, invoker_id):
            if "active_PCs" in context.user_data and chat_id in context.user_data["active_PCs"]:

                new_assistant = (user_id, context.user_data["active_PCs"][chat_id])

                if "assistants" in context.chat_data["action_roll"]["roll"]:
                    for elem in context.chat_data["action_roll"]["roll"]["assistants"]:
                        if elem == new_assistant:
                            auto_delete_message(update.message.reply_text(
                                placeholders["1"], parse_mode=ParseMode.HTML), 10)

                            return

                context.chat_data["action_roll"]["roll"].setdefault(
                    "assistants", []).append(new_assistant)

                if "query_menu" in context.chat_data["action_roll"]:
                    update_bonus_dice_kb(context, ["action_roll", "roll", "bonus_dice"],
                                         action_roll_calc_total_dice(context.chat_data["action_roll"]["roll"]))

                auto_delete_message(
                    update.message.reply_text(placeholders["0"].format(context.user_data["active_PCs"][chat_id]),
                                              parse_mode=ParseMode.HTML), 18)
                return

    auto_delete_message(
        update.message.reply_text(placeholders["2"], parse_mode=ParseMode.HTML), 18)


def group_action_participate(update: Update, context: CallbackContext) -> None:
    """
    Stores the information about the PC of the user who decided to participate in the group action
    in the chat_data if the sender of this command has actually a PC and if the pc is not already in the action.
    This command can be executed in any time of the group action's conversation.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    """
    placeholders = get_lang(context, group_action_participate.__name__)

    user_id = get_user_id(update)
    chat_id = update.effective_message.chat_id
    invoker_id = context.chat_data["action_roll"]["invoker"]
    pc_name = context.user_data["active_PCs"][chat_id]
    if user_id != invoker_id or (user_id == invoker_id and context.chat_data["action_roll"]["roll"]["pc"] != pc_name):
        if query_game_of_user(chat_id, user_id) == query_game_of_user(chat_id, invoker_id):
            if "active_PCs" in context.user_data and chat_id in context.user_data["active_PCs"]:

                new_participant = {"id": user_id}

                if "participants" in context.chat_data["action_roll"]["roll"]:
                    if pc_name in context.chat_data["action_roll"]["roll"]["participants"]:
                        auto_delete_message(update.message.reply_text(
                            placeholders["1"], parse_mode=ParseMode.HTML), 10)

                        return

                    context.chat_data["action_roll"]["roll"]["participants"][pc_name] = new_participant

                    context.chat_data["action_roll"]["group_action"].append((user_id, pc_name))

                    context.chat_data["action_roll"]["roll"]["participants"][pc_name]["bonus_dice"] = 0

                    context.chat_data["action_roll"]["roll"]["participants"][pc_name]["push"] = False

                auto_delete_message(
                    update.message.reply_text(placeholders["0"].format(context.user_data["active_PCs"][chat_id]),
                                              parse_mode=ParseMode.HTML), 18)
                return

    auto_delete_message(
        update.message.reply_text(placeholders["2"], parse_mode=ParseMode.HTML), 18)


def group_action_bargains(update: Update, context: CallbackContext) -> int:
    """
    Handles the choice of the user regarding the "Push Yourself" or "Devil's Bargain" option during the group action
    and stores all the information in the chat_data. If the user choose the "Devil's Bargain", the description request
    is sent. Otherwise, the bonus dice InlineKeyboard is sent.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, action_roll_bargains.__name__)
    user_id = get_user_id(update)

    if not context.chat_data["action_roll"]["group_action"]:
        context.chat_data["action_roll"].pop("group_action")
        return 2

    current_user, pc_name = context.chat_data["action_roll"]["group_action"][0]

    add_tag_in_telegram_data(context, location="chat",
                             tags=["action_roll", "roll", "participants", pc_name, "bonus_dice"], value=0)

    if user_id == current_user:
        try:
            context.chat_data["action_roll"]["master_message"].delete()
        except:
            pass
        context.chat_data["action_roll"]["message"].delete()
        query = update.callback_query
        query.answer()

        choice = query.data

        # Push
        if choice == 1:
            add_tag_in_telegram_data(context, location="chat",
                                     tags=["action_roll", "roll", "participants", pc_name, "push"], value=True)
        else:
            add_tag_in_telegram_data(context, location="chat",
                                     tags=["action_roll", "roll", "participants", pc_name, "push"], value=False)
        # Devil's Bargain
        if choice == 2:
            context.chat_data["action_roll"]["message"] = \
                context.chat_data["action_roll"]["invocation_message"].reply_text(
                    placeholders["0"], parse_mode=ParseMode.HTML)
            return 0

        bonus_dice_lang = get_lang(context, "bonus_dice")

        query_menu = context.chat_data["action_roll"]["invocation_message"].reply_text(
            bonus_dice_lang["message"].format(
                group_action_calc_total_dice(update, context)),
            reply_markup=build_plus_minus_keyboard(
                [bonus_dice_lang["button"].format(
                    context.chat_data["action_roll"]["roll"]["participants"][pc_name]["bonus_dice"])],
                done_button=True,
                back_button=False),
            parse_mode=ParseMode.HTML)

        add_tag_in_telegram_data(context, location="chat", tags=["action_roll", "query_menu"], value=query_menu)

        return 1


def action_roll_bargains(update: Update, context: CallbackContext) -> int:
    """
    Handles the choice of the user regarding the "Push Yourself" or "Devil's Bargain" option during the action roll
    and stores all the information in the chat_data. If the user choose the "Devil's Bargain", the description request
    is sent. Otherwise, the bonus dice InlineKeyboard is sent.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, action_roll_bargains.__name__)
    user_id = get_user_id(update)
    invoker_id = context.chat_data["action_roll"]["invoker"]

    if user_id == invoker_id:
        try:
            context.chat_data["action_roll"]["master_message"].delete()
        except:
            pass
        context.chat_data["action_roll"]["message"].delete()
        query = update.callback_query
        query.answer()

        choice = query.data

        # Push
        if choice == 1:
            add_tag_in_telegram_data(context, location="chat",
                                     tags=["action_roll", "roll", "push"], value=True)
        else:
            add_tag_in_telegram_data(context, location="chat",
                                     tags=["action_roll", "roll", "push"], value=False)
        # Devil's Bargain
        if choice == 2:
            context.chat_data["action_roll"]["message"] = \
                context.chat_data["action_roll"]["invocation_message"].reply_text(
                    placeholders["0"], parse_mode=ParseMode.HTML)
            return 0

        bonus_dice_lang = get_lang(context, "bonus_dice")

        add_tag_in_telegram_data(context, location="chat", tags=["action_roll", "roll", "bonus_dice"], value=0)

        query_menu = context.chat_data["action_roll"]["invocation_message"].reply_text(
            bonus_dice_lang["message"].format(
                action_roll_calc_total_dice(context.chat_data["action_roll"]["roll"])),
            reply_markup=build_plus_minus_keyboard(
                [bonus_dice_lang["button"].format(
                    context.chat_data["action_roll"]["roll"]["bonus_dice"])],
                done_button=True,
                back_button=False),
            parse_mode=ParseMode.HTML)

        add_tag_in_telegram_data(context, location="chat", tags=["action_roll", "query_menu"], value=query_menu)

        return 1


def action_roll_devil_bargains(update: Update, context: CallbackContext) -> int:
    """
    Stores the description of the Devil's Bargain in the chat_data and sends the bonus dice InlineKeyboard.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    context.chat_data["action_roll"]["message"].delete()

    if "group_action" in context.chat_data["action_roll"]:
        add_tag_in_telegram_data(context, location="chat",
                                 tags=["action_roll", "roll", "participants",
                                       context.chat_data["action_roll"]["group_action"][0][1],
                                       "devil_bargain"], value=update.message.text)
        tot_dice = group_action_calc_total_dice(update, context)
    else:
        add_tag_in_telegram_data(context, location="chat",
                                 tags=["action_roll", "roll", "devil_bargain"], value=update.message.text)
        tot_dice = action_roll_calc_total_dice(context.chat_data["action_roll"]["roll"])

    bonus_dice_lang = get_lang(context, "bonus_dice")
    add_tag_in_telegram_data(context, location="chat", tags=["action_roll", "roll", "bonus_dice"], value=0)
    query_menu = context.chat_data["action_roll"]["invocation_message"].reply_text(bonus_dice_lang["message"].format(
        tot_dice),
        reply_markup=build_plus_minus_keyboard(
            [bonus_dice_lang["button"].format(
                context.chat_data["action_roll"]["roll"]["bonus_dice"])],
            done_button=True,
            back_button=False),
        parse_mode=ParseMode.HTML)

    add_tag_in_telegram_data(context, location="chat", tags=["action_roll", "query_menu"], value=query_menu)

    update.message.delete()

    return 1


def action_roll_bonus_dice(update: Update, context: CallbackContext) -> int:
    """
    Handles the addition or removal of bonus dice and updates the related Keyboard.
    When the user confirms, the number of dice to roll is passed to roll_dice method.
    Then, the outcome is stored in the chat_data and the final description request is sent.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation when the "DONE" button is pressed.
    """
    placeholders = get_lang(context, action_roll_bonus_dice.__name__)

    query = update.callback_query
    query.answer()

    bonus_dice = context.chat_data["action_roll"]["roll"]["bonus_dice"]

    choice = query.data
    if "+" in choice or "-" in choice:
        bonus_dice += int(choice.split(" ")[2])
        add_tag_in_telegram_data(context, location="chat",
                                 tags=["action_roll", "roll", "bonus_dice"], value=bonus_dice)

        update_bonus_dice_kb(context, ["action_roll", "roll", "bonus_dice"],
                             action_roll_calc_total_dice(context.chat_data["action_roll"]["roll"]))

    elif choice == "DONE":
        dice_to_roll = action_roll_calc_total_dice(context.chat_data["action_roll"]["roll"])
        context.chat_data["action_roll"]["query_menu"].delete()

        roll_dice(update, context, dice_to_roll, ["action_roll", "roll", "outcome"])

        if "participants" in context.chat_data["action_roll"]["roll"]:
            max_outcome = context.chat_data["action_roll"]["roll"]["outcome"]
            if max_outcome != "CRIT":
                for key in context.chat_data["action_roll"]["roll"]["participants"].keys():
                    outcome = context.chat_data["action_roll"]["roll"]["participants"][key]["outcome"]
                    if outcome == "CRIT":
                        max_outcome = outcome
                        break
                    if outcome > max_outcome:
                        max_outcome = outcome

            context.chat_data["action_roll"]["roll"]["outcome"] = max_outcome

            update.effective_message.reply_text(placeholders["1"].format(str(max_outcome)),
                                                parse_mode=ParseMode.HTML,
                                                quote=False)
            update.effective_message.reply_sticker(sticker=dice_stickers[str(max_outcome)], quote=False)

        context.chat_data["action_roll"]["message"] = \
            context.chat_data["action_roll"]["invocation_message"].reply_text(
                placeholders["0"], parse_mode=ParseMode.HTML)
        return 2

    else:
        bonus_dice_lang = get_lang(context, "bonus_dice")
        auto_delete_message(update.effective_message.reply_text(bonus_dice_lang["extended"], parse_mode=ParseMode.HTML),
                            bonus_dice_lang["extended"])

    return 1


def group_action_bonus_dice(update: Update, context: CallbackContext) -> int:
    """
    Handles the addition or removal of bonus dice and updates the related Keyboard.
    When the user confirms, the number of dice to roll is passed to roll_dice method.
    Then, the conversation moves on the next participant, if present, or to the invoker.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation when the "DONE" button is pressed.
    """
    placeholders = get_lang(context, group_action_bonus_dice.__name__)

    query = update.callback_query
    query.answer()

    pc_name = context.chat_data["action_roll"]["group_action"][0][1]

    bonus_dice = context.chat_data["action_roll"]["roll"]["participants"][pc_name]["bonus_dice"]

    choice = query.data
    if "+" in choice or "-" in choice:
        tags = ["action_roll", "roll", "participants", pc_name, "bonus_dice"]
        bonus_dice += int(choice.split(" ")[2])
        add_tag_in_telegram_data(context, location="chat", tags=tags, value=bonus_dice)

        total_dice = group_action_calc_total_dice(update, context)

        update_bonus_dice_kb(context, tags, total_dice)

    elif choice == "DONE":
        dice_to_roll = group_action_calc_total_dice(update, context)

        context.chat_data["action_roll"]["query_menu"].delete()

        roll_dice(update, context, dice_to_roll, ["action_roll", "roll", "participants", pc_name, "outcome"])

        context.chat_data["action_roll"]["group_action"].pop(0)
        if not context.chat_data["action_roll"]["group_action"]:
            context.chat_data["action_roll"].pop("group_action")

        if "group_action" in context.chat_data["action_roll"] and context.chat_data["action_roll"]:
            context.chat_data["action_roll"]["message"] = context.chat_data["action_roll"][
                "invocation_message"].reply_text(
                placeholders["1"].format(context.chat_data["action_roll"]["group_action"][0][1]),
                parse_mode=ParseMode.HTML, reply_markup=custom_kb(buttons=placeholders["keyboard"],
                                                                  callback_data=placeholders[
                                                                      "callbacks"],
                                                                  inline=True, split_row=1))
            return 20

        else:
            context.chat_data["action_roll"]["message"] = context.chat_data["action_roll"][
                "invocation_message"].reply_text(
                placeholders["0"], reply_markup=custom_kb(buttons=placeholders["keyboard"],
                                                          callback_data=placeholders["callbacks"],
                                                          inline=True, split_row=1))
            return 2

    else:
        bonus_dice_lang = get_lang(context, "bonus_dice")
        auto_delete_message(update.effective_message.reply_text(bonus_dice_lang["extended"], parse_mode=ParseMode.HTML),
                            bonus_dice_lang["extended"])

    return 1


def action_roll_notes(update: Update, context: CallbackContext) -> int:
    """
    Stores the final description of the action roll in the chat_data, calls the controller method to apply the roll's
    effects and sends the notification for the PCs who suffered a new trauma after this action.
    Finally, calls action_roll_end.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: call to action_roll_end
    """
    context.chat_data["action_roll"]["message"].delete()

    placeholders = get_lang(context, action_roll_notes.__name__)
    description = update.message.text

    add_tag_in_telegram_data(context, location="chat", tags=["action_roll", "roll", "notes"], value=description)

    trauma_victims = controller.commit_action(update.effective_message.chat_id,
                                              get_user_id(update), context.chat_data["action_roll"]["roll"])

    for victim in trauma_victims:
        update.effective_message.reply_text(placeholders["0"].format(victim[0], victim[1]), parse_mode=ParseMode.HTML,
                                            quote=False)

    return action_roll_end(update, context)


def action_roll_end(update: Update, context: CallbackContext) -> int:
    """
    Ends the action_roll conversation and deletes all the saved information from the chat_data.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: ConversationHandler.END
    """
    if get_user_id(update) == context.chat_data["action_roll"]["invoker"]:
        delete_conv_from_telegram_data(context, "action_roll", "chat")

        return end_conv(update, context)


# ------------------------------------------conv_actionRoll-------------------------------------------------------------


# ------------------------------------------conv_changeState------------------------------------------------------------


def change_state(update: Update, context: CallbackContext) -> int:
    """
    Handles the change of game state.
    Sends the user an inline keyboard with the possible states.
    If the user hasn't joined a game, or if the chat group hasn't finished the INIT phase, the conversation is canceled.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation
    """
    placeholders = get_lang(context, change_state.__name__)

    context.user_data.setdefault("change_state", {})["invocation_message"] = update.message

    if query_game_of_user(update.message.chat_id, get_user_id(update)) is None:
        update.message.reply_text(text=placeholders["err1"])
        return end_conv(update, context)

    game_id = query_game_of_user(update.message.chat_id, get_user_id(update))
    curr_state = controller.get_game_state(game_id)

    if curr_state == 0:
        if not controller.can_start_game(game_id):
            update.message.reply_text(placeholders["err2"], parse_mode=ParseMode.HTML)
            return end_conv(update, context)

    update.message.reply_text(placeholders[str(curr_state)], parse_mode=ParseMode.HTML,
                              reply_markup=custom_kb(buttons=placeholders["keyboard"], inline=True, split_row=1,
                                                     callback_data=placeholders["callback"]))

    return 0


def change_state_choice(update: Update, context: CallbackContext) -> int:
    """
    Switches the game phase accordingly with the user choice, calling Controller.change_state.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: change_state_end().
    """
    placeholders = get_lang(context, change_state_choice.__name__)

    query = update.callback_query
    query.answer()

    choice = query.data.split("$")

    controller.change_state(query_game_of_user(update.effective_message.chat_id, get_user_id(update)), int(choice[1]))
    context.user_data["change_state"]["invocation_message"].reply_text(placeholders["0"].format(
        choice[0]), parse_mode=ParseMode.HTML)

    return change_state_end(update, context)


def change_state_end(update: Update, context: CallbackContext) -> int:
    """
    Ends the conversation when /cancel is received then deletes the information collected so far
    and exits the conversation.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: ConversationHandler.END.
    """
    delete_conv_from_telegram_data(context, "change_state")

    return end_conv(update, context)


# ------------------------------------------conv_changeState------------------------------------------------------------


def roll_dice(update: Update, context: CallbackContext, dice_to_roll: int = None,
              tags: List["str"] = None, location: str = "chat", chat_id: int = None) -> None:
    """
    Rolls the specified amount of dice and interprets the result, according to BitD rules.
    If no parameters are passed after "/roll", only one die is rolled.

    :param chat_id: if specified the messages are sent to the selected chat.
    :param dice_to_roll: the number of dice to roll
    :param tags: the list of tags that states where the outcome should be saved
    :param location: specifies the dict in the telegram data ("user", "chat" or "bot"). By default it's user_data.
    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    """
    dice = 1
    if dice_to_roll is not None:
        dice = dice_to_roll
    elif context.args:
        try:
            dice = int(context.args[0])
        except ValueError:
            context.bot.send_message(chat_id, get_lang(context, roll_dice.__name__)["nan"].format(context.args[0]),
                                     parse_mode=ParseMode.HTML)
            return

    result, rolls = DiceRoller.roll_dice(dice)

    if chat_id is None:
        chat_id = update.effective_message.chat_id

    def execute(r: List[int]) -> None:
        for i in range(len(r)):
            auto_delete_message(context.bot.send_sticker(chat_id, sticker=dice_stickers[str(r[i])]),
                                (len(r) - i) * 3 + 3)
            time.sleep(3)
        time.sleep(3)

    if dice != 1:
        try:
            dice_to_send = rolls[0: ([i for i, dice in enumerate(rolls) if dice == 6][1] + 1)]
        except IndexError:
            dice_to_send = rolls.copy()
        t = Thread(target=execute, kwargs={"r": dice_to_send})
        t.start()
        t.join()

    context.bot.send_message(chat_id, get_lang(context, roll_dice.__name__)[str(result)], parse_mode=ParseMode.HTML)
    context.bot.send_sticker(chat_id, sticker=dice_stickers[str(result)])

    if tags is not None:
        add_tag_in_telegram_data(context, tags=tags, location=location, value=result)


def send_journal(update: Update, context: CallbackContext) -> None:
    placeholders = get_lang(context, send_journal.__name__)

    if query_game_of_user(update.message.chat_id, get_user_id(update)) is None:
        update.message.reply_text(placeholders["0"])
        return

    journal = controller.get_journal_of_game(query_game_of_user(update.effective_message.chat_id, get_user_id(update)))
    update.message.reply_document(document=journal[0], filename=journal[1], caption=placeholders["1"])


def send_map(update: Update, context: CallbackContext) -> None:
    placeholders = get_lang(context, send_map.__name__)

    if query_game_of_user(update.message.chat_id, get_user_id(update)) is None:
        update.message.reply_text(placeholders["0"])
        return

    map = controller.get_interactive_map(update.effective_message.chat_id, get_user_id(update))
    update.message.reply_document(document=map[0], filename=map[1], caption=placeholders["1"])


# ------------------------------------------conv_addCohort--------------------------------------------------------------


def add_cohort(update: Update, context: CallbackContext) -> int:
    """
    Handles the creation of a cohort checking if the user has already joined a game, and it's not in the INIT phase.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: next conversation's state.
    """
    placeholders = get_lang(context, add_cohort.__name__)

    if is_game_in_wrong_phase(update, context, placeholders["err"]):
        return add_cohort_end(update, context)

    if controller.get_crew_upgrade_points(query_game_of_user(update.message.chat_id, get_user_id(update))) < 2:
        message = update.message.reply_text(placeholders["err2"])
        auto_delete_message(message, 15)
        return add_cohort_end(update, context)

    add_tag_in_telegram_data(context, ["add_cohort", "invocation_message"], update.message)

    message = update.message.reply_text(placeholders["0"], reply_markup=custom_kb(placeholders["keyboard"], True, 1))

    add_tag_in_telegram_data(context, ["add_cohort", "message"], message)

    add_tag_in_telegram_data(context, ["add_cohort", "cohort"], {})

    return 0


def add_cohort_choice(update: Update, context: CallbackContext) -> int:
    """
    Stores the chosen cohort class (Gang or Expert) in the user_data and advances the conversation to
    the next state that regards the cohort's type.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: next conversation's state.
    """
    placeholders = get_lang(context, add_cohort_choice.__name__)
    context.user_data["add_cohort"]["message"].delete()

    query = update.callback_query
    query.answer()

    choice = query.data

    expert = True
    if choice.lower() != "expert":
        expert = False
    add_tag_in_telegram_data(context, ["add_cohort", "cohort", "expert"], expert)

    message = context.user_data["add_cohort"]["invocation_message"].reply_text(
        placeholders["0"], reply_markup=custom_kb(placeholders["keyboard" + str(expert)]))

    add_tag_in_telegram_data(context, ["add_cohort", "message"], message)

    return 1


def add_cohort_type(update: Update, context: CallbackContext) -> int:
    """
    Stores the chosen cohort type in the user_data and advances the conversation to
    the next state that regards the choice of the number of edges and flaws.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: next conversation's state.
    """
    placeholders = get_lang(context, add_cohort_type.__name__)
    context.user_data["add_cohort"]["message"].delete()

    add_tag_in_telegram_data(context, ["add_cohort", "cohort", "type"], update.message.text)

    message = context.user_data["add_cohort"]["invocation_message"].reply_text(placeholders["0"])
    add_tag_in_telegram_data(context, ["add_cohort", "message"], message)

    update.message.delete()
    return 2


def add_cohort_edgflaw_num(update: Update, context: CallbackContext) -> int:
    """
    Stores the chosen number of edges and flaws in the user_data and advances the conversation to
    the next state that regards the choice of the edges.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: next conversation's state.
    """
    placeholders = get_lang(context, add_cohort_edgflaw_num.__name__)
    context.user_data["add_cohort"]["message"].delete()

    num = update.message.text

    if num.isdigit():
        num = int(num)

    if isinstance(num, int) and 0 <= num <= 4:
        if num == 0:
            controller.add_cohort_in_crew(query_game_of_user(update.message.chat_id, get_user_id(update)),
                                          context.user_data["add_cohort"]["cohort"])

            return add_cohort_end(update, context)

        add_tag_in_telegram_data(context, ["add_cohort", "numEdgeFlaws"], num)

        message = context.user_data["add_cohort"]["invocation_message"].reply_text(
            placeholders["0"], reply_markup=custom_kb(
                get_lang(context, add_cohort_edges.__name__)["keyboard"], split_row=2))

        add_tag_in_telegram_data(context, ["add_cohort", "message"], message)
        update.message.delete()
        return 3
    else:
        message = context.user_data["add_cohort"]["invocation_message"].reply_text(
            placeholders["1"].format(update.message.text), parse_mode=ParseMode.HTML)
        add_tag_in_telegram_data(context, ["add_cohort", "message"], message)
        update.message.delete()
        return 2


def add_cohort_edges(update: Update, context: CallbackContext) -> int:
    """
    Stores the edges in the user_data and advances the conversation to
    the next state that regards the choice of the flaws after all the edges have been selected.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: next conversation's state.
    """
    placeholders = get_lang(context, add_cohort_edges.__name__)
    context.user_data["add_cohort"]["message"].delete()

    context.user_data["add_cohort"]["cohort"].setdefault("edges", []).append(update.message.text)

    if len(context.user_data["add_cohort"]["cohort"]["edges"]) == context.user_data["add_cohort"]["numEdgeFlaws"]:
        message = context.user_data["add_cohort"]["invocation_message"].reply_text(
            placeholders["1"], reply_markup=custom_kb(
                get_lang(context, add_cohort_flaws.__name__)["keyboard"], split_row=2))

        add_tag_in_telegram_data(context, ["add_cohort", "message"], message)

        update.message.delete()
        return 4

    else:
        message = context.user_data["add_cohort"]["invocation_message"].reply_text(
            placeholders["0"], reply_markup=custom_kb(
                get_lang(context, add_cohort_edges.__name__)["keyboard"], split_row=2))

        add_tag_in_telegram_data(context, ["add_cohort", "message"], message)

        update.message.delete()
        return 3


def add_cohort_flaws(update: Update, context: CallbackContext) -> int:
    """
    Stores the flaws in the user_data and advances the conversation to
    the end state after all the edges have been selected; before advancing to the next state the new cohort is stored
    calling the Controller method add_cohort_in_crew().

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: next conversation's state.
    """
    placeholders = get_lang(context, add_cohort_flaws.__name__)
    context.user_data["add_cohort"]["message"].delete()

    context.user_data["add_cohort"]["cohort"].setdefault("flaws", []).append(update.message.text)

    if len(context.user_data["add_cohort"]["cohort"]["flaws"]) == context.user_data["add_cohort"]["numEdgeFlaws"]:

        controller.add_cohort_in_crew(
            query_game_of_user(update.message.chat_id, get_user_id(update)), context.user_data["add_cohort"]["cohort"])

        return add_cohort_end(update, context)

    else:
        message = context.user_data["add_cohort"]["invocation_message"].reply_text(
            placeholders["0"], reply_markup=custom_kb(placeholders["keyboard"], split_row=2))

        add_tag_in_telegram_data(context, ["add_cohort", "message"], message)

        update.message.delete()
        return 4


def add_cohort_end(update: Update, context: CallbackContext) -> int:
    """
    Ends the conversation when /cancel is received then deletes the information collected so far
    and exits the conversation.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: ConversationHandler.END.
    """
    delete_conv_from_telegram_data(context, "add_cohort")

    return end_conv(update, context)


# ------------------------------------------conv_addCohort--------------------------------------------------------------


# ------------------------------------------conv_createClock------------------------------------------------------------


def create_clock(update: Update, context: CallbackContext) -> int:
    """
    Handles the creation of a clock checking if the user has already joined a game, and it's not in the INIT phase.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: next conversation's state.
    """
    placeholders = get_lang(context, create_clock.__name__)

    if is_game_in_wrong_phase(update, context, placeholders["err"]):
        return create_clock_end(update, context)

    add_tag_in_telegram_data(context, ["create_clock", "invocation_message"], update.message)

    message = update.message.reply_text(placeholders["0"])

    add_tag_in_telegram_data(context, ["create_clock", "message"], message)

    add_tag_in_telegram_data(context, ["create_clock", "clock"], {})

    add_tag_in_telegram_data(context, ["create_clock", "clock", "name"], "")

    return 0


def create_project_clock(update: Update, context: CallbackContext) -> Optional[int]:
    """
    Handles the creation of a project clock in the middle of the downtime activity,
    checking if the user has already joined a game, and it's not in the INIT phase.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: next conversation's state.
    """
    placeholders = get_lang(context, create_clock.__name__)

    if "downtime" in context.chat_data and "invoker" in context.chat_data["downtime"]:
        if get_user_id(update) != context.chat_data["downtime"]["invoker"]:
            return
    else:
        return

    if is_game_in_wrong_phase(update, context, placeholders["err"]):
        return create_clock_end(update, context)

    add_tag_in_telegram_data(context, ["create_clock", "invocation_message"], update.message)

    message = update.message.reply_text(placeholders["0"])

    add_tag_in_telegram_data(context, ["create_clock", "message"], message)

    add_tag_in_telegram_data(context, ["create_clock", "clock"], {})

    add_tag_in_telegram_data(context, ["create_clock", "clock", "name"], "[project] ")

    return 0


def create_clock_name(update: Update, context: CallbackContext) -> int:
    """
    Stores the chosen clock name in the user_data and advances the conversation to
    the next state that regards the clock's number of segments.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: next conversation's state.
    """
    placeholders = get_lang(context, create_clock_name.__name__)
    context.user_data["create_clock"]["message"].delete()
    clock_name = update.message.text
    if "[project]" in clock_name:
        message = context.user_data["create_clock"]["invocation_message"].reply_text(placeholders["1"])
        add_tag_in_telegram_data(context, ["create_clock", "message"], message)
        update.message.delete()
        return 0

    context.user_data["create_clock"]["clock"]["name"] += clock_name

    message = context.user_data["create_clock"]["invocation_message"].reply_text(
        placeholders["0"], reply_markup=custom_kb(placeholders["keyboard"]))

    add_tag_in_telegram_data(context, ["create_clock", "message"], message)

    update.message.delete()
    return 1


def create_clock_segments(update: Update, context: CallbackContext) -> int:
    """
    Stores the clock's number of segments in the user_data and advances the conversation to
    the end state; before advancing to the next state the new clock is stored
    calling the Controller method add_clock_to_game().

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: next conversation's state.
    """
    placeholders = get_lang(context, create_clock_segments.__name__)
    context.user_data["create_clock"]["message"].delete()

    num = update.message.text

    if num.isdigit():
        num = int(num)

    if isinstance(num, int) and 2 <= num <= 36:
        add_tag_in_telegram_data(context, ["create_clock", "clock", "segments"], num)
    else:
        message = context.user_data["create_clock"]["invocation_message"].reply_text(
            placeholders["1"].format(update.message.text), parse_mode=ParseMode.HTML)
        add_tag_in_telegram_data(context, ["create_clock", "message"], message)
        update.message.delete()
        return 1

    controller.add_clock_to_game(update.message.chat_id, get_user_id(update),
                                 context.user_data["create_clock"]["clock"])

    if controller.is_master(get_user_id(update), update.message.chat_id):
        name = "The GM"
    else:
        name = query_users_names(get_user_id(update))[0]

    update.message.reply_text(placeholders["0"].format(
        name, context.user_data["create_clock"]["clock"]["segments"],
        context.user_data["create_clock"]["clock"]["name"]), quote=False, parse_mode=ParseMode.HTML)

    if "[project]" in context.user_data["create_clock"]["clock"]["name"]:
        placeholders = get_lang(context, downtime_project_choice.__name__)

        new_clock = controller.get_clocks_of_game(query_game_of_user(update.message.chat_id, get_user_id(update)), True)
        new_clock = new_clock[len(new_clock) - 1]
        name = new_clock.split(": ")[0]

        choice = new_clock.split(": ")[1]
        segments = int(choice.split("/")[1])
        add_tag_in_telegram_data(context, ["downtime", "info", "clock", "name"], name, "chat")
        add_tag_in_telegram_data(context, ["downtime", "info", "clock", "segments"], segments, "chat")
        add_tag_in_telegram_data(context, ["downtime", "info", "clock", "progress"], 0, "chat")

        keyboard = query_attributes(True)
        message = context.chat_data["downtime"]["invocation_message"].reply_text(
            placeholders["1"], reply_markup=custom_kb(keyboard, True, 1))
        add_tag_in_telegram_data(context, ["downtime", "message"], message, "chat")

    return create_clock_end(update, context)


def create_clock_end(update: Update, context: CallbackContext) -> int:
    """
    Ends the conversation when /cancel is received then deletes the information collected so far
    and exits the conversation.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: ConversationHandler.END.
    """
    delete_conv_from_telegram_data(context, "create_clock")

    return end_conv(update, context)


# ------------------------------------------conv_createClock------------------------------------------------------------


# ------------------------------------------conv_tickClock--------------------------------------------------------------


def tick_clock(update: Update, context: CallbackContext) -> int:
    """
    Handles the advancement of a clock checking if the user has already joined a game, and it's not in the INIT phase.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: next conversation's state.
    """
    placeholders = get_lang(context, tick_clock.__name__)

    if is_game_in_wrong_phase(update, context, placeholders["err"]):
        return create_clock_end(update, context)

    add_tag_in_telegram_data(context, ["tick_clock", "invocation_message"], update.message)

    clocks = controller.get_clocks_of_game(query_game_of_user(update.message.chat_id, get_user_id(update)))
    if not clocks:
        update.message.reply_text(placeholders["err2"])
        return tick_clock_end(update, context)

    message = update.message.reply_text(placeholders["0"], reply_markup=custom_kb(clocks, inline=True, split_row=1))
    add_tag_in_telegram_data(context, ["tick_clock", "message"], message)

    add_tag_in_telegram_data(context, ["tick_clock", "old_clock"], {})

    return 0


def tick_clock_choice(update: Update, context: CallbackContext) -> int:
    """
    Stores the chosen clock in the user_data and advances the conversation to
    the next state that regards the number of ticks to advance the clock.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: next conversation's state.
    """
    placeholders = get_lang(context, tick_clock_choice.__name__)
    context.user_data["tick_clock"]["message"].delete()

    query = update.callback_query
    query.answer()

    choice = query.data

    name = choice.split(": ")[0]

    choice = choice.split(": ")[1]

    progress = int(choice.split("/")[0])
    segments = int(choice.split("/")[1])

    add_tag_in_telegram_data(context, ["tick_clock", "old_clock", "name"], name)
    add_tag_in_telegram_data(context, ["tick_clock", "old_clock", "segments"], segments)
    add_tag_in_telegram_data(context, ["tick_clock", "old_clock", "progress"], progress)

    message = context.user_data["tick_clock"]["invocation_message"].reply_text(placeholders["0"])
    add_tag_in_telegram_data(context, ["tick_clock", "message"], message)

    return 1


def tick_clock_progress(update: Update, context: CallbackContext) -> int:
    """
    Stores the number of ticks in the user_data and advances the conversation to
    the end state; before advancing to the next state the clock is ticked and stored
    calling the Controller method tick_clock_of_game().

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: next conversation's state.
    """
    placeholders = get_lang(context, tick_clock_progress.__name__)
    context.user_data["tick_clock"]["message"].delete()

    num = update.message.text

    try:
        num = int(num)
    except ValueError:
        message = context.user_data["tick_clock"]["invocation_message"].reply_text(
            placeholders["err"].format(update.message.text), parse_mode=ParseMode.HTML)
        add_tag_in_telegram_data(context, ["tick_clock", "message"], message)
        update.message.delete()
        return 1

    add_tag_in_telegram_data(context, ["tick_clock", "ticks"], num)

    finished, new_clock = controller.tick_clock_of_game(update.message.chat_id, get_user_id(update),
                                                        context.user_data["tick_clock"]["old_clock"],
                                                        context.user_data["tick_clock"]["ticks"])

    if controller.is_master(get_user_id(update), update.message.chat_id):
        username = "The GM"
    else:
        username = query_users_names(get_user_id(update))[0]

    if finished:
        context.user_data["tick_clock"]["invocation_message"].reply_text(
            placeholders["1"].format(username, new_clock["name"]), parse_mode=ParseMode.HTML)
    else:
        context.user_data["tick_clock"]["invocation_message"].reply_text(
            placeholders["0"].format(username, new_clock["name"], new_clock["progress"], new_clock["segments"]),
            parse_mode=ParseMode.HTML)

    return tick_clock_end(update, context)


def tick_clock_end(update: Update, context: CallbackContext) -> int:
    """
    Ends the conversation when /cancel is received then deletes the information collected so far
    and exits the conversation.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: ConversationHandler.END.
    """
    delete_conv_from_telegram_data(context, "tick_clock")

    return end_conv(update, context)


# ------------------------------------------conv_tickClock--------------------------------------------------------------

# ------------------------------------------conv_addClaim---------------------------------------------------------------

def add_claim(update: Update, context: CallbackContext) -> int:
    """
    Handles the addition of a new claim checking if the user has already joined a game, and it's not in the INIT phase.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: next conversation's state.
    """
    placeholders = get_lang(context, add_claim.__name__)

    if is_game_in_wrong_phase(update, context, placeholders["err"]):
        return add_claim_end(update, context)

    add_tag_in_telegram_data(context, ["add_claim", "invocation_message"], update.message)

    message = update.message.reply_text(placeholders["0"], reply_markup=custom_kb(
        placeholders["keyboard"], inline=True, split_row=1, callback_data=placeholders["callbacks"]))
    add_tag_in_telegram_data(context, ["add_claim", "message"], message)

    add_tag_in_telegram_data(context, ["add_claim", "claim"], {})

    return 0


def add_claim_type(update: Update, context: CallbackContext) -> int:
    """
    Stores the chosen claim type in the user_data and advances the conversation to
    the next state that regards the claim selection.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: next conversation's state.
    """
    placeholders = get_lang(context, add_claim_type.__name__)
    context.user_data["add_claim"]["message"].delete()

    query = update.callback_query
    query.answer()

    choice = bool(query.data == "True")

    add_tag_in_telegram_data(context, ["add_claim", "claim", "prison"], choice)

    claims_names = [claim["name"] for claim in query_claims(prison=choice, as_dict=True)]

    buttons_list = []
    buttons = []
    for i in range(len(claims_names)):
        buttons.append(claims_names[i])
        if (i + 1) % 8 == 0:
            buttons_list.append(buttons.copy())
            buttons.clear()
    if buttons:
        buttons_list.append(buttons.copy())

    add_tag_in_telegram_data(context, tags=["add_claim", "buttons_list"], value=buttons_list)

    query_menu = context.user_data["add_claim"]["invocation_message"].reply_text(
        placeholders["0"], reply_markup=build_multi_page_kb(buttons_list[0]))
    add_tag_in_telegram_data(context, ["add_claim", "query_menu"], query_menu)
    add_tag_in_telegram_data(context, ["add_claim", "query_menu_index"], 0)

    return 1


def add_claim_name(update: Update, context: CallbackContext) -> int:
    placeholders = get_lang(context, add_claim_type.__name__)

    query = update.callback_query
    query.answer()

    choice = query.data
    index = context.user_data["add_claim"]["query_menu_index"]

    if choice == "RIGHT":
        index += 1
        if index > len(context.user_data["add_claim"]["buttons_list"]):
            index = 0
        context.user_data["add_claim"]["query_menu_index"] = index

    elif choice == "LEFT":
        index -= 1
        if index == -len(context.user_data["add_claim"]["buttons_list"]):
            index = 0

        context.user_data["add_claim"]["query_menu_index"] = index

    else:
        name = choice.split("$")[0]
        description = query_claims(name=name, as_dict=True)[0]["description"]
        if "$" in choice:
            choice = choice.split("$")[0]
            add_tag_in_telegram_data(context, ["add_claim", "claim", "name"], choice)
            add_tag_in_telegram_data(context, ["add_claim", "claim", "description"], description)

            controller.add_claim_to_game(query_game_of_user(update.effective_message.chat_id, get_user_id(update)),
                                         context.user_data["add_claim"]["claim"])

            return add_claim_end(update, context)

        else:
            auto_delete_message(update.effective_message.reply_text(
                text=description, quote=False), description)
            return 1

    context.user_data["add_claim"]["query_menu"].edit_text(
        placeholders["0"], reply_markup=build_multi_page_kb(
            context.user_data["add_claim"]["buttons_list"][context.user_data["add_claim"]["query_menu_index"]]))
    return 1


def add_claim_end(update: Update, context: CallbackContext) -> int:
    """
    Ends the conversation when /cancel is received then deletes the information collected so far
    and exits the conversation.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: ConversationHandler.END.
    """
    delete_conv_from_telegram_data(context, "add_claim")

    return end_conv(update, context)


# ------------------------------------------conv_addClaim---------------------------------------------------------------

# ------------------------------------------conv_score------------------------------------------------------------------

def score(update: Update, context: CallbackContext) -> int:
    """
    Checks if the user's game is in the right phase and starts the conversation to create a new score.
    Adds the dict "score" in chat_data and stores the ID of the invoker.
    Finally, it sends the score category request.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, score.__name__)

    if is_game_in_wrong_phase(update, context, placeholders["err"], 3):
        return score_end(update, context)

    add_tag_in_telegram_data(context, location="chat", tags=["score", "invoker"], value=get_user_id(update))
    add_tag_in_telegram_data(context, location="chat", tags=["score", "invocation_message"], value=update.message)

    message = update.message.reply_text(placeholders["0"], reply_markup=custom_kb(
        placeholders["keyboard"], split_row=1))
    add_tag_in_telegram_data(context, location="chat", tags=["score", "message"], value=message)

    user_id = get_user_id(update)

    context.chat_data["score"].setdefault("players", []).append((user_id,
                                                                 context.user_data["active_PCs"][
                                                                     update.effective_message.chat_id]))
    context.chat_data["score"].setdefault("score_info", {}).setdefault(
        "members", {}).setdefault(
        user_id, {})[context.user_data["active_PCs"][update.effective_message.chat_id]] = 3

    return 0


def score_category(update: Update, context: CallbackContext) -> int:
    """
    Stores the score's category in the chat_data and sends the keyboard with the request of the target's type.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    if get_user_id(update) == context.chat_data["score"]["invoker"]:
        context.chat_data["score"]["message"].delete()

        placeholders = get_lang(context, score_category.__name__)

        add_tag_in_telegram_data(context, location="chat", tags=["score", "score_info", "category"],
                                 value=update.message.text)

        message = context.chat_data["score"]["invocation_message"].reply_text(
            placeholders["0"],
            reply_markup=custom_kb(placeholders["keyboard"],
                                   inline=True,
                                   callback_data=placeholders["callbacks"]))
        add_tag_in_telegram_data(context, location="chat", tags=["score", "message"], value=message)

        update.message.delete()

        return 0


def score_target(update: Update, context: CallbackContext) -> int:
    """
    Handles the selection of the target's type. If NPC or Faction is selected, it requests the list of NPCs or Factions
    to the Controller to build an InlineKeyboard.
    In any case the target request is sent.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, score_target.__name__)
    chat_id = update.effective_message.chat_id

    query = update.callback_query
    query.answer()

    choice = query.data
    if choice == "NPC":
        npcs = controller.get_npcs(query_game_of_user(chat_id, get_user_id(update)))

        buttons_list = []
        buttons = []
        for i in range(len(npcs)):
            buttons.append(npcs[i])
            if (i + 1) % 8 == 0:
                buttons_list.append(buttons.copy())
                buttons.clear()
        if buttons:
            buttons_list.append(buttons.copy())
        add_tag_in_telegram_data(context, location="chat", tags=["score", "buttons_list"], value=buttons_list)

        context.chat_data["score"]["query_menu"] = context.chat_data["score"]["invocation_message"].reply_text(
            placeholders["0"],
            parse_mode=ParseMode.HTML,
            reply_markup=build_multi_page_kb(buttons_list[0]))
    elif choice == "Faction":
        factions = controller.get_factions(query_game_of_user(chat_id, get_user_id(update)))

        buttons_list = []
        buttons = []
        for i in range(len(factions)):
            buttons.append(factions[i])
            if (i + 1) % 8 == 0:
                buttons_list.append(buttons.copy())
                buttons.clear()
        if buttons:
            buttons_list.append(buttons.copy())
        add_tag_in_telegram_data(context, location="chat", tags=["score", "buttons_list"], value=buttons_list)

        context.chat_data["score"]["query_menu"] = context.chat_data["score"]["invocation_message"].reply_text(
            placeholders["0"],
            parse_mode=ParseMode.HTML,
            reply_markup=build_multi_page_kb(buttons_list[0]))
    elif choice == "Other":
        context.chat_data["score"]["message"].delete()
        context.chat_data["score"]["message"] = context.chat_data["score"]["invocation_message"].reply_text(
            placeholders["1"],
            parse_mode=ParseMode.HTML)
        add_tag_in_telegram_data(context, location="chat", tags=["score", "score_info", "target", "type"], value=choice)
        return 2

    add_tag_in_telegram_data(context, location="chat", tags=["score", "query_menu_index"], value=0)
    add_tag_in_telegram_data(context, location="chat", tags=["score", "score_info", "target", "type"], value=choice)

    context.chat_data["score"]["message"].delete()
    return 1


def score_target_custom(update: Update, context: CallbackContext) -> int:
    """
    Stores the information about a custom target in the chat_data.
    Sends the score's plan type request.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, score_target_selection.__name__)
    context.chat_data["score"]["message"].delete()
    add_tag_in_telegram_data(context, location="chat", tags=["score", "score_info", "target", "name"],
                             value=update.message.text)
    message = context.chat_data["score"]["invocation_message"].reply_text(text=placeholders["1"],
                                                                          parse_mode=ParseMode.HTML,
                                                                          reply_markup=custom_kb(
                                                                              placeholders["keyboard"]),
                                                                          )
    add_tag_in_telegram_data(context, location="chat", tags=["score", "message"], value=message)

    update.message.delete()
    return 3


def score_target_selection(update: Update, context: CallbackContext) -> int:
    """
    Stores the information about an NPC or Faction target in the chat_data.
    Sends the score's plan type request.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, score_target_selection.__name__)

    query = update.callback_query
    query.answer()

    choice = query.data
    index = context.chat_data["score"]["query_menu_index"]

    if choice == "RIGHT":
        index += 1
        if index > len(context.chat_data["score"]["buttons_list"]):
            index = 0
        context.chat_data["score"]["query_menu_index"] = index

    elif choice == "LEFT":
        index -= 1
        if index == -len(context.chat_data["score"]["buttons_list"]):
            index = 0

        context.chat_data["score"]["query_menu_index"] = index
    else:
        name = choice.split("$")[0]
        name = name.split(" - ")[1]
        if "$" in choice:
            add_tag_in_telegram_data(context, location="chat", tags=["score", "score_info", "target", "name"],
                                     value=name)
            message = context.chat_data["score"]["invocation_message"].reply_text(text=placeholders["1"],
                                                                                  parse_mode=ParseMode.HTML,
                                                                                  reply_markup=custom_kb(
                                                                                      placeholders["keyboard"]))
            add_tag_in_telegram_data(context, location="chat", tags=["score", "message"], value=message)
            context.chat_data["score"]["query_menu"].delete()
            return 3
        else:
            description = ""
            if context.chat_data["score"]["score_info"]["target"]["type"] == "NPC":
                npc_name = name.split(", ")[0]
                npc_role = name.split(", ")[1]
                description = query_npcs(name=npc_name,
                                         role=npc_role, as_dict=True)[0]["description"]
            elif context.chat_data["score"]["score_info"]["target"]["type"] == "Faction":
                faction_name = name.split(": ")[0]
                description = query_factions(name=faction_name, as_dict=True)[0]["description"]

            if description is None or description == "":
                description = placeholders["404"]
            auto_delete_message(update.effective_message.reply_text(
                text=description, quote=False), description)
            return 1

    context.chat_data["score"]["query_menu"].edit_text(
        placeholders["0"], reply_markup=build_multi_page_kb(
            context.chat_data["score"]["buttons_list"][context.chat_data["score"]["query_menu_index"]]))
    return 1


def score_plan_type(update: Update, context: CallbackContext) -> int:
    """
    Stores the information about the plan type in the chat_data.
    Sends the score's plan details request.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    context.chat_data["score"]["message"].delete()

    placeholders = get_lang(context, score_plan_type.__name__)

    add_tag_in_telegram_data(context, location="chat", tags=["score", "score_info", "plan_type"],
                             value=update.message.text)

    try:
        text = placeholders[update.message.text]
    except KeyError:
        text = placeholders["Other"]
    message = context.chat_data["score"]["invocation_message"].reply_text(text, parse_mode=ParseMode.HTML)

    add_tag_in_telegram_data(context, location="chat", tags=["score", "message"], value=message)

    update.message.delete()

    return 4


def score_plan_details(update: Update, context: CallbackContext) -> int:
    """
    Stores the information about the plan's details the chat_data.
    Sends the score's title request.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    context.chat_data["score"]["message"].delete()

    placeholders = get_lang(context, score_plan_details.__name__)

    add_tag_in_telegram_data(context, location="chat", tags=["score", "score_info", "plan_details"],
                             value=update.message.text)

    message = context.chat_data["score"]["invocation_message"].reply_text(placeholders["0"])

    add_tag_in_telegram_data(context, location="chat", tags=["score", "message"], value=message)

    update.message.delete()

    return 5


def score_title(update: Update, context: CallbackContext) -> int:
    """
    Stores the title of the score in the chat_data.
    Sends the load request in the game's chat.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    context.chat_data["score"]["message"].delete()
    placeholders = get_lang(context, score_title.__name__)

    add_tag_in_telegram_data(context, location="chat", tags=["score", "score_info", "title"],
                             value=update.message.text)

    message = context.chat_data["score"]["invocation_message"].reply_text(placeholders["0"].format(
        context.chat_data["score"]["players"][0][1]),
        parse_mode=ParseMode.HTML,
        reply_markup=custom_kb(
            placeholders["keyboard"],
            selective=False))

    add_tag_in_telegram_data(context, location="chat", tags=["score", "message"], value=message)

    update.message.delete()

    return 6


def score_engagement(update: Update, context: CallbackContext) -> int:
    """
    Handles the selection of the total number of dice for the engagement roll.
    When the DONE button is pressed, it calls the roll_dice method to get the result and sends the final notes request.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    if get_user_id(update) == context.chat_data["score"]["invoker"]:
        placeholders = get_lang(context, score_engagement.__name__)

        query = update.callback_query
        query.answer()

        bonus_dice = context.chat_data["score"]["dice"]

        choice = query.data
        if "+" in choice or "-" in choice:
            bonus_dice += int(choice.split(" ")[2])
            add_tag_in_telegram_data(context, location="chat",
                                     tags=["score", "dice"], value=bonus_dice)

            update_bonus_dice_kb(context, ["score", "dice"], tot_dice=bonus_dice, message_tag="score",
                                 button_tag="engagement")

        elif choice == "DONE":
            dice_to_roll = context.chat_data["score"]["dice"]

            context.chat_data["score"]["query_menu"].delete()

            roll_dice(update, context, dice_to_roll, ["score", "score_info", "outcome"])

            context.chat_data["score"]["message"] = \
                context.chat_data["score"]["invocation_message"].reply_text(
                    placeholders["0"], parse_mode=ParseMode.HTML)
            return 1

        else:
            bonus_dice_lang = get_lang(context, "bonus_dice")
            auto_delete_message(
                update.effective_message.reply_text(bonus_dice_lang["score"], parse_mode=ParseMode.HTML),
                bonus_dice_lang["engagement_extended"])

        return 0


def score_notes(update: Update, context: CallbackContext) -> int:
    """
    Stores the final description of the score in the chat_data, calls the controller method to apply the roll's
    effects and sends the notification for the PCs who suffered a new trauma after this action.
    Finally, calls action_roll_end.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: call to score_end
    """
    context.chat_data["score"]["message"].delete()

    description = update.message.text

    add_tag_in_telegram_data(context, location="chat", tags=["score", "score_info", "notes"], value=description)

    controller.add_new_score(update.effective_message.chat_id,
                             get_user_id(update), context.chat_data["score"]["score_info"])

    return score_end(update, context)


def score_pcs_loads(update: Update, context: CallbackContext) -> int:
    """
    Listens for the first user in the chat who has to select the load for the score.
    Stores the received value in the chat_data, pops the user from the temporary list and if the list in not empty
    sends the same message for the next user. Otherwise, the conversation is moved to the engagement roll state.

    :param update:
    :param context:
    :return:
    """
    user_id = get_user_id(update)

    if user_id == context.chat_data["score"]["players"][0][0]:
        placeholders = get_lang(context, score_pcs_loads.__name__)

        load = update.message.text
        try:
            load = int(load)
        except ValueError:
            update.message.reply_text(placeholders["nan"].format(context.args[0]),
                                      parse_mode=ParseMode.HTML)
            return 1

        context.chat_data["score"]["score_info"]["members"][user_id][context.chat_data["score"]["players"][0][1]] = load
        context.chat_data["score"]["players"].pop(0)

        if not context.chat_data["score"]["players"]:
            bonus_dice_lang = get_lang(context, "bonus_dice")
            add_tag_in_telegram_data(context, location="chat", tags=["score", "dice"], value=1)
            query_menu = context.chat_data["score"]["invocation_message"].reply_text(bonus_dice_lang["score"].format(
                1),
                reply_markup=build_plus_minus_keyboard(
                    [bonus_dice_lang["engagement"].format(
                        context.chat_data["score"]["dice"])],
                    done_button=True,
                    back_button=False),
                parse_mode=ParseMode.HTML)

            add_tag_in_telegram_data(context, location="chat", tags=["score", "query_menu"], value=query_menu)
            return 2

        next_player = context.chat_data["score"]["players"][0]

        message = context.chat_data["score"]["invocation_message"].reply_text(placeholders["0"].format(
            next_player[1]),
            parse_mode=ParseMode.HTML,
            reply_markup=custom_kb(
                placeholders["keyboard"],
                selective=False))

        add_tag_in_telegram_data(context, location="chat", tags=["score", "message"], value=message)

        return 1


def score_load(update: Update, context: CallbackContext):
    """
    Stores the information of the user who decided to join the score in the chat_data.
    Adds to the temporary list of users the user's id

    :param update:
    :param context:
    :return:
    """
    placeholders = get_lang(context, score_load.__name__)

    user_id = get_user_id(update)
    chat_id = update.effective_message.chat_id
    invoker_id = context.chat_data["score"]["invoker"]

    if user_id != invoker_id:
        if query_game_of_user(chat_id, user_id) == query_game_of_user(chat_id, invoker_id):
            if "active_PCs" in context.user_data and chat_id in context.user_data["active_PCs"]:

                new_member = context.user_data["active_PCs"][chat_id]

                if "members" in context.chat_data["score"]["score_info"]:
                    if user_id in context.chat_data["score"]["score_info"]["members"]:
                        if new_member in context.chat_data["score"]["score_info"][user_id]:
                            auto_delete_message(update.message.reply_text(
                                placeholders["1"], parse_mode=ParseMode.HTML), 10)

                            return

                # default load is 3
                context.chat_data["score"].setdefault("players", []).append((user_id, new_member))
                context.chat_data["score"].setdefault("score_info", {}).setdefault(
                    "members", {}).setdefault(user_id, {})[new_member] = 3

                auto_delete_message(
                    update.message.reply_text(placeholders["0"].format(context.user_data["active_PCs"][chat_id]),
                                              parse_mode=ParseMode.HTML), 18)
                return

    auto_delete_message(
        update.message.reply_text(placeholders["2"], parse_mode=ParseMode.HTML), 18)


def score_end(update: Update, context: CallbackContext) -> int:
    """
    Ends the conversation when /cancel is received then deletes the information collected so far
    and exits the conversation.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: ConversationHandler.END.
    """
    delete_conv_from_telegram_data(context, "score", "chat")

    return end_conv(update, context)


# ------------------------------------------conv_score------------------------------------------------------------------

# ------------------------------------------send_sheets-----------------------------------------------------------------

def send_character_sheet(update: Update, context: CallbackContext) -> None:
    placeholders = get_lang(context, send_character_sheet.__name__)
    chat_id = update.effective_message.chat_id

    if is_user_not_in_game(update, placeholders["err"]):
        return

    if "active_PCs" in context.user_data and chat_id in context.user_data["active_PCs"]:
        img_bytes, file_name = controller.get_character_sheet_image(chat_id, get_user_id(update),
                                                                    context.user_data["active_PCs"][chat_id])

        update.effective_message.reply_photo(photo=img_bytes, filename=file_name, caption=placeholders["1"])
    else:
        update.message.reply_text(placeholders["0"])


def send_crew_sheet(update: Update, context: CallbackContext) -> None:
    placeholders = get_lang(context, send_crew_sheet.__name__)

    if is_user_not_in_game(update, placeholders["err"]):
        return

    if controller.game_has_crew(query_game_of_user(update.effective_message.chat_id, get_user_id(update))):
        chat_id = update.effective_message.chat_id
        img_bytes, file_name = controller.get_crew_sheet_image(query_game_of_user(chat_id, get_user_id(update)))
        update.effective_message.reply_photo(photo=img_bytes, filename=file_name, caption=placeholders["1"])
    else:
        update.message.reply_text(placeholders["0"])


# ------------------------------------------send_sheets-----------------------------------------------------------------


# ------------------------------------------conv_resistanceRoll---------------------------------------------------------


def resistance_roll(update: Update, context: CallbackContext) -> int:
    """
    Checks if the user controls a PC in this chat and starts the conversation of the resistance roll.
    Adds the dict "resistance_roll" in chat_data and stores the ID of the invoker and his active PC in it.
    Finally, sends the goal request.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    if "active_PCs" in context.user_data and update.effective_message.chat_id in context.user_data["active_PCs"]:
        placeholders = get_lang(context, resistance_roll.__name__)

        if is_game_in_wrong_phase(update, context, placeholders["1"]):
            return resistance_roll_end(update, context)

        message = update.effective_message.reply_text(placeholders["0"])
        add_tag_in_telegram_data(context, location="chat", tags=["resistance_roll", "message"], value=message)
        add_tag_in_telegram_data(context, location="chat", tags=["resistance_roll", "invocation_message"],
                                 value=update.message)
        add_tag_in_telegram_data(context, location="chat", tags=["resistance_roll", "invoker"],
                                 value=get_user_id(update))
        add_tag_in_telegram_data(context, location="chat", tags=["resistance_roll", "roll", "pc"],
                                 value=context.user_data["active_PCs"][update.effective_message.chat_id])
        return 0


def resistance_roll_description(update: Update, context: CallbackContext) -> int:
    """
    Stores the goal's description in the chat_data and sends the master the keyboard with how the PC will deal with the
    damage.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: he next state of the conversation.
    """
    if get_user_id(update) == context.chat_data["resistance_roll"]["invoker"]:
        context.chat_data["resistance_roll"]["message"].delete()
        placeholders = get_lang(context, resistance_roll_description.__name__)

        add_tag_in_telegram_data(context, location="chat", tags=["resistance_roll", "roll", "description"],
                                 value=update.message.text)

        message = context.chat_data["resistance_roll"]["invocation_message"].reply_text(placeholders["1"].format(
            context.chat_data["resistance_roll"]["roll"]["pc"],
            context.chat_data["resistance_roll"]["roll"]["description"]), parse_mode=ParseMode.HTML)

        add_tag_in_telegram_data(context, location="chat", tags=["resistance_roll", "message"], value=message)

        add_tag_in_telegram_data(context, location="chat", tags=["resistance_roll", "GM_question"],
                                 value={"text": placeholders["0"], "reply_markup": custom_kb(
                                     buttons=placeholders["keyboard"],
                                     split_row=1,
                                     inline=True,
                                     callback_data=placeholders["callbacks"])})

        update.message.delete()

        return 1


def resistance_roll_damage(update: Update, context: CallbackContext) -> int:
    """
    Stores how the PC will deal with the damage and sends the GM a keyboard with all the PC's attributes
    and their ratings.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, resistance_roll_damage.__name__)
    context.chat_data["resistance_roll"]["message"].delete()

    query = update.callback_query
    query.answer()
    choice = query.data

    add_tag_in_telegram_data(context, location="chat", tags=["resistance_roll", "roll", "damage"], value=choice)

    chat_id = update.effective_message.chat_id

    attributes_ratings = controller.get_pc_attribute_rating(chat_id, context.chat_data["resistance_roll"]["invoker"],
                                                            context.chat_data["resistance_roll"]["roll"]["pc"])

    buttons = ["{}: {}".format(attribute[0], attribute[1]) for attribute in attributes_ratings]

    context.chat_data["resistance_roll"]["message"] = context.chat_data["resistance_roll"][
        "invocation_message"].reply_text(placeholders["0"],
                                         parse_mode=ParseMode.HTML,
                                         reply_markup=custom_kb(buttons, inline=True))

    return 1


def resistance_roll_attribute(update: Update, context: CallbackContext) -> int:
    """
    Stores the attribute chosen by the GM in the chat_data and sends the user the bonus dice keyboard.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """

    query = update.callback_query
    query.answer()
    choice = query.data

    add_tag_in_telegram_data(context, location="chat", tags=["resistance_roll", "roll", "attribute"], value=choice)

    context.chat_data["resistance_roll"]["message"].delete()

    add_tag_in_telegram_data(context, location="chat", tags=["resistance_roll", "roll", "bonus_dice"], value=0)

    dice = resistance_roll_calc_total_dice(context.chat_data["resistance_roll"]["roll"])

    bonus_dice_lang = get_lang(context, "bonus_dice")

    query_menu = context.chat_data["resistance_roll"]["invocation_message"].reply_text(
        bonus_dice_lang["message"].format(
            dice),
        reply_markup=build_plus_minus_keyboard(
            [bonus_dice_lang["button"].format(
                context.chat_data["resistance_roll"]["roll"]["bonus_dice"])],
            done_button=True,
            back_button=False),
        parse_mode=ParseMode.HTML)

    add_tag_in_telegram_data(context, location="chat", tags=["resistance_roll", "query_menu"], value=query_menu)

    return 2


def resistance_roll_bonus_dice(update: Update, context: CallbackContext) -> int:
    """
    Handles the addition or removal of bonus dice and updates the related Keyboard.
    When the user confirms, the number of dice to roll is passed to roll_dice method.
    Then, the outcome is stored in the chat_data and the final description request is sent.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation when the "DONE" button is pressed.
    """
    placeholders = get_lang(context, resistance_roll_bonus_dice.__name__)

    if get_user_id(update) != context.chat_data["resistance_roll"]["invoker"]:
        return 2

    query = update.callback_query
    query.answer()

    bonus_dice = context.chat_data["resistance_roll"]["roll"]["bonus_dice"]

    choice = query.data
    if "+" in choice or "-" in choice:
        tags = ["resistance_roll", "roll", "bonus_dice"]
        bonus_dice += int(choice.split(" ")[2])
        add_tag_in_telegram_data(context, location="chat", tags=tags, value=bonus_dice)

        update_bonus_dice_kb(context, tags,
                             resistance_roll_calc_total_dice(context.chat_data["resistance_roll"]["roll"]))

    elif choice == "DONE":
        dice_to_roll = resistance_roll_calc_total_dice(context.chat_data["resistance_roll"]["roll"])

        context.chat_data["resistance_roll"]["query_menu"].delete()

        roll_dice(update, context, dice_to_roll, ["resistance_roll", "roll", "outcome"])

        context.chat_data["resistance_roll"]["message"] = \
            context.chat_data["resistance_roll"]["invocation_message"].reply_text(
                placeholders["0"], parse_mode=ParseMode.HTML)
        return 0

    else:
        bonus_dice_lang = get_lang(context, "bonus_dice")
        auto_delete_message(update.effective_message.reply_text(bonus_dice_lang["extended"], parse_mode=ParseMode.HTML),
                            bonus_dice_lang["extended"])

    return 2


def resistance_roll_notes(update: Update, context: CallbackContext) -> int:
    """
    Stores the final description of the resistance roll in the chat_data, calls the controller method to apply the roll's
    effects and sends the notification for the PCs who suffered a new trauma after this action.
    Finally, calls resistance_roll_end.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: call to resistance_roll_end
    """
    context.chat_data["resistance_roll"]["message"].delete()

    placeholders = get_lang(context, resistance_roll_notes.__name__)
    description = update.message.text

    add_tag_in_telegram_data(context, location="chat", tags=["resistance_roll", "roll", "notes"], value=description)

    trauma_victim = controller.commit_resistance_roll(update.effective_message.chat_id,
                                                      get_user_id(update),
                                                      context.chat_data["resistance_roll"]["roll"])

    if trauma_victim:
        update.effective_message.reply_text(placeholders["0"].format(trauma_victim[0], trauma_victim[1]),
                                            parse_mode=ParseMode.HTML,
                                            quote=False)

    return resistance_roll_end(update, context)


def resistance_roll_end(update: Update, context: CallbackContext) -> int:
    """
    Ends the resistance_roll conversation and deletes all the saved information from the chat_data.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: ConversationHandler.END
    """
    if get_user_id(update) == context.chat_data["resistance_roll"]["invoker"]:
        delete_conv_from_telegram_data(context, "resistance_roll", "chat")

        return end_conv(update, context)


# ------------------------------------------conv_resistanceRoll---------------------------------------------------------


def add_stress(update: Update, context: CallbackContext) -> None:
    """
    Adds the given stress to the active pc of the user.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    """
    placeholders = get_lang(context, add_stress.__name__)

    if is_user_not_in_game(update, placeholders["err"]):
        return

    chat_id = update.effective_message.chat_id

    if "active_PCs" not in context.user_data or chat_id not in context.user_data["active_PCs"]:
        update.message.reply_text(placeholders["err2"], parse_mode=ParseMode.HTML)
        return

    try:
        stress = int(context.args[0])
    except (ValueError, IndexError, AttributeError):
        stress = 1

    pc_name = context.user_data["active_PCs"][update.effective_message.chat_id]
    trauma_victim = controller.add_stress_to_pc(update.effective_message.chat_id, get_user_id(update), pc_name, stress)

    auto_delete_message(update.message.reply_text(placeholders["0"].format(stress, pc_name),
                                                  parse_mode=ParseMode.HTML), 18)

    if trauma_victim:
        update.effective_message.reply_text(placeholders["1"].format(trauma_victim[0], trauma_victim[1]),
                                            parse_mode=ParseMode.HTML,
                                            quote=False)


# ------------------------------------------conv_addTrauma--------------------------------------------------------------


def add_trauma(update: Update, context: CallbackContext) -> int:
    """
    Checks if the user controls a PC in this chat and starts the conversation that handles the adding of a trauma.
    Adds the dict "add_trauma" in user_data and stores the ID of the invoker in it.
    Finally, sends the trauma request.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, add_trauma.__name__)

    if is_user_not_in_game(update, placeholders["err"]):
        return add_trauma_end(update, context)

    chat_id = update.effective_message.chat_id

    if "active_PCs" not in context.user_data or chat_id not in context.user_data["active_PCs"]:
        update.message.reply_text(placeholders["err2"], parse_mode=ParseMode.HTML)
        return add_trauma_end(update, context)

    pc_name = context.user_data["active_PCs"][chat_id]

    buttons = [trauma[0] for trauma in query_traumas(pc_class=controller.get_pc_type(chat_id,
                                                                                     get_user_id(update), pc_name))]
    message = update.message.reply_text(placeholders["0"], reply_markup=custom_kb(buttons))

    add_tag_in_telegram_data(context, ["add_trauma", "message"], message)
    add_tag_in_telegram_data(context, ["add_trauma", "invocation_message"], update.message)

    return 0


def add_trauma_name(update: Update, context: CallbackContext) -> int:
    """
    Calls the controller method add_trauma_to_pc with the given trauma and
    eventually sends the user a message if he reached the trauma limit, then calls add_trauma_end.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: call to add_trauma_end
    """
    placeholders = get_lang(context, add_trauma_name.__name__)
    context.user_data["add_trauma"]["message"].delete()

    pc_name = context.user_data["active_PCs"][update.effective_message.chat_id]
    is_dead = controller.add_trauma_to_pc(update.effective_message.chat_id,
                                          get_user_id(update), pc_name, update.message.text)

    if is_dead:
        auto_delete_message(context.user_data["add_trauma"]["invocation_message"].reply_text(
            placeholders["0"].format(pc_name), parse_mode=ParseMode.HTML))

    return add_trauma_end(update, context)


def add_trauma_end(update: Update, context: CallbackContext) -> int:
    """
    Ends the conversation when /cancel is received then deletes the information collected so far
    and exits the conversation.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: ConversationHandler.END.
    """
    delete_conv_from_telegram_data(context, "add_trauma")

    return end_conv(update, context)


# ------------------------------------------conv_addTrauma--------------------------------------------------------------


# ------------------------------------------conv_heat-------------------------------------------------------------------


def heat(update: Update, context: CallbackContext) -> int:
    """
    Checks if the user controls a PC in this chat and starts the conversation of the heat.
    Adds the dict "heat" in user_data and stores the ID of the invoker and his active PC in it.
    Finally, sends the request for the nature of the score.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, heat.__name__)

    if is_game_in_wrong_phase(update, context, placeholders["1"], 2):
        return heat_end(update, context)

    add_tag_in_telegram_data(context, ["heat", "invocation_message"], update.message)

    message = update.message.reply_text(placeholders["0"], reply_markup=custom_kb(
        placeholders["keyboard"], inline=True, split_row=2, callback_data=placeholders["callbacks"]))
    add_tag_in_telegram_data(context, ["heat", "message"], message)
    add_tag_in_telegram_data(context, ["heat", "info", "total_heat"], value=0)

    return 0


def heat_score_nature(update: Update, context: CallbackContext) -> int:
    """
    Stores the nature of the score chosen by the user in user_data, and asks the user for the target profile.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, heat_score_nature.__name__)

    query = update.callback_query
    query.answer()
    choice, heat_to_add = query.data

    add_tag_in_telegram_data(context, tags=["heat", "info", "score_nature"], value=choice)

    context.user_data["heat"]["info"]["total_heat"] += int(heat_to_add)

    context.user_data["heat"]["message"].delete()

    message = context.user_data["heat"]["invocation_message"].reply_text(placeholders["0"], reply_markup=custom_kb(
        placeholders["keyboard"], inline=True, split_row=1, callback_data=placeholders["callbacks"]))
    add_tag_in_telegram_data(context, ["heat", "message"], message)

    return 1


def heat_target_profile(update: Update, context: CallbackContext) -> int:
    """
    Stores the target's profile chosen by the user in the user_data, and asks the user for the turf hostility.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, heat_target_profile.__name__)

    query = update.callback_query
    query.answer()
    choice, heat_to_add = query.data

    add_tag_in_telegram_data(context, tags=["heat", "info", "famous_target"], value=bool(choice == "True"))
    context.user_data["heat"]["message"].delete()

    context.user_data["heat"]["info"]["total_heat"] += int(heat_to_add)

    message = context.user_data["heat"]["invocation_message"].reply_text(placeholders["0"], reply_markup=custom_kb(
        placeholders["keyboard"], inline=True, split_row=1, callback_data=placeholders["callbacks"]))
    add_tag_in_telegram_data(context, ["heat", "message"], message)

    return 2


def heat_turf_hostility(update: Update, context: CallbackContext) -> int:
    """
    Stores the turf hostility chosen by the user in user_data, and asks the user for the war situation.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, heat_turf_hostility.__name__)

    query = update.callback_query
    query.answer()
    choice, heat_to_add = query.data
    add_tag_in_telegram_data(context, tags=["heat", "info", "hostility"], value=bool(choice == "True"))
    context.user_data["heat"]["message"].delete()

    context.user_data["heat"]["info"]["total_heat"] += int(heat_to_add)

    message = context.user_data["heat"]["invocation_message"].reply_text(placeholders["0"], reply_markup=custom_kb(
        placeholders["keyboard"], inline=True, split_row=1, callback_data=placeholders["callbacks"]))
    add_tag_in_telegram_data(context, ["heat", "message"], message)

    return 3


def heat_war_situation(update: Update, context: CallbackContext) -> int:
    """
    Stores the war situation chosen by the user in user_data, and asks the user if some killing was involved.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, heat_war_situation.__name__)

    query = update.callback_query
    query.answer()
    choice, heat_to_add = query.data
    add_tag_in_telegram_data(context, tags=["heat", "info", "war"], value=bool(choice == "True"))
    context.user_data["heat"]["message"].delete()

    context.user_data["heat"]["info"]["total_heat"] += int(heat_to_add)

    message = context.user_data["heat"]["invocation_message"].reply_text(placeholders["0"], reply_markup=custom_kb(
        placeholders["keyboard"], inline=True, split_row=1, callback_data=placeholders["callbacks"]))
    add_tag_in_telegram_data(context, ["heat", "message"], message)

    return 4


def heat_killing(update: Update, context: CallbackContext) -> int:
    """
    Stores if some killing was involved in user_data, and asks the user if they want to change the total_heat.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    query = update.callback_query
    query.answer()
    choice, heat_to_add = query.data
    add_tag_in_telegram_data(context, tags=["heat", "info", "bodies"], value=bool(choice == "True"))
    context.user_data["heat"]["message"].delete()

    context.user_data["heat"]["info"]["total_heat"] += int(heat_to_add)

    bonus_dice_lang = get_lang(context, "bonus_dice")

    query_menu = context.user_data["heat"]["invocation_message"].reply_text(
        bonus_dice_lang["heat"].format(context.user_data["heat"]["info"]["total_heat"]),
        reply_markup=build_plus_minus_keyboard(
            [bonus_dice_lang["heat_button"].format(
                context.user_data["heat"]["info"]["total_heat"])],
            done_button=True,
            back_button=False),
        parse_mode=ParseMode.HTML)

    add_tag_in_telegram_data(context, ["heat", "query_menu"], query_menu)

    return 5


def heat_extra(update: Update, context: CallbackContext) -> int:
    """
    Stores the final heat amount in the user_data, calls the controller method to apply the heat
    and sends the notification for the wanted level of the crew.
    Finally, calls heat_end.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, heat_extra.__name__)

    query = update.callback_query
    query.answer()

    total_heat = context.user_data["heat"]["info"]["total_heat"]

    choice = query.data
    if "+" in choice or "-" in choice:
        tags = ["heat", "info", "total_heat"]
        total_heat += int(choice.split(" ")[2])
        add_tag_in_telegram_data(context, tags=tags, value=total_heat)

        update_bonus_dice_kb(context, tags, total_heat, location="user", message_tag="heat", button_tag="heat_button")

    elif choice == "DONE":
        wanted_level = controller.add_heat_to_crew(update.effective_message.chat_id, get_user_id(update),
                                                   context.user_data["heat"]["info"])
        auto_delete_message(context.user_data["heat"]["invocation_message"].reply_text(
            placeholders["0"].format(wanted_level), parse_mode=ParseMode.HTML), 18)
        return heat_end(update, context)

    else:
        bonus_dice_lang = get_lang(context, "bonus_dice")
        auto_delete_message(
            update.effective_message.reply_text(bonus_dice_lang["heat_description"], parse_mode=ParseMode.HTML),
            bonus_dice_lang["heat_description"])

    return 5


def heat_end(update: Update, context: CallbackContext) -> int:
    """
    Ends the heat conversation and deletes all the saved information from the user_data.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: ConversationHandler.END
    """
    delete_conv_from_telegram_data(context, "heat")

    return end_conv(update, context)


# ------------------------------------------conv_heat-------------------------------------------------------------------

# ------------------------------------------conv_endScore---------------------------------------------------------------

def end_score(update: Update, context: CallbackContext) -> int:
    """
    Checks if the is in the right phase, is a score exists, and starts the conversation of the conclusion of a score.
    Adds the dict "heat" in user_data and stores the ID of the invoker and his active PC in it.
    Finally, sends the request for the nature of the score.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, end_score.__name__)

    if is_game_in_wrong_phase(update, context, placeholders["1"], 3):
        return end_score_end(update, context)
    if not controller.exists_score(update.effective_message.chat_id, get_user_id(update)):
        auto_delete_message(update.effective_message.reply_text(placeholders["2"]), 18.0)
        return end_score_end(update, context)

    add_tag_in_telegram_data(context, ["end_score", "invocation_message"], update.message)

    message = update.message.reply_text(placeholders["0"], reply_markup=custom_kb(
        placeholders["keyboard"], split_row=1), parse_mode=ParseMode.HTML)
    add_tag_in_telegram_data(context, ["end_score", "message"], message)

    return 0


def end_score_outcome(update: Update, context: CallbackContext) -> int:
    """
    Stores the description of the score's outcome in the user_data and sends the score's final notes request.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    context.user_data["end_score"]["message"].delete()
    placeholders = get_lang(context, end_score_outcome.__name__)

    add_tag_in_telegram_data(context, tags=["end_score", "info", "outcome"],
                             value=update.message.text)

    message = context.user_data["end_score"]["invocation_message"].reply_text(placeholders["0"],
                                                                              parse_mode=ParseMode.HTML)
    add_tag_in_telegram_data(context, tags=["end_score", "message"], value=message)

    update.message.delete()

    return 1


def end_score_notes(update: Update, context: CallbackContext) -> int:
    """
    Stores the final notes of the score in the user_data, calls the controller to get how much rep the crew earned and
    sends the Rep InlineKeyboard.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    context.user_data["end_score"]["message"].delete()

    add_tag_in_telegram_data(context, tags=["end_score", "info", "notes"],
                             value=update.message.text)

    total_rep = controller.get_last_score_rep(update.effective_message.chat_id, get_user_id(update))

    add_tag_in_telegram_data(context, tags=["end_score", "info", "rep"],
                             value=total_rep)

    bonus_dice_lang = get_lang(context, "bonus_dice")

    query_menu = context.user_data["end_score"]["invocation_message"].reply_text(
        bonus_dice_lang["rep"].format(context.user_data["end_score"]["info"]["rep"]),
        reply_markup=build_plus_minus_keyboard(
            [bonus_dice_lang["rep_button"].format(
                context.user_data["end_score"]["info"]["rep"])],
            done_button=True,
            back_button=False),
        parse_mode=ParseMode.HTML)

    add_tag_in_telegram_data(context, ["end_score", "query_menu"], query_menu)

    update.message.delete()

    return 2


def end_score_rep(update: Update, context: CallbackContext) -> int:
    """
    Stores the final rep amount in the user_data, calls the controller method to add the rep to the crew
    and terminates the conversation.
    Finally, calls end_score_end.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: call to end_score_end().
    """
    placeholders = get_lang(context, end_score_rep.__name__)

    query = update.callback_query
    query.answer()

    total_rep = context.user_data["end_score"]["info"]["rep"]

    choice = query.data
    if "+" in choice or "-" in choice:
        tags = ["end_score", "info", "rep"]
        total_rep += int(choice.split(" ")[2])
        add_tag_in_telegram_data(context, tags=tags, value=total_rep)

        update_bonus_dice_kb(context, tags, total_rep, location="user", message_tag="rep", button_tag="rep_button")

    elif choice == "DONE":
        coin_to_spend = controller.end_score(update.effective_message.chat_id, get_user_id(update),
                                             context.user_data["end_score"]["info"])
        if coin_to_spend > 0:
            auto_delete_message(context.user_data["end_score"]["invocation_message"].reply_text(
                placeholders["0"].format(coin_to_spend), parse_mode=ParseMode.HTML), 18)
        return end_score_end(update, context)

    else:
        bonus_dice_lang = get_lang(context, "bonus_dice")
        auto_delete_message(
            update.effective_message.reply_text(bonus_dice_lang["rep_description"], parse_mode=ParseMode.HTML),
            bonus_dice_lang["rep_description"])

    return 2


def end_score_end(update: Update, context: CallbackContext) -> int:
    """
    Ends the heat conversation and deletes all the saved information from the user_data.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: ConversationHandler.END
    """
    delete_conv_from_telegram_data(context, "end_score")

    return end_conv(update, context)


# ------------------------------------------conv_endScore---------------------------------------------------------------


# ------------------------------------------conv_entanglement-----------------------------------------------------------


def entanglement(update: Update, context: CallbackContext) -> int:
    """
    Checks if the user is in a game and in the correct phase, then starts the conversation that handles the entanglement
    throws the amount of dice following the game's rules and asks the user the name for the entanglement.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, entanglement.__name__)

    if is_game_in_wrong_phase(update, context, placeholders["err"], 2):
        return entanglement_end(update, context)

    add_tag_in_telegram_data(context, ["entanglement", "invocation_message"], update.message)

    context.user_data["entanglement"].setdefault("info", {}).setdefault("secret", False)

    game_id = query_game_of_user(update.message.chat_id, get_user_id(update))

    heat_value = controller.get_crew_heat(game_id)
    wanted_level = controller.get_crew_wanted_level(game_id)

    url = helpers.create_deep_linked_url(context.bot.username)

    add_tag_in_telegram_data(context, ["entanglement", "chat_id"], update.message.chat_id)

    if update.message.chat.type != "private":
        auto_delete_message(update.effective_chat.send_message(
            placeholders["public"].format(query_users_names(get_user_id(update))[0], url),
            reply_to_message_id=update.message.message_id,
            parse_mode=ParseMode.HTML), 18)

    roll_dice(update, context, wanted_level, ["entanglement", "outcome"], "user", get_user_id(update))
    entanglement_placeholder = placeholders["6"]
    for key in placeholders:
        if str(heat_value) in key:
            entanglement_placeholder = placeholders[key]
    for key in entanglement_placeholder:
        if str(context.user_data["entanglement"]["outcome"]) in key:
            entanglement_placeholder = entanglement_placeholder[key]

    message = context.bot.send_message(chat_id=get_user_id(update), text=placeholders["private"],
                                       reply_markup=custom_kb([entanglement_placeholder]))

    add_tag_in_telegram_data(context, ["entanglement", "message"], message)

    return 0


def secret_entanglement(update: Update, context: CallbackContext) -> int:
    """
    Sets the secret tag in the entanglement info to True, then calls entanglement().

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    add_tag_in_telegram_data(context, ["entanglement", "info", "secret"], True)
    return entanglement(update, context)


def entanglement_name(update: Update, context: CallbackContext) -> int:
    """
    Stores the name of the entanglement in the user_data and advances the conversation to
    the next state that regards the entanglement's description.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: next conversation's state.
    """
    placeholders = get_lang(context, entanglement_name.__name__)

    context.user_data["entanglement"]["message"].delete()

    add_tag_in_telegram_data(context, ["entanglement", "info", "name"], update.message.text)

    message = context.bot.send_message(chat_id=get_user_id(update), text=placeholders["0"])
    add_tag_in_telegram_data(context, ["entanglement", "message"], message)

    update.message.delete()

    return 1


def entanglement_description(update: Update, context: CallbackContext) -> int:
    """
    Stores the description of the entanglement in the user_data and calls the controller method commit_entanglement,
    then calls entanglement_end.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, entanglement_description.__name__)

    context.user_data["entanglement"]["message"].delete()

    add_tag_in_telegram_data(context, ["entanglement", "info", "description"], update.message.text)

    chat_id = context.user_data["entanglement"]["chat_id"]

    user_name = query_users_names(get_user_id(update))[0]

    if context.user_data["entanglement"]["info"]["secret"]:
        context.bot.send_message(chat_id, placeholders["secret"].format(user_name), ParseMode.HTML)
    else:
        context.bot.send_message(chat_id, placeholders["public"].format(user_name, update.message.text), ParseMode.HTML)

    controller.commit_entanglement(
        query_game_of_user(chat_id, get_user_id(update)), context.user_data["entanglement"]["info"])

    return entanglement_end(update, context)


def entanglement_end(update: Update, context: CallbackContext) -> int:
    """
    Ends the entanglement conversation and deletes all the saved information from the user_data.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: ConversationHandler.END
    """
    delete_conv_from_telegram_data(context, "entanglement")

    return end_conv(update, context)


# ------------------------------------------conv_entanglement-----------------------------------------------------------


# ------------------------------------------conv_payoff-----------------------------------------------------------------


def payoff(update: Update, context: CallbackContext) -> int:
    """
    Checks if the user is in a game and in the correct phase, then starts the conversation that handles the payoff,
    and asks the user the amount of coin earned.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, payoff.__name__)

    if is_game_in_wrong_phase(update, context, placeholders["err"], 2):
        return entanglement_end(update, context)

    add_tag_in_telegram_data(context, ["payoff", "invocation_message"], update.message)

    message = update.message.reply_text(placeholders["0"], reply_markup=custom_kb(placeholders["keyboard"]))
    add_tag_in_telegram_data(context, ["payoff", "message"], message)

    return 0


def payoff_amount(update: Update, context: CallbackContext) -> int:
    """
    Stores the amount of coin in the user_data and advances the conversation to the
    next state that regards how to store the earnings sending the user an inline keyboard with the available options.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: next conversation's state.
    """
    placeholders = get_lang(context, payoff_amount.__name__)
    context.user_data["payoff"]["message"].delete()

    coins = update.message.text
    try:
        coins = int(coins)
    except:
        placeholders = get_lang(context, payoff.__name__)
        message = context.user_data["payoff"]["invocation_message"].reply_text(
            placeholders["0"], reply_markup=custom_kb(placeholders["keyboard"]))
        add_tag_in_telegram_data(context, ["payoff", "message"], message)
        return 0

    add_tag_in_telegram_data(context, ["payoff", "info", "amount"], coins)

    can_divvy, can_store_in_vault = \
        controller.can_store_coins(query_game_of_user(update.message.chat_id, get_user_id(update)), coins)

    buttons = placeholders["keyboard"].copy()
    callbacks = placeholders["callbacks"].copy()

    if not can_store_in_vault:
        buttons.pop(1)
        callbacks.pop(1)
    if not can_divvy:
        buttons.pop(0)
        callbacks.pop(0)

    message = context.user_data["payoff"]["invocation_message"].reply_text(
        placeholders["0"], reply_markup=custom_kb(buttons, inline=True, split_row=1, callback_data=callbacks))
    add_tag_in_telegram_data(context, ["payoff", "message"], message)

    update.message.delete()
    return 1


def payoff_choice(update: Update, context: CallbackContext) -> int:
    """
    Stores the handling method for the coins in the user_data and advances the conversation to the
    next state that regards the payoff notes.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: next conversation's state.
    """
    placeholders = get_lang(context, payoff_choice.__name__)
    context.user_data["payoff"]["message"].delete()

    query = update.callback_query
    query.answer()

    choice = query.data

    # Divvy
    if choice == 1:
        add_tag_in_telegram_data(context, ["payoff", "info", "distributed"], True)
    # Vault
    elif choice == 2:
        add_tag_in_telegram_data(context, ["payoff", "info", "distributed"], False)
    # Do it later
    else:
        auto_delete_message(context.user_data["payoff"]["invocation_message"].reply_text(
            placeholders["0"].format(context.user_data["payoff"]["info"]["amount"])), 15)

    message = context.user_data["payoff"]["invocation_message"].reply_text(placeholders["1"])
    add_tag_in_telegram_data(context, ["payoff", "message"], message)
    return 2


def payoff_notes(update: Update, context: CallbackContext) -> int:
    """
    Stores the notes in the user_data and calls the controller method commit_payoff, then
    calls payoff_end.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: payoff_end.
    """
    context.user_data["payoff"]["message"].delete()

    add_tag_in_telegram_data(context, ["payoff", "info", "notes"], update.message.text)

    controller.commit_payoff(query_game_of_user(update.message.chat_id, get_user_id(update)),
                             context.user_data["payoff"]["info"])

    return payoff_end(update, context)


def payoff_end(update: Update, context: CallbackContext) -> int:
    """
    Ends the payoff conversation and deletes all the saved information from the user_data.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: ConversationHandler.END
    """
    delete_conv_from_telegram_data(context, "payoff")

    return end_conv(update, context)


# ------------------------------------------conv_payoff-----------------------------------------------------------------


# ------------------------------------------conv_armor_use--------------------------------------------------------------


def armor_use(update: Update, context: CallbackContext) -> int:
    """
    Checks if the user is in a game and in the correct phase, then starts the conversation that handles the armor use
    and asks the user for the type of armor.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    if "active_PCs" in context.user_data and update.effective_message.chat_id in context.user_data["active_PCs"]:
        placeholders = get_lang(context, armor_use.__name__)

        if is_game_in_wrong_phase(update, context, placeholders["1"]):
            return end_score_end(update, context)

        add_tag_in_telegram_data(context, ["armor_use", "invocation_message"], update.message)

        add_tag_in_telegram_data(context, ["armor_use", "info", "pc"],
                                 context.user_data["active_PCs"][update.effective_message.chat_id])

        message = update.message.reply_text(placeholders["0"], reply_markup=custom_kb(
            placeholders["keyboard"], inline=True, split_row=1))
        add_tag_in_telegram_data(context, ["armor_use", "message"], message)

        return 0


def armor_use_type(update: Update, context: CallbackContext) -> int:
    """
    Stores the type of the armor in the user_data and asks the user for the description of the armor usage.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, armor_use_type.__name__)

    query = update.callback_query
    query.answer()
    choice = query.data

    context.user_data["armor_use"]["message"].delete()

    add_tag_in_telegram_data(context, ["armor_use", "info", "armor_type"], choice)

    message = context.user_data["armor_use"]["invocation_message"].reply_text(placeholders["0"])
    add_tag_in_telegram_data(context, ["armor_use", "message"], message)

    return 1


def armor_use_description(update: Update, context: CallbackContext) -> int:
    """
    Stores the description of the armor usage and calls the controller method commit_armor_use,
    then calls armor_use_end.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, armor_use_description.__name__)

    add_tag_in_telegram_data(context, ["armor_use", "info", "notes"], update.message.text)

    context.user_data["armor_use"]["message"].delete()

    message = context.user_data["armor_use"]["invocation_message"].reply_text(placeholders["0"].format(
        context.user_data["armor_use"]["info"]["pc"], context.user_data["armor_use"]["info"]["armor_type"]
    ), parse_mode=ParseMode.HTML)
    auto_delete_message(message, 8.0)

    controller.commit_armor_use(update.effective_message.chat_id, get_user_id(update),
                                context.user_data["armor_use"]["info"])

    return armor_use_end(update, context)


def armor_use_end(update: Update, context: CallbackContext) -> int:
    """
    Ends the armor use conversation and deletes all the saved information from the user_data.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: ConversationHandler.END
    """
    delete_conv_from_telegram_data(context, "armor_use")

    return end_conv(update, context)


# ------------------------------------------conv_armor_use--------------------------------------------------------------

# ------------------------------------------conv_vault_capacity---------------------------------------------------------

def vault_capacity(update: Update, context: CallbackContext) -> int:
    """
    Starts the conversation that regards the vault's capacity.
    Sends the InlineKeyboard with the current capacity of the vault.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.:
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, vault_capacity.__name__)

    if is_game_in_wrong_phase(update, context, placeholders["err"]):
        return vault_capacity_end(update, context)

    add_tag_in_telegram_data(context, ["vault_capacity", "invocation_message"], update.message)

    add_tag_in_telegram_data(context, ["vault_capacity", "capacity"],
                             controller.get_vault_capacity_of_crew(
                                 query_game_of_user(update.effective_message.chat_id, get_user_id(update))))

    placeholders = get_lang(context, "bonus_dice")
    query_menu = update.message.reply_text(placeholders["vault_capacity_message"],
                                           reply_markup=build_plus_minus_keyboard(
                                               [placeholders["vault_capacity_button"].format(
                                                   context.user_data["vault_capacity"]["capacity"])],
                                               inline=True,
                                               back_button=False,
                                               done_button=True))
    add_tag_in_telegram_data(context, ["vault_capacity", "query_menu"], query_menu)

    return 0


def vault_capacity_kb(update: Update, context: CallbackContext) -> int:
    """
    Handles the selection of the buttons from the inline keyboard of the vault capacity.
    Calls the controller method modify_vault_capacity() when DONE button is pressed.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.:
    :return: this state if the DONE button has not been pressed, vault_capacity_end() otherwise.
    """

    placeholders = get_lang(context, "bonus_dice")

    query = update.callback_query
    query.answer()
    choice = query.data

    capacity = context.user_data["vault_capacity"]["capacity"]

    if "+" in choice or "-" in choice:
        capacity += int(choice.split(" ")[1])
        if capacity < 0:
            capacity = 0
        add_tag_in_telegram_data(context, ["vault_capacity", "capacity"], value=capacity)

        update_bonus_dice_kb(context, location="user", tags=["vault_capacity", "capacity"],
                             tot_dice=context.user_data["vault_capacity"]["capacity"],
                             message_tag="vault_capacity_message",
                             button_tag="vault_capacity_button")

    elif choice == "DONE":
        controller.modify_vault_capacity(query_game_of_user(update.effective_message.chat_id, get_user_id(update)),
                                         context.user_data["vault_capacity"]["capacity"])
        return vault_capacity_end(update, context)

    else:
        auto_delete_message(
            update.effective_message.reply_text(placeholders["vault_capacity_rules"], parse_mode=ParseMode.HTML),
            placeholders["vault_capacity_rules"])

    return 0


def vault_capacity_end(update: Update, context: CallbackContext) -> int:
    """
    Ends the vault capacity conversation and deletes all the saved information from the user_data.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: ConversationHandler.END
    """
    delete_conv_from_telegram_data(context, "vault_capacity")

    return end_conv(update, context)


# ------------------------------------------conv_vault_capacity---------------------------------------------------------

# ------------------------------------------conv_add_coin---------------------------------------------------------------


def add_coin(update: Update, context: CallbackContext) -> int:
    """
    Checks if the user is in a game and in the correct phase, then starts the conversation that handles the coins
    and sends the user the inline keyboard.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """

    placeholders = get_lang(context, add_coin.__name__)

    if is_game_in_wrong_phase(update, context, placeholders["err"]):
        return add_coin_end(update, context)

    add_tag_in_telegram_data(context, ["add_coin", "invocation_message"], update.message)

    add_tag_in_telegram_data(context, ["add_coin", "info", "coins"], 0)
    add_tag_in_telegram_data(context, ["add_coin", "info", "stash"], 0)
    add_tag_in_telegram_data(context, ["add_coin", "info", "vault"], 0)

    query_menu = update.message.reply_text(placeholders["0"],
                                           reply_markup=build_plus_minus_keyboard(
                                               build_add_coin_buttons(update, context),
                                               back_button=False, done_button=True))

    add_tag_in_telegram_data(context, ["add_coin", "query_menu"], query_menu)

    return 0


def build_add_coin_buttons(update: Update, context: CallbackContext) -> List[str]:
    """
    Builds the button for the inline keyboard used to add coins.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the list of buttons' label.
    """
    chat_id = update.effective_message.chat_id
    try:
        pc_name = context.user_data["active_PCs"][chat_id]
    except:
        pc_name = None
    coins, stash, vault = controller.get_player_coins(chat_id, get_user_id(update), pc_name)

    buttons = []
    if coins is not None and stash is not None:
        coins += context.user_data["add_coin"]["info"]["coins"]
        stash += context.user_data["add_coin"]["info"]["stash"]
        buttons.append("Coins: {}".format(coins))
        buttons.append("Stash: {}".format(stash))
    vault += context.user_data["add_coin"]["info"]["vault"]
    buttons.append("Vault: {}".format(vault))

    return buttons


def add_coin_amount(update: Update, context: CallbackContext) -> int:
    """
    Handles the selection of the buttons from the inline keyboard of the coins.
    Calls the controller method commit_add_coin() when DONE button is pressed.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.:
    :return: this state if the DONE button has not been pressed, add_coin_end otherwise.
    """

    placeholders = get_lang(context, add_coin_amount.__name__)

    query = update.callback_query
    query.answer()
    choice = query.data

    add_coin_info = context.user_data["add_coin"]["info"]
    chat_id = update.effective_message.chat_id
    try:
        pc_name = context.user_data["active_PCs"][chat_id]
    except:
        pc_name = None
    if "+" in choice or "-" in choice:

        choice = choice.split(" ")

        if controller.check_add_coin(chat_id, get_user_id(update), pc_name, choice[0].lower(), int(choice[1]) +
                                                                                               context.user_data[
                                                                                                   "add_coin"]["info"][
                                                                                                   choice[0].lower()]):

            add_coin_info[choice[0].lower()] += int(choice[1])
        else:
            auto_delete_message(context.user_data["add_coin"]["invocation_message"].reply_text(
                placeholders["0"]))

        placeholders = get_lang(context, add_coin.__name__)
        context.user_data["add_coin"]["query_menu"].edit_text(placeholders["0"],
                                                              reply_markup=build_plus_minus_keyboard(
                                                                  build_add_coin_buttons(update, context),
                                                                  back_button=False,
                                                                  done_button=True))
        return 0
    elif choice == "DONE":
        controller.commit_add_coin(chat_id, get_user_id(update), pc_name, add_coin_info)
        return add_coin_end(update, context)
    else:
        if choice.split(": ")[0].lower() == "vault":
            auto_delete_message(context.user_data["add_coin"]["invocation_message"].reply_text(
                placeholders["vault"].format(
                    controller.get_vault_capacity_of_crew(query_game_of_user(chat_id, get_user_id(update))))), 3)
        else:
            auto_delete_message(context.user_data["add_coin"]["invocation_message"].reply_text(
                placeholders[choice.split(": ")[0].lower()]), 3)
        return 0


def add_coin_end(update: Update, context: CallbackContext) -> int:
    """
    Ends the armor use conversation and deletes all the saved information from the user_data.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: ConversationHandler.END
    """
    delete_conv_from_telegram_data(context, "add_coin")

    return end_conv(update, context)


# ------------------------------------------conv_add_coin---------------------------------------------------------------


def upgrade_crew(update: Update, context: CallbackContext) -> None:
    """
    Handles the upgrade of the crew, increasing its tier or changing its hold.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    """
    placeholders = get_lang(context, upgrade_crew.__name__)

    if is_game_in_wrong_phase(update, context, placeholders["err"]):
        return

    hold, tier = controller.upgrade_crew(query_game_of_user(update.message.chat_id, get_user_id(update)))

    auto_delete_message(update.message.reply_text(placeholders[str(hold)].format(tier), parse_mode=ParseMode.HTML))


# ------------------------------------------conv_factions_status--------------------------------------------------------

def factions_status(update: Update, context: CallbackContext) -> int:
    """
    Starts the conversation that regards the factions' status.
    Sends the InlineKeyboard with the factions and their current status.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.:
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, factions_status.__name__)

    if is_user_not_in_game(update, placeholders["err"]):
        return factions_status_end(update, context)

    add_tag_in_telegram_data(context, ["factions_status", "invocation_message"], update.message)

    factions = controller.get_factions(query_game_of_user(update.effective_message.chat_id, get_user_id(update)))

    buttons_list = []
    buttons = []
    for i in range(len(factions)):
        buttons.append(factions[i])
        if (i + 1) % 8 == 0:
            buttons_list.append(buttons.copy())
            buttons.clear()
    if buttons:
        buttons_list.append(buttons.copy())
    add_tag_in_telegram_data(context, tags=["factions_status", "buttons_list"], value=buttons_list)
    add_tag_in_telegram_data(context, tags=["factions_status", "query_menu_index"], value=0)

    context.user_data["factions_status"]["query_menu"] = context.user_data["factions_status"][
        "invocation_message"].reply_text(
        placeholders["0"],
        parse_mode=ParseMode.HTML,
        reply_markup=build_multi_page_kb(buttons_list[0], done_button=True))

    return 0


def factions_status_selection(update: Update, context: CallbackContext) -> int:
    """
    Handles the selection of the buttons from the inline keyboard of the factions status.
    Sends the InlineKeyboard to select the status of the selected faction.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.:
    :return: this state if the DONE button has not been pressed, faction_status_update() otherwise.
    """

    placeholders = get_lang(context, factions_status_selection.__name__)

    query = update.callback_query
    query.answer()

    choice = query.data
    index = context.user_data["factions_status"]["query_menu_index"]

    if choice == "RIGHT":
        index += 1
        if index > len(context.user_data["factions_status"]["buttons_list"]):
            index = 0
        context.user_data["factions_status"]["query_menu_index"] = index

    elif choice == "LEFT":
        index -= 1
        if index == -len(context.user_data["factions_status"]["buttons_list"]):
            index = 0

        context.user_data["factions_status"]["query_menu_index"] = index
    elif choice == "DONE":
        context.user_data["factions_status"]["query_menu"].delete()
        controller.update_factions_status(query_game_of_user(update.effective_message.chat_id, get_user_id(update)),
                                          context.user_data["factions_status"]["factions"])

        return factions_status_end(update, context)
    else:
        status = int(choice.split(" ")[0])
        name = choice.split("$")[0]
        name = name.split(" - ")[1]
        name = name.split(":")[0]
        if "$" in choice:
            add_tag_in_telegram_data(context, tags=["factions_status", "focus"],
                                     value=name)
            add_tag_in_telegram_data(context, tags=["factions_status", "factions", name],
                                     value=status)
            placeholders = get_lang(context, "bonus_dice")
            message = context.user_data["factions_status"]["invocation_message"].reply_text(
                text=placeholders["factions_status_message"].format(name),
                parse_mode=ParseMode.HTML,
                reply_markup=build_plus_minus_keyboard(
                    [placeholders["factions_status_button"].format(status)], back_button=False, done_button=True))

            context.user_data["factions_status"]["query_menu"].delete()
            add_tag_in_telegram_data(context, tags=["factions_status", "query_menu"], value=message)
            return 1
        else:
            description = query_factions(name=name, as_dict=True)[0]["description"]

            if description is None or description == "":
                description = placeholders["404"]
            auto_delete_message(update.effective_message.reply_text(
                text=description, quote=False), description)
            return 0

    context.user_data["factions_status"]["query_menu"].edit_text(
        placeholders["0"], reply_markup=build_multi_page_kb(
            context.user_data["factions_status"]["buttons_list"][
                context.user_data["factions_status"]["query_menu_index"]], done_button=True))
    return 0


def factions_status_update(update: Update, context: CallbackContext) -> int:
    """
    Handles the selection of the new status of the selected. faction. The value is stored in the user_data.
    When the selection is finished the InlineKeyboard with all the factions is sent again.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.:
    :return: this state if the DONE button has not been pressed, factions_status_selection() otherwise.
    """
    placeholders = get_lang(context, "bonus_dice")

    query = update.callback_query
    query.answer()
    choice = query.data

    focus = context.user_data["factions_status"]["focus"]
    status = context.user_data["factions_status"]["factions"][focus]

    if "+" in choice or "-" in choice:
        status += int(choice.split(" ")[1])
        if status < -3:
            status = -3
        if status > 3:
            status = 3
        add_tag_in_telegram_data(context, ["factions_status", "factions", focus], value=status)

        update_bonus_dice_kb(context, location="user", tags=["factions_status", "factions", focus],
                             tot_dice=context.user_data["factions_status"]["factions"][focus],
                             message_tag="factions_status_message",
                             button_tag="factions_status_button")

    elif choice == "DONE":
        placeholders = get_lang(context, factions_status_update.__name__)
        context.user_data["factions_status"]["query_menu"].delete()
        context.user_data["factions_status"]["query_menu"] = context.user_data["factions_status"][
            "invocation_message"].reply_text(
            placeholders["0"],
            parse_mode=ParseMode.HTML,
            reply_markup=build_multi_page_kb(
                context.user_data["factions_status"]["buttons_list"][
                    context.user_data["factions_status"]["query_menu_index"]], done_button=True))

        return 0

    else:
        auto_delete_message(
            update.effective_message.reply_text(placeholders["factions_status_description"], parse_mode=ParseMode.HTML),
            placeholders["factions_status_description"])

    return 1


def factions_status_end(update: Update, context: CallbackContext) -> int:
    """
    Ends the factions' status conversation and deletes all the saved information from the user_data.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: ConversationHandler.END
    """
    delete_conv_from_telegram_data(context, "faction_status")

    return end_conv(update, context)


# ------------------------------------------conv_factions_status--------------------------------------------------------


# ------------------------------------------conv_use_item---------------------------------------------------------------


def use_item(update: Update, context: CallbackContext) -> int:
    """
    Checks if the user is in a game, in the correct phase and has active PCs, then starts the conversation that handles
    the use of an ite, and asks the user for what item they want to use.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    if "active_PCs" in context.user_data and update.effective_message.chat_id in context.user_data["active_PCs"]:
        placeholders = get_lang(context, use_item.__name__)

        if is_game_in_wrong_phase(update, context, placeholders["1"], 3):
            return end_score_end(update, context)

        add_tag_in_telegram_data(context, ["use_item", "invocation_message"], update.message)

        chat_id = update.effective_message.chat_id
        user_id = get_user_id(update)

        add_tag_in_telegram_data(context, ["use_item", "info", "pc"], context.user_data["active_PCs"][chat_id])
        items = controller.get_items_names(query_game_of_user(chat_id, user_id),
                                           controller.get_pc_class(chat_id,
                                                                   user_id,
                                                                   context.user_data["use_item"]["info"]["pc"]))
        items = [item[0] for item in items]

        buttons_list = []
        buttons = []
        for i in range(len(items)):
            buttons.append(items[i])
            if (i + 1) % 8 == 0:
                buttons_list.append(buttons.copy())
                buttons.clear()
        if buttons:
            buttons_list.append(buttons.copy())
        add_tag_in_telegram_data(context, ["use_item", "buttons_list"], buttons_list)

        context.user_data["use_item"]["query_menu"] = update.message.reply_text(
            placeholders["0"],
            parse_mode=ParseMode.HTML,
            reply_markup=build_multi_page_kb(buttons_list[0])
        )

        add_tag_in_telegram_data(context, ["use_item", "query_menu_index"], 0)

        return 0


def use_item_name(update: Update, context: CallbackContext) -> int:
    """
    Stores the name of the item in the user data, calls the controller method use_item and, if it returns true,
    asks them the description of the usage; if it returns false calls use_item_end.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, use_item_name.__name__)

    query = update.callback_query
    query.answer()
    choice = query.data
    index = context.user_data["use_item"]["query_menu_index"]

    if choice == "RIGHT":
        index += 1
        if index > len(context.user_data["use_item"]["buttons_list"]):
            index = 0
        context.user_data["use_item"]["query_menu_index"] = index

    elif choice == "LEFT":
        index -= 1
        if index == -len(context.user_data["use_item"]["buttons_list"]):
            index = 0
        context.user_data["use_item"]["query_menu_index"] = index

    else:
        item_name = choice.split("$")[0]
        if "$" in choice:
            add_tag_in_telegram_data(context, ["use_item", "info", "item_name"], item_name)
            result = controller.use_item(update.effective_message.chat_id,
                                         get_user_id(update),
                                         context.user_data["use_item"]["info"])
            if result:
                message = context.user_data["use_item"]["invocation_message"].reply_text(placeholders["1"].format(
                    context.user_data["use_item"]["info"]["item_name"]), parse_mode=ParseMode.HTML)
                add_tag_in_telegram_data(context, ["use_item", "message"], message)
                return 1
            else:
                message = context.user_data["use_item"]["invocation_message"].reply_text(placeholders["2"])
                auto_delete_message(message, 10)
                return use_item_end(update, context)
        else:
            name = item_name.split(": ")[0]
            description, weight, usages, quality = controller.get_item_description(
                update.effective_message.chat_id, get_user_id(update), name,
                context.user_data["use_item"]["info"]["pc"])
            info = placeholders["3"].format(description, weight, usages, quality)
            auto_delete_message(update.effective_message.reply_text(text=info, quote=False), info)
            return 0

    context.user_data["use_item"]["query_menu"].edit_text(
        placeholders["0"],
        reply_markup=build_multi_page_kb(
            context.user_data["use_item"]["buttons_list"][context.user_data["use_item"]["query_menu_index"]]))
    return 0


def use_item_description(update: Update, context: CallbackContext) -> int:
    """
    Stores the description of the item in the user data and calls the controller method commit_use_item then calls
    use_item_end.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, use_item_description.__name__)

    add_tag_in_telegram_data(context, ["use_item", "info", "notes"], update.message.text)
    context.user_data["use_item"]["message"].delete()

    chat_id = update.effective_message.chat_id
    user_id = get_user_id(update)
    controller.commit_use_item(query_game_of_user(chat_id, user_id), user_id, context.user_data["use_item"]["info"])

    auto_delete_message(placeholders["0"], 8)

    return use_item_end(update, context)


def use_item_end(update: Update, context: CallbackContext) -> int:
    """
    Ends the use item conversation and deletes all the saved information from the user_data.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: ConversationHandler.END
    """
    delete_conv_from_telegram_data(context, "use_item")

    return end_conv(update, context)


# ------------------------------------------conv_use_item---------------------------------------------------------------


# ------------------------------------------conv_add_action_dots--------------------------------------------------------


def add_action_dots(update: Update, context: CallbackContext) -> int:
    placeholders = get_lang(context, add_action_dots.__name__)
    if "active_PCs" in context.user_data and update.effective_message.chat_id in context.user_data["active_PCs"]:
        chat_id = update.effective_message.chat_id

        add_tag_in_telegram_data(context, ["add_action_dots", "invocation_message"], update.message)

        current_action_dots = controller.get_pc_actions_ratings(get_user_id(update), chat_id,
                                                                context.user_data["active_PCs"][chat_id])
        action_dots = {}
        for elem in current_action_dots:
            action_dots[elem[0].capitalize()] = elem[1]

        add_tag_in_telegram_data(context, tags=["add_action_dots", "action_dots"], value=action_dots)
        add_tag_in_telegram_data(context, tags=["add_action_dots", "points"], value=controller.get_pc_points(
            chat_id, get_user_id(update), context.user_data["active_PCs"][chat_id]))

        buttons = query_attributes(only_names=True)
        buttons.append("DONE")
        query_menu = context.user_data["add_action_dots"]["invocation_message"].reply_text(
            text=placeholders["0"],
            reply_markup=custom_kb(buttons, inline=True, split_row=3))
        add_tag_in_telegram_data(context, tags=["add_action_dots", "query_menu"], value=query_menu)
        return 0

    update.effective_message.reply_text(placeholders["err"])


def add_action_dots_attribute_selection(update: Update, context: CallbackContext) -> int:
    placeholders = get_lang(context, add_action_dots_attribute_selection.__name__)
    chat_id = update.effective_message.chat_id
    pc = context.user_data["active_PCs"][chat_id]

    query = update.callback_query
    query.answer()

    choice = query.data
    if choice == "DONE":
        controller.add_action_dots(chat_id, get_user_id(update), pc,
                                   context.user_data["add_action_dots"]["action_dots"],
                                   context.user_data["add_action_dots"]["points"])

        return add_action_dots_end(update, context)

    add_tag_in_telegram_data(context, tags=["add_action_dots", "selected_attribute"], value=choice)

    buttons = create_central_buttons_action_dots(context.user_data["add_action_dots"]["action_dots"], choice)

    context.user_data["add_action_dots"]["query_menu"].delete()
    query_menu = context.user_data["add_action_dots"]["invocation_message"].reply_text(
        text=placeholders["0"].format(context.user_data["add_action_dots"]["points"][choice]),
        reply_markup=build_plus_minus_keyboard(buttons))
    add_tag_in_telegram_data(context, tags=["add_action_dots", "query_menu"], value=query_menu)
    return 1


def add_action_dots_keyboard(update: Update, context: CallbackContext) -> int:
    placeholders = get_lang(context, add_action_dots_keyboard.__name__)

    query = update.callback_query
    query.answer()

    action_dots = context.user_data["add_action_dots"]["action_dots"]

    choice = query.data
    if "+" in choice or "-" in choice:
        attribute = context.user_data["add_action_dots"]["selected_attribute"]

        choice = choice.split(" ")
        context.user_data["add_action_dots"]["points"][attribute] -= int(choice[1])
        if context.user_data["add_action_dots"]["points"][attribute] < 0:
            context.user_data["add_action_dots"]["points"][attribute] = 0
            return 1

        action_dots[choice[0]] += int(choice[1])

        if action_dots[choice[0]] < 0:
            context.user_data["add_action_dots"]["points"][attribute] -= 1
            action_dots[choice[0]] = 0
        elif action_dots[choice[0]] > 4:
            context.user_data["add_action_dots"]["points"][attribute] += 1
            action_dots[choice[0]] = 4

        buttons = create_central_buttons_action_dots(action_dots, attribute)

        context.user_data["add_action_dots"]["query_menu"].edit_text(text=placeholders["0"].format(
            context.user_data["add_action_dots"]["points"][attribute]),
            reply_markup=build_plus_minus_keyboard(buttons))

        return 1
    elif choice == "BACK":
        context.user_data["add_action_dots"]["query_menu"].delete()
        buttons = query_attributes(only_names=True)
        buttons.append("DONE")
        query_menu = context.user_data["add_action_dots"]["invocation_message"].reply_text(
            text=placeholders["1"],
            reply_markup=custom_kb(buttons, inline=True, split_row=3))
        add_tag_in_telegram_data(context, tags=["add_action_dots", "query_menu"], value=query_menu)

        return 0

    else:

        description = query_actions(choice)[0][1]
        auto_delete_message(context.bot.sendMessage(chat_id=get_user_id(update),
                                                    text=description,
                                                    ), description)
        return 1


def add_action_dots_end(update: Update, context: CallbackContext) -> int:
    """
    Ends the fortune roll conversation and deletes all the saved information from the user_data.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: ConversationHandler.END
    """
    delete_conv_from_telegram_data(context, "add_action_dots")

    return end_conv(update, context)


# ------------------------------------------conv_add_action_dots--------------------------------------------------------


# ------------------------------------------conv_fortune_roll-----------------------------------------------------------


def fortune_roll(update: Update, context: CallbackContext) -> int:
    """
    Checks if the user in the correct game phase then starts the conversation of the fortune roll.
    Adds the dict "fortune_roll" in user_data .
    Finally, sends the goal request.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, fortune_roll.__name__)

    if is_game_in_wrong_phase(update, context, placeholders["err"]):
        return fortune_roll_end(update, context)

    add_tag_in_telegram_data(context, ["fortune_roll", "invocation_message"], update.message)

    message = update.message.reply_text(placeholders["0"])
    add_tag_in_telegram_data(context, ["fortune_roll", "message"], message)

    return 0


def fortune_roll_goal(update: Update, context: CallbackContext) -> int:
    """
    Stores goal of the fortune roll in the user data, then sends the inline keyboard to select
    which type of fortune roll perform.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """

    placeholders = get_lang(context, fortune_roll_goal.__name__)
    context.user_data["fortune_roll"]["message"].delete()

    add_tag_in_telegram_data(context, ["fortune_roll", "roll", "goal"], update.message.text)

    chat_id = update.message.chat_id

    keyboard = placeholders["keyboard"].copy()
    callbacks = placeholders["callbacks"].copy()

    if not controller.get_cohorts_of_crew(chat_id, get_user_id(update)):
        keyboard.pop(2)
        callbacks.pop(2)

    if ("active_PCs" in context.user_data and chat_id not in context.user_data["active_PCs"]) or \
            ("active_PCs" not in context.user_data):
        keyboard.pop(1)
        keyboard.pop(0)
        callbacks.pop(1)
        callbacks.pop(0)

    message = context.user_data["fortune_roll"]["invocation_message"].reply_text(
        placeholders["0"], ParseMode.HTML, reply_markup=custom_kb(keyboard, True, 2, callbacks))

    add_tag_in_telegram_data(context, ["fortune_roll", "message"], message)

    update.message.delete()
    return 1


def fortune_roll_choice(update: Update, context: CallbackContext) -> int:
    """
    Advances the conversation to the next state based on the type of fortune role chosen.
    Eventually stores the info in the user_data or sends the next inline keyboard.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, fortune_roll_choice.__name__)
    context.user_data["fortune_roll"]["message"].delete()

    add_tag_in_telegram_data(context, ["fortune_roll", "bonus_dice"], 0)

    query = update.callback_query
    query.answer()
    choice = query.data

    chat_id = update.effective_message.chat_id
    try:
        pc_name = context.user_data["active_PCs"][chat_id]
    except:
        pc_name = None

    # Action
    if choice == 1:
        message = context.user_data["fortune_roll"]["invocation_message"].reply_text(placeholders["0"], ParseMode.HTML,
                                                                                     reply_markup=custom_kb(
                                                                                         query_attributes(True), True))

        add_tag_in_telegram_data(context, ["fortune_roll", "message"], message)
        return 10

    # Attribute
    elif choice == 2:
        keyboard: List[str] = ["{}: {}".format(attr[0], attr[1]) for attr in controller.get_pc_attribute_rating(
            chat_id, get_user_id(update), pc_name)]
        lifestyle = controller.get_pc_lifestyle(chat_id, get_user_id(update), pc_name)
        if lifestyle is not None:
            keyboard.append("Lifestyle: {}".format(lifestyle))
        message = context.user_data["fortune_roll"]["invocation_message"].reply_text(placeholders["1"], ParseMode.HTML,
                                                                                     reply_markup=custom_kb(
                                                                                         keyboard, True, 1))

        add_tag_in_telegram_data(context, ["fortune_roll", "message"], message)
        return 2

    # Cohort quality:
    elif choice == 3:
        cohorts = controller.get_cohorts_of_crew(chat_id, get_user_id(update))
        cohorts = ["{}: {}".format(cohort[0], cohort[1]) for cohort in cohorts]

        message = context.user_data["fortune_roll"]["invocation_message"].reply_text(placeholders["4"], ParseMode.HTML,
                                                                                     reply_markup=custom_kb(
                                                                                         cohorts, True, 1))

        add_tag_in_telegram_data(context, ["fortune_roll", "message"], message)

        return 2

    # Item quality
    elif choice == 4:
        items = controller.get_items_names(query_game_of_user(chat_id, get_user_id(update)),
                                           controller.get_pc_class(chat_id, get_user_id(update), pc_name))

        items = ["{}: {}".format(item[0], item[1]) for item in items]

        buttons_list = []
        buttons = []
        for i in range(len(items)):
            buttons.append(items[i])
            if (i + 1) % 8 == 0:
                buttons_list.append(buttons.copy())
                buttons.clear()
        if buttons:
            buttons_list.append(buttons.copy())
        add_tag_in_telegram_data(context, tags=["fortune_roll", "buttons_list"], value=buttons_list)
        add_tag_in_telegram_data(context, tags=["fortune_roll", "query_menu_index"], value=0)

        query_menu = context.user_data["fortune_roll"]["invocation_message"].reply_text(
            placeholders["5"], ParseMode.HTML, reply_markup=build_multi_page_kb(buttons_list[0]))

        add_tag_in_telegram_data(context, ["fortune_roll", "query_menu"], query_menu)

        return 30

    # Crew tier
    elif choice == 5:
        crew_tier = controller.get_crew_tier(query_game_of_user(chat_id, get_user_id(update)))
        add_tag_in_telegram_data(context, ["fortune_roll", "roll", "what"], "Crew's tier: {}".format(crew_tier))
        add_tag_in_telegram_data(context, ["fortune_roll", "dice"], crew_tier)
        return send_fortune_roll_bonus_dice(context)

    # Faction tier
    elif choice == 6:
        factions = controller.get_factions(query_game_of_user(chat_id, get_user_id(update)))

        buttons_list = []
        buttons = []
        for i in range(len(factions)):
            buttons.append(factions[i])
            if (i + 1) % 8 == 0:
                buttons_list.append(buttons.copy())
                buttons.clear()
        if buttons:
            buttons_list.append(buttons.copy())
        add_tag_in_telegram_data(context, tags=["fortune_roll", "buttons_list"], value=buttons_list)
        add_tag_in_telegram_data(context, tags=["fortune_roll", "query_menu_index"], value=0)

        query_menu = context.user_data["fortune_roll"]["invocation_message"].reply_text(
            placeholders["2"], ParseMode.HTML, reply_markup=build_multi_page_kb(buttons_list[0]))

        add_tag_in_telegram_data(context, ["fortune_roll", "query_menu"], query_menu)

        return 20


def fortune_roll_what(update: Update, context: CallbackContext) -> int:
    """
    Stores the "what" (what is rolled) of the fortune roll in the user_data.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: send_fortune_roll_bonus_dice
    """
    context.user_data["fortune_roll"]["message"].delete()

    query = update.callback_query
    query.answer()
    choice = query.data

    add_tag_in_telegram_data(context, ["fortune_roll", "roll", "what"], choice)
    add_tag_in_telegram_data(context, ["fortune_roll", "dice"], int(choice.split(": ")[1]))

    return send_fortune_roll_bonus_dice(context)


def send_fortune_roll_bonus_dice(context: CallbackContext) -> int:
    """
    Sends the keyboard for the bonus dice of the fortune roll

    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, "bonus_dice")
    query_menu = context.user_data["fortune_roll"]["invocation_message"].reply_text(
        placeholders["message"].format(fortune_roll_calc_total_dice(context.user_data["fortune_roll"])),
        reply_markup=build_plus_minus_keyboard(
            [placeholders["button"].format(
                context.user_data["fortune_roll"]["bonus_dice"])],
            done_button=True,
            back_button=False),
        parse_mode=ParseMode.HTML)

    add_tag_in_telegram_data(context, tags=["fortune_roll", "query_menu"], value=query_menu)

    return 3


def fortune_roll_calc_total_dice(fortune_dict: dict) -> int:
    """
    Calculates the total dice added for the fortune roll so far.

    :param fortune_dict: a dictionary containing the fortune roll's info
    :return: the total number of dice.
    """
    return fortune_dict["bonus_dice"] + fortune_dict["dice"]


def fortune_roll_bonus_dice(update: Update, context: CallbackContext) -> int:
    """
    Handles the addition or removal of bonus dice and updates the related Keyboard.
    When the user confirms, the number of dice to roll is passed to roll_dice method.
    Then, the outcome is stored in the chat_data and the final description request is sent.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation when the "DONE" button is pressed.
    """
    placeholders = get_lang(context, fortune_roll_bonus_dice.__name__)

    query = update.callback_query
    query.answer()

    bonus_dice = context.user_data["fortune_roll"]["bonus_dice"]

    choice = query.data
    if "+" in choice or "-" in choice:
        tags = ["fortune_roll", "bonus_dice"]
        bonus_dice += int(choice.split(" ")[2])
        add_tag_in_telegram_data(context, tags=tags, value=bonus_dice)

        update_bonus_dice_kb(context, tags,
                             fortune_roll_calc_total_dice(context.user_data["fortune_roll"]), "user")

    elif choice == "DONE":
        dice_to_roll = fortune_roll_calc_total_dice(context.user_data["fortune_roll"])

        context.user_data["fortune_roll"]["query_menu"].delete()

        roll_dice(update, context, dice_to_roll, ["fortune_roll", "roll", "outcome"], "user")

        context.user_data["fortune_roll"]["message"] = \
            context.user_data["fortune_roll"]["invocation_message"].reply_text(
                placeholders["0"], parse_mode=ParseMode.HTML)
        return 4

    else:
        bonus_dice_lang = get_lang(context, "bonus_dice")
        auto_delete_message(update.effective_message.reply_text(bonus_dice_lang["fortune_roll_extended"],
                                                                parse_mode=ParseMode.HTML),
                            bonus_dice_lang["fortune_roll_extended"])

    return 3


def fortune_roll_notes(update: Update, context: CallbackContext) -> int:
    add_tag_in_telegram_data(context, ["fortune_roll", "roll", "notes"], update.message.text)

    chat_id = update.message.chat_id
    if controller.is_master(get_user_id(update), chat_id):
        add_tag_in_telegram_data(context, ["fortune_roll", "roll", "pc"], "The GM")
    else:
        add_tag_in_telegram_data(context, ["fortune_roll", "roll", "pc"], context.user_data["active_PCs"][chat_id])
    controller.commit_fortune_roll(query_game_of_user(chat_id, get_user_id(update)),
                                   context.user_data["fortune_roll"]["roll"])

    return fortune_roll_end(update, context)


def fortune_roll_action(update: Update, context: CallbackContext) -> int:
    """
    Handles the choice of the action to roll.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, fortune_roll_action.__name__)
    context.user_data["fortune_roll"]["message"].delete()

    query = update.callback_query
    query.answer()
    choice = query.data

    chat_id = update.effective_message.chat_id
    pc_name = context.user_data["active_PCs"][chat_id]
    actions = controller.get_pc_actions_ratings(get_user_id(update), chat_id, pc_name, choice)
    keyboard = ["{}: {}".format(action[0], action[1]) for action in actions]
    message = context.user_data["fortune_roll"]["invocation_message"].reply_text(placeholders["0"], ParseMode.HTML,
                                                                                 reply_markup=custom_kb(
                                                                                     keyboard, True, 1))

    add_tag_in_telegram_data(context, ["fortune_roll", "message"], message)

    return 2


def fortune_roll_faction(update: Update, context: CallbackContext) -> int:
    """
    Handles the choice of the faction used to perform the roll.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """

    placeholders = get_lang(context, fortune_roll_faction.__name__)

    query = update.callback_query
    query.answer()

    choice = query.data
    index = context.user_data["fortune_roll"]["query_menu_index"]

    if choice == "RIGHT":
        index += 1
        if index > len(context.user_data["fortune_roll"]["buttons_list"]):
            index = 0
        context.user_data["fortune_roll"]["query_menu_index"] = index

    elif choice == "LEFT":
        index -= 1
        if index == -len(context.user_data["fortune_roll"]["buttons_list"]):
            index = 0

        context.user_data["fortune_roll"]["query_menu_index"] = index
    else:
        name = choice.split("$")[0]
        name = name.split(" - ")[1]
        if "$" in choice:
            add_tag_in_telegram_data(context, tags=["fortune_roll", "roll", "what"],
                                     value=name)
            add_tag_in_telegram_data(context, tags=["fortune_roll", "dice"],
                                     value=int(name.split(": ")[1]))

            context.user_data["fortune_roll"]["query_menu"].delete()

            return send_fortune_roll_bonus_dice(context)
        else:
            name = name.split(":")[0]
            description = query_factions(name=name, as_dict=True)[0]["description"]

            if description is None or description == "":
                description = placeholders["404"]
            auto_delete_message(update.effective_message.reply_text(
                text=description, quote=False), description)
            return 20

    context.user_data["fortune_roll"]["query_menu"].edit_text(
        placeholders["0"], reply_markup=build_multi_page_kb(
            context.user_data["fortune_roll"]["buttons_list"][
                context.user_data["fortune_roll"]["query_menu_index"]]))
    return 20


def fortune_roll_item(update: Update, context: CallbackContext) -> int:
    """
    Handles the choice of the item used to perform the roll.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """

    placeholders = get_lang(context, fortune_roll_item.__name__)

    query = update.callback_query
    query.answer()

    choice = query.data
    index = context.user_data["fortune_roll"]["query_menu_index"]

    if choice == "RIGHT":
        index += 1
        if index > len(context.user_data["fortune_roll"]["buttons_list"]):
            index = 0
        context.user_data["fortune_roll"]["query_menu_index"] = index

    elif choice == "LEFT":
        index -= 1
        if index == -len(context.user_data["fortune_roll"]["buttons_list"]):
            index = 0

        context.user_data["fortune_roll"]["query_menu_index"] = index
    else:
        name = choice.split("$")[0]
        if "$" in choice:
            add_tag_in_telegram_data(context, tags=["fortune_roll", "roll", "what"],
                                     value=name)

            add_tag_in_telegram_data(context, tags=["fortune_roll", "dice"],
                                     value=int(name.split(": ")[1]))

            context.user_data["fortune_roll"]["query_menu"].delete()

            return send_fortune_roll_bonus_dice(context)
        else:
            name = name.split(":")[0]
            description, weight, usages, quality = controller.get_item_description(
                update.effective_message.chat_id, get_user_id(update), name,
                context.user_data["active_PCs"][update.effective_message.chat_id])
            info = placeholders["1"].format(description, weight, usages, quality)
            auto_delete_message(update.effective_message.reply_text(text=info, quote=False), info)
            return 30

    context.user_data["fortune_roll"]["query_menu"].edit_text(
        placeholders["0"], reply_markup=build_multi_page_kb(
            context.user_data["fortune_roll"]["buttons_list"][
                context.user_data["fortune_roll"]["query_menu_index"]]))
    return 30


def fortune_roll_end(update: Update, context: CallbackContext) -> int:
    """
    Ends the fortune roll conversation and deletes all the saved information from the user_data.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: ConversationHandler.END
    """
    delete_conv_from_telegram_data(context, "fortune_roll")

    return end_conv(update, context)


# ------------------------------------------conv_fortune_roll-----------------------------------------------------------


# ------------------------------------------conv_add_exp----------------------------------------------------------------


def add_exp(update: Update, context: CallbackContext) -> int:
    """
    Checks if the user is in a game and in the correct phase, then starts the conversation that handles the exp
    and sends the user the inline keyboard.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, add_exp.__name__)

    if is_game_in_wrong_phase(update, context, placeholders["err"]):
        return add_exp_end(update, context)

    add_tag_in_telegram_data(context, ["add_exp", "invocation_message"], update.message)

    add_tag_in_telegram_data(context, ["add_exp", "info", "crew"], 0)
    add_tag_in_telegram_data(context, ["add_exp", "info", "playbook"], 0)
    add_tag_in_telegram_data(context, ["add_exp", "info", "insight"], 0)
    add_tag_in_telegram_data(context, ["add_exp", "info", "prowess"], 0)
    add_tag_in_telegram_data(context, ["add_exp", "info", "resolve"], 0)

    query_menu = update.message.reply_text(placeholders["0"],
                                           reply_markup=build_plus_minus_keyboard(
                                               build_add_exp_buttons(update, context),
                                               back_button=False, done_button=True))

    add_tag_in_telegram_data(context, ["add_exp", "query_menu"], query_menu)

    return 0


def build_add_exp_buttons(update: Update, context: CallbackContext) -> List[str]:
    """
    Builds the button for the inline keyboard used to add exp.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the list of buttons' label.
    """
    chat_id = update.effective_message.chat_id
    try:
        pc_name = context.user_data["active_PCs"][chat_id]
    except:
        pc_name = None
    exp_dict = controller.get_exp(chat_id, get_user_id(update), pc_name)

    buttons = []
    for key in exp_dict.keys():
        exp_dict[key] += context.user_data["add_exp"]["info"][key]
        buttons.append("{}: {}".format(key.capitalize(), exp_dict[key]))

    return buttons


def add_exp_amount(update: Update, context: CallbackContext) -> int:
    """
    Handles the selection of the buttons from the inline keyboard of the exp.
    Calls the controller method commit_add_exp() when DONE button is pressed.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.:
    :return: this state if the DONE button has not been pressed, add_coin_end otherwise.
    """
    placeholders = get_lang(context, add_exp_amount.__name__)

    query = update.callback_query
    query.answer()
    choice = query.data

    add_exp_info = context.user_data["add_exp"]["info"]
    chat_id = update.effective_message.chat_id
    try:
        pc_name = context.user_data["active_PCs"][chat_id]
    except:
        pc_name = None

    if "+" in choice or "-" in choice:
        choice = choice.split(" ")
        selection = choice[0].lower()
        exp = controller.get_exp(chat_id, get_user_id(update), pc_name, selection)
        if (add_exp_info[selection] + exp + int(choice[1])) >= 0:
            add_exp_info[selection] += int(choice[1])
        placeholders = get_lang(context, add_exp.__name__)
        context.user_data["add_exp"]["query_menu"].edit_text(placeholders["0"],
                                                             reply_markup=build_plus_minus_keyboard(
                                                                 build_add_exp_buttons(update, context),
                                                                 back_button=False,
                                                                 done_button=True))
        return 0
    elif choice == "DONE":
        result = controller.commit_add_exp(chat_id, get_user_id(update), pc_name, add_exp_info)
        for t in result:
            auto_delete_message(context.user_data["add_exp"]["invocation_message"].reply_text(
                placeholders[t[0]].format(t[1])
            ))
        return add_exp_end(update, context)
    else:
        name = choice.split(": ")[0].lower()
        if name == "crew":
            auto_delete_message(context.user_data["add_exp"]["invocation_message"].reply_text(
                placeholders["crew"].format(controller.get_playbook_size(chat_id, get_user_id(update)))))
        else:
            auto_delete_message(context.user_data["add_exp"]["invocation_message"].reply_text(
                placeholders[name].format(controller.get_playbook_size(chat_id, get_user_id(update),
                                                                       pc_name, attribute=name))))
        return 0


def add_exp_end(update: Update, context: CallbackContext) -> int:
    """
    Ends the add exp conversation and deletes all the saved information from the user_data.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: ConversationHandler.END
    """
    delete_conv_from_telegram_data(context, "add_exp")

    return end_conv(update, context)


# ------------------------------------------conv_add_exp----------------------------------------------------------------


# ------------------------------------------conv_add_upgrade------------------------------------------------------------


def add_upgrade(update: Update, context: CallbackContext) -> int:
    """
    Checks if the user is in a game and in the correct phase, then starts the conversation that handles the upgrades
    and sends the user the inline keyboard.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, add_upgrade.__name__)

    if is_game_in_wrong_phase(update, context, placeholders["err"]):
        return add_upgrade_end(update, context)

    add_tag_in_telegram_data(context, ["add_upgrade", "invocation_message"], update.message)
    add_tag_in_telegram_data(context, ["add_upgrade", "info", "upgrade_points"], controller.get_crew_upgrade_points(
        query_game_of_user(update.effective_message.chat_id, get_user_id(update))
    ))

    add_tag_in_telegram_data(context, ["add_upgrade", "info", "upgrades"], controller.get_crew_upgrades(
        query_game_of_user(update.effective_message.chat_id, get_user_id(update))))

    groups = query_upgrade_groups()
    groups.append("DONE")

    query_menu = update.message.reply_text(placeholders["0"], reply_markup=custom_kb(groups, inline=True, split_row=2))
    add_tag_in_telegram_data(context, ["add_upgrade", "query_menu"], query_menu)

    return 0


def add_upgrade_group(update: Update, context: CallbackContext) -> int:
    """
    Stores the group of the upgrade chosen by the user in the user_data and asks to divide the upgrade points between
    all the upgrades of the category. If DONE is selected then calls commit_add_upgrades in controller.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, add_upgrade_group.__name__)

    query = update.callback_query
    query.answer()
    choice = query.data

    add_tag_in_telegram_data(context, ["add_upgrade", "info", "group"], choice)

    context.user_data["add_upgrade"]["query_menu"].delete()

    upgrades = context.user_data["add_upgrade"]["info"]["upgrades"]

    if choice == "DONE":
        controller.commit_add_upgrade(update.effective_message.chat_id,
                                      get_user_id(update), context.user_data["add_upgrade"]["info"]["upgrades"],
                                      context.user_data["add_upgrade"]["info"]["upgrade_points"])
        return add_upgrade_end(update, context)
    elif choice.lower() == "specific":
        buttons = create_central_buttons_upgrades(upgrades, choice, controller.get_crew_type(query_game_of_user(
            update.effective_message.chat_id, get_user_id(update))))
    else:
        buttons = create_central_buttons_upgrades(upgrades, choice)

    query_menu = context.user_data["add_upgrade"]["invocation_message"].reply_text(
        placeholders["0"].format(context.user_data["add_upgrade"]["info"]["upgrade_points"]),
        reply_markup=build_plus_minus_keyboard(buttons))

    add_tag_in_telegram_data(context, ["add_upgrade", "query_menu"], query_menu)

    return 1


def add_upgrade_selection(update: Update, context: CallbackContext) -> int:
    """
    Gets the user selection, removes the amount of available upgrade points and increase the quality of
    the selected upgrade.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, add_upgrade_selection.__name__)

    query = update.callback_query
    query.answer()
    choice = query.data

    upgrades = context.user_data["add_upgrade"]["info"]["upgrades"]

    if "+" in choice or "-" in choice:
        choice = choice.split(" ")
        name = choice[0]
        for i in range(1, len(choice) - 1):
            name += " {}".format(choice[i])

        upgrade = None
        for upg in upgrades:
            if upg["name"] == name:
                if "+" in choice and context.user_data["add_upgrade"]["info"]["upgrade_points"] > 0:
                    upg["quality"] += int(choice[-1])
                    context.user_data["add_upgrade"]["info"]["upgrade_points"] -= int(choice[-1])
                else:
                    upg["quality"] += int(choice[-1])
                    context.user_data["add_upgrade"]["info"]["upgrade_points"] -= int(choice[-1])
                if upg["quality"] == 0:
                    upgrades.remove(upg)
                else:
                    upgrade = upg
                break

        if upgrade is None and "+" in choice[-1]:
            if context.user_data["add_upgrade"]["info"]["upgrade_points"] > 0:
                upgrades.append(
                    {"name": name, "quality": 1, "tot_quality": query_upgrades(name)[0]["tot_quality"]})
                context.user_data["add_upgrade"]["info"]["upgrade_points"] -= 1
                upgrade = upgrades[-1]

        if upgrade is not None:
            if upgrade["quality"] < 0:
                context.user_data["add_upgrade"]["info"]["upgrade_points"] -= 1
                upgrade["quality"] = 0

            tot_quality = query_upgrades(upgrade["name"])[0]["tot_quality"]
            if upgrade["quality"] > tot_quality:
                context.user_data["add_upgrade"]["info"]["upgrade_points"] += 1
                upgrade["quality"] = tot_quality

        group = context.user_data["add_upgrade"]["info"]["group"]

        if group.lower() == "specific":
            buttons = create_central_buttons_upgrades(upgrades, group, controller.get_crew_type(query_game_of_user(
                update.effective_message.chat_id, get_user_id(update))))
        else:
            buttons = create_central_buttons_upgrades(upgrades, group)

        # context.user_data["add_upgrade"]["query_menu"].delete()
        context.user_data["add_upgrade"]["query_menu"].edit_text(
            text=placeholders["0"].format(context.user_data["add_upgrade"]["info"]["upgrade_points"]),
            reply_markup=build_plus_minus_keyboard(buttons))
        return 1

    elif choice == "BACK":
        group = query_upgrade_groups()
        group.append("DONE")
        context.user_data["add_upgrade"]["query_menu"].delete()
        context.user_data["add_upgrade"]["query_menu"] = context.user_data["add_upgrade"][
            "invocation_message"].reply_text(
            text=placeholders["1"].format(context.user_data["add_upgrade"]["info"]["upgrade_points"]),
            reply_markup=custom_kb(group, inline=True, split_row=2))
        return 0

    else:

        description = query_upgrades(upgrade=choice)[0]["description"]
        auto_delete_message(context.user_data["add_upgrade"]["invocation_message"].reply_text(
            text=description,
        ), description)
        return 1


def add_upgrade_end(update: Update, context: CallbackContext) -> int:
    """
    Ends the add upgrade conversation and deletes all the saved information from the user_data.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: ConversationHandler.END
    """
    delete_conv_from_telegram_data(context, "add_upgrade")

    return end_conv(update, context)


# ------------------------------------------conv_add_upgrade------------------------------------------------------------


# ------------------------------------------conv_downtimeActivity-------------------------------------------------------


def downtime(update: Update, context: CallbackContext) -> int:
    placeholders = get_lang(context, downtime.__name__)

    if is_game_in_wrong_phase(update, context, placeholders["err"], 2):
        return downtime_end(update, context)

    chat_id = update.message.chat_id
    if ("active_PCs" in context.user_data and chat_id not in context.user_data["active_PCs"]) or \
            ("active_PCs" not in context.user_data):
        auto_delete_message(update.message.reply_text(placeholders["err2"]), 15)
        return downtime_end(update, context)

    add_tag_in_telegram_data(context, ["downtime", "invoker"], get_user_id(update), "chat")
    add_tag_in_telegram_data(context, ["downtime", "invocation_message"], update.message, "chat")
    add_tag_in_telegram_data(context, ["downtime", "info", "pc"], context.user_data["active_PCs"][chat_id], "chat")

    message = update.message.reply_text(placeholders["0"], ParseMode.HTML, reply_markup=custom_kb(
        placeholders["keyboard"], True, 2, placeholders["callbacks"]))
    add_tag_in_telegram_data(context, ["downtime", "message"], message, "chat")

    return 0


def downtime_choice(update: Update, context: CallbackContext) -> Optional[int]:
    if get_user_id(update) != context.chat_data["downtime"]["invoker"]:
        return

    placeholders = get_lang(context, downtime_choice.__name__)
    context.chat_data["downtime"]["message"].delete()

    query = update.callback_query
    query.answer()
    choice = query.data

    chat_id = update.effective_message.chat_id

    # Acquire Asset
    if choice == 1:
        add_tag_in_telegram_data(context, ["downtime", "info", "activity"], "acquire_asset", "chat")
        message = context.chat_data["downtime"]["invocation_message"].reply_text(placeholders["1"])
        add_tag_in_telegram_data(context, ["downtime", "message"], message, "chat")
        return 10
    # Crafting
    elif choice == 2:
        add_tag_in_telegram_data(context, ["downtime", "info", "activity"], "crafting", "chat")
        message = context.chat_data["downtime"]["invocation_message"].reply_text(placeholders["2"])
        add_tag_in_telegram_data(context, ["downtime", "message"], message, "chat")
        return 20
    # Long term project
    elif choice == 3:
        add_tag_in_telegram_data(context, ["downtime", "info", "activity"], "long_term_project", "chat")
        keyboard = controller.get_clocks_of_game(query_game_of_user(chat_id, get_user_id(update)), True)
        keyboard.append(placeholders["new"])
        message = context.chat_data["downtime"]["invocation_message"].reply_text(
            placeholders["3"], reply_markup=custom_kb(keyboard, True, 1))
        add_tag_in_telegram_data(context, ["downtime", "message"], message, "chat")
        return 30
    # Recover
    elif choice == 4:
        add_tag_in_telegram_data(context, ["downtime", "info", "activity"], "recover", "chat")
        keyboard = placeholders["keyboard4"].copy()
        callbacks = placeholders["callbacks4"].copy()
        if not controller.get_cohorts_of_crew(chat_id, get_user_id(update)):
            keyboard.pop(2)
            callbacks.pop(2)
        message = context.chat_data["downtime"]["invocation_message"].reply_text(
            placeholders["4"], reply_markup=custom_kb(keyboard, True, 1, callbacks))
        add_tag_in_telegram_data(context, ["downtime", "message"], message, "chat")
        return 40
    # Reduce heat
    elif choice == 5:
        add_tag_in_telegram_data(context, ["downtime", "info", "activity"], "reduce_heat", "chat")
        keyboard = query_attributes(True)
        message = context.chat_data["downtime"]["invocation_message"].reply_text(
            placeholders["5"], reply_markup=custom_kb(keyboard, True))
        add_tag_in_telegram_data(context, ["downtime", "message"], message, "chat")
        return 50
    # Train
    elif choice == 6:
        add_tag_in_telegram_data(context, ["downtime", "info", "activity"], "train", "chat")
        keyboard = ["Personal"]
        keyboard += query_attributes(True)
        message = context.chat_data["downtime"]["invocation_message"].reply_text(
            placeholders["6"], reply_markup=custom_kb(keyboard, True, 1))
        add_tag_in_telegram_data(context, ["downtime", "message"], message, "chat")
        return 60
    # Vice
    elif choice == 7:
        add_tag_in_telegram_data(context, ["downtime", "info", "activity"], "indulge_vice", "chat")
        attribute_ratings = [rating[1] for rating in controller.get_pc_attribute_rating(
            chat_id, get_user_id(update), context.user_data["active_PCs"][chat_id])]

        roll_dice(update, context, min(attribute_ratings), ["downtime", "info", "outcome"])

        outcome = context.chat_data["downtime"]["info"]["outcome"]
        placeholders = get_lang(context, "bonus_dice")
        query_menu = context.chat_data["downtime"]["invocation_message"].reply_text(
            placeholders["vice_message"], reply_markup=build_plus_minus_keyboard(
                [placeholders["vice_button"].format(outcome)], False, True))
        add_tag_in_telegram_data(context, ["downtime", "query_menu"], query_menu, "chat")
        return 70
    # Help cohort
    elif choice == 8:
        add_tag_in_telegram_data(context, ["downtime", "info", "activity"], "help_cohort", "chat")
        cohorts = controller.get_cohorts_of_crew(chat_id, get_user_id(update))
        if not cohorts:
            placeholders = get_lang(context, "missing_cohorts")
            auto_delete_message(context.chat_data["downtime"]["invocation_message"].reply_text(placeholders["0"]), 15)
            return downtime_end(update, context)
        cohorts = ["{}: {}".format(cohort[0], cohort[1]) for cohort in cohorts]
        callbacks = [i + 1 for i in range(len(cohorts))]
        message = context.chat_data["downtime"]["invocation_message"].reply_text(
            placeholders["8"], reply_markup=custom_kb(cohorts, True, 1, callbacks))
        add_tag_in_telegram_data(context, ["downtime", "message"], message, "chat")
        return 80
    # Replace cohort
    elif choice == 9:
        add_tag_in_telegram_data(context, ["downtime", "info", "activity"], "replace_cohort", "chat")
        cohorts = controller.get_cohorts_of_crew(chat_id, get_user_id(update), True)
        if not cohorts:
            placeholders = get_lang(context, "missing_cohorts")
            auto_delete_message(context.chat_data["downtime"]["invocation_message"].reply_text(placeholders["0"]), 15)
            return downtime_end(update, context)
        cohorts = ["\u2620\uFE0F{}: {}".format(cohort[0], cohort[1]) for cohort in cohorts]
        callbacks = [i + 1 for i in range(len(cohorts))]
        message = context.chat_data["downtime"]["invocation_message"].reply_text(
            placeholders["9"], reply_markup=custom_kb(cohorts, True, 1, callbacks))
        add_tag_in_telegram_data(context, ["downtime", "message"], message, "chat")
        return 80


def downtime_asset(update: Update, context: CallbackContext) -> Optional[int]:
    if get_user_id(update) != context.chat_data["downtime"]["invoker"]:
        return

    placeholders = get_lang(context, downtime_asset.__name__)
    context.chat_data["downtime"]["message"].delete()

    add_tag_in_telegram_data(context, ["downtime", "info", "asset"], update.message.text, "chat")

    message = context.chat_data["downtime"]["invocation_message"].reply_text(placeholders["1"].format(
        context.chat_data["downtime"]["info"]["pc"],
        context.chat_data["downtime"]["info"]["asset"]), parse_mode=ParseMode.HTML)

    add_tag_in_telegram_data(context, location="chat", tags=["downtime", "message"], value=message)

    add_tag_in_telegram_data(context, location="chat", tags=["downtime", "GM_question"],
                             value={"text": placeholders["0"],
                                    "reply_markup": custom_kb(buttons=placeholders["keyboard"])})

    update.message.delete()
    return 11


def downtime_minimum_quality(update: Update, context: CallbackContext) -> Optional[int]:
    placeholders = get_lang(context, downtime_minimum_quality.__name__)
    context.chat_data["downtime"]["message"].delete()

    try:
        quality = int(update.message.text)
    except:
        message = context.chat_data["downtime"]["invocation_message"].reply_text(placeholders["err"])
        add_tag_in_telegram_data(context, ["downtime", "message"], message, "chat")
        return 0

    add_tag_in_telegram_data(context, location="chat", tags=["downtime", "info", "minimum_quality"], value=quality)
    add_tag_in_telegram_data(context, location="chat", tags=["downtime", "dice"], value=controller.get_crew_tier(
        query_game_of_user(update.message.chat_id, get_user_id(update))))
    add_tag_in_telegram_data(context, location="chat", tags=["downtime", "bonus_dice"], value=0)

    send_downtime_bonus_dice(context)

    update.message.delete()
    return 1


def send_downtime_bonus_dice(context: CallbackContext):
    """
    Sends the keyboard for the bonus dice of the downtime activity

    :param context: instance of CallbackContext linked to the user.
    """
    placeholders = get_lang(context, "bonus_dice")
    query_menu = context.chat_data["downtime"]["invocation_message"].reply_text(
        placeholders["message"].format(downtime_calc_total_dice(context.chat_data["downtime"])),
        reply_markup=build_plus_minus_keyboard(
            [placeholders["button"].format(
                context.chat_data["downtime"]["bonus_dice"])],
            done_button=True,
            back_button=False),
        parse_mode=ParseMode.HTML)

    add_tag_in_telegram_data(context, location="chat", tags=["downtime", "query_menu"], value=query_menu)


def downtime_calc_total_dice(downtime_dict: dict) -> int:
    """
    Calculates the total dice added for the fortune roll so far.

    :param downtime_dict: a dictionary containing the fortune roll's info
    :return: the total number of dice.
    """
    return downtime_dict["bonus_dice"] + downtime_dict["dice"]


def downtime_bonus_dice(update: Update, context: CallbackContext) -> Optional[int]:
    """
    Handles the addition or removal of bonus dice and updates the related Keyboard.
    When the user confirms, the number of dice to roll is passed to roll_dice method.
    Then, the outcome is stored in the chat_data and the final description request is sent.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation when the "DONE" button is pressed.
    """
    if get_user_id(update) != context.chat_data["downtime"]["invoker"]:
        return

    placeholders = get_lang(context, downtime_bonus_dice.__name__)

    query = update.callback_query
    query.answer()

    bonus_dice = context.chat_data["downtime"]["bonus_dice"]
    activity = context.chat_data["downtime"]["info"]["activity"]

    choice = query.data
    if "+" in choice or "-" in choice:
        tags = ["downtime", "bonus_dice"]
        bonus_dice += int(choice.split(" ")[2])
        add_tag_in_telegram_data(context, location="chat", tags=tags, value=bonus_dice)

        update_bonus_dice_kb(context, tags, downtime_calc_total_dice(context.chat_data["downtime"]))

    elif choice == "DONE":
        dice_to_roll = downtime_calc_total_dice(context.chat_data["downtime"])

        context.chat_data["downtime"]["query_menu"].delete()

        roll_dice(update, context, dice_to_roll, ["downtime", "info", "outcome"])

        if activity != "crafting" and activity != "acquire_asset":
            placeholders = get_lang(context, downtime_notes.__name__)
            context.chat_data["downtime"]["message"] = \
                context.chat_data["downtime"]["invocation_message"].reply_text(
                    placeholders["0"], parse_mode=ParseMode.HTML)
            return 2

        else:
            outcome = context.chat_data["downtime"]["info"]["outcome"]
            crew_tier = controller.get_crew_tier(query_game_of_user(
                update.effective_message.chat_id, get_user_id(update)))
            quality = crew_tier
            if isinstance(outcome, str):
                quality += 2
            else:
                if 1 <= outcome <= 3:
                    quality += -1
                elif outcome == 6:
                    quality += 1
            add_tag_in_telegram_data(context, location="chat", tags=["downtime", "info", "quality"], value=quality)
            context.chat_data["downtime"]["message"] = \
                context.chat_data["downtime"]["invocation_message"].reply_text(
                    placeholders["0"].format(context.chat_data["downtime"]["info"]["minimum_quality"], quality),
                    parse_mode=ParseMode.HTML)
            return 0

    else:
        bonus_dice_lang = get_lang(context, "bonus_dice")
        auto_delete_message(update.effective_message.reply_text(bonus_dice_lang["extended"],
                                                                parse_mode=ParseMode.HTML),
                            bonus_dice_lang["extended"])
    if activity != "crafting" and activity != "acquire_asset":
        return 1
    else:
        return 12


def downtime_added_quality(update: Update, context: CallbackContext) -> Optional[int]:
    placeholders = get_lang(context, downtime_added_quality.__name__)

    try:
        extra_quality = int(update.message.text)
        if extra_quality < 0:
            raise Exception
    except:
        message = context.chat_data["downtime"]["invocation_message"].reply_text(placeholders["err"])
        add_tag_in_telegram_data(context, ["downtime", "message"], message, "chat")
        return 0

    chat_id = update.effective_message.chat_id

    add_tag_in_telegram_data(context, location="chat", tags=["downtime", "info", "extra_quality"], value=extra_quality)

    crew_tier = controller.get_crew_tier(query_game_of_user(chat_id, get_user_id(update)))
    tot_quality = context.chat_data["downtime"]["info"]["quality"]

    if tot_quality + extra_quality < context.chat_data["downtime"]["info"]["minimum_quality"]:
        auto_delete_message(context.chat_data["downtime"]["invocation_message"].reply_text(
            placeholders["0"].format(extra_quality), ParseMode.HTML), 15)

        placeholders = get_lang(context, downtime_notes.__name__)
        message = context.chat_data["downtime"]["invocation_message"].reply_text(placeholders["0"], ParseMode.HTML)
        add_tag_in_telegram_data(context, ["downtime", "message"], message, "chat")
        return 3

    elif extra_quality > 0:
        context.chat_data["downtime"]["message"].delete()
        placeholders = get_lang(context, "payment_keyboard")

        keyboard = placeholders["keyboard"].copy()
        callbacks = placeholders["callbacks"].copy()

        if context.chat_data["downtime"]["info"]["activity"] == "acquire_asset":
            coins = controller.calc_coins_acquire_asset(tot_quality, extra_quality, crew_tier)

            can_pay_crew, can_pay_possession = controller.can_pay(chat_id, get_user_id(update),
                                                                  context.chat_data["downtime"]["info"]["pc"], coins)
        else:
            coins = extra_quality
            can_pay_crew, can_pay_possession = controller.can_pay(chat_id, get_user_id(update),
                                                                  context.chat_data["downtime"]["info"]["pc"],
                                                                  coins)
        if not can_pay_possession:
            keyboard.pop(1)
            callbacks.pop(1)
        if not can_pay_crew:
            keyboard.pop(0)
            callbacks.pop(0)

        message = context.chat_data["downtime"]["invocation_message"].reply_text(
            placeholders["0"].format(coins), ParseMode.HTML,
            reply_markup=custom_kb(keyboard, True, 1, callbacks))
        add_tag_in_telegram_data(context, ["downtime", "message"], message, "chat")

        return 1

    else:
        context.chat_data["downtime"]["message"].delete()
        placeholders = get_lang(context, downtime_notes.__name__)
        message = context.chat_data["downtime"]["invocation_message"].reply_text(
            placeholders["0"], ParseMode.HTML)
        add_tag_in_telegram_data(context, ["downtime", "message"], message, "chat")
        return 2


def downtime_payment(update: Update, context: CallbackContext) -> int:
    placeholders = get_lang(context, downtime_payment.__name__)
    context.chat_data["downtime"]["message"].delete()

    query = update.callback_query
    query.answer()
    choice = query.data

    add_tag_in_telegram_data(context, ["downtime", "info", "payment"], choice, "chat")

    activity = context.chat_data["downtime"]["info"]["activity"]

    if activity.lower() == "crafting":
        message = context.chat_data["downtime"]["invocation_message"].reply_text(placeholders["1"], ParseMode.HTML)
        add_tag_in_telegram_data(context, ["downtime", "message"], message, "chat")

    else:
        message = context.chat_data["downtime"]["invocation_message"].reply_text(placeholders["0"], ParseMode.HTML)
        add_tag_in_telegram_data(context, ["downtime", "message"], message, "chat")

    return 2


def downtime_item(update: Update, context: CallbackContext) -> Optional[int]:
    if get_user_id(update) != context.chat_data["downtime"]["invoker"]:
        return

    placeholders = get_lang(context, downtime_item.__name__)
    context.chat_data["downtime"]["message"].delete()

    add_tag_in_telegram_data(context, ["downtime", "info", "item"], update.message.text, "chat")

    message = context.chat_data["downtime"]["invocation_message"].reply_text(placeholders["1"].format(
        context.chat_data["downtime"]["info"]["pc"],
        context.chat_data["downtime"]["info"]["item"]), parse_mode=ParseMode.HTML)

    add_tag_in_telegram_data(context, location="chat", tags=["downtime", "message"], value=message)

    add_tag_in_telegram_data(context, location="chat", tags=["downtime", "GM_question"],
                             value={"text": placeholders["0"],
                                    "reply_markup": custom_kb(buttons=placeholders["keyboard"])})

    update.message.delete()
    return 21


def downtime_item_description(update: Update, context: CallbackContext) -> Optional[int]:
    if get_user_id(update) != context.chat_data["downtime"]["invoker"]:
        return

    placeholders = get_lang(context, downtime_notes.__name__)
    context.chat_data["downtime"]["message"].delete()

    add_tag_in_telegram_data(context, ["downtime", "info", "item_description"], update.message.text, "chat")

    message = context.chat_data["downtime"]["invocation_message"].reply_text(placeholders["0"], ParseMode.HTML)
    add_tag_in_telegram_data(context, ["downtime", "message"], message, "chat")

    update.message.delete()
    return 3


def downtime_attribute_train_choice(update: Update, context: CallbackContext) -> int:
    placeholders = get_lang(context, downtime_notes.__name__)
    context.chat_data["downtime"]["message"].delete()

    query = update.callback_query
    query.answer()
    choice = query.data

    add_tag_in_telegram_data(context, ["downtime", "info", "attribute"], choice, "chat")

    message = context.chat_data["downtime"]["invocation_message"].reply_text(placeholders["0"], ParseMode.HTML)
    add_tag_in_telegram_data(context, ["downtime", "message"], message, "chat")
    return 1


def downtime_cohort_choice(update: Update, context: CallbackContext) -> int:
    placeholders = get_lang(context, downtime_notes.__name__)
    context.chat_data["downtime"]["message"].delete()

    query = update.callback_query
    query.answer()
    choice = int(query.data) - 1

    add_tag_in_telegram_data(context, ["downtime", "info", "cohort"], choice, "chat")
    activity = context.chat_data["downtime"]["info"]["activity"]
    if activity == "replace_cohort":
        placeholders = get_lang(context, "payment_keyboard")

        keyboard = placeholders["keyboard"].copy()
        callbacks = placeholders["callbacks"].copy()

        chat_id = update.effective_message.chat_id
        coins = controller.get_crew_tier(query_game_of_user(chat_id, get_user_id(update))) + 2
        can_pay_crew, can_pay_possession = controller.can_pay(
            chat_id, get_user_id(update), context.chat_data["downtime"]["info"]["pc"], coins)
        if not can_pay_possession:
            keyboard.pop(1)
            callbacks.pop(1)
        if not can_pay_crew:
            keyboard.pop(0)
            callbacks.pop(0)

        message = context.chat_data["downtime"]["invocation_message"].reply_text(
            placeholders["0"].format(coins), ParseMode.HTML,
            reply_markup=custom_kb(keyboard, True, 1, callbacks))
        add_tag_in_telegram_data(context, ["downtime", "message"], message, "chat")
        return 0
    elif activity == "recover":
        cohort_quality = controller.get_cohorts_of_crew(
            update.effective_message.chat_id, get_user_id(update))[choice][1]

        add_tag_in_telegram_data(context, ["downtime", "dice"], cohort_quality, "chat")

        send_downtime_bonus_dice(context)
        return 1
    else:
        message = context.chat_data["downtime"]["invocation_message"].reply_text(placeholders["0"], ParseMode.HTML)
        add_tag_in_telegram_data(context, ["downtime", "message"], message, "chat")
        return 1


def downtime_attribute_choice(update: Update, context: CallbackContext) -> Optional[int]:
    if get_user_id(update) != context.chat_data["downtime"]["invoker"]:
        return

    placeholders = get_lang(context, downtime_attribute_choice.__name__)
    context.chat_data["downtime"]["message"].delete()

    query = update.callback_query
    query.answer()
    choice = query.data

    actions = controller.get_pc_actions_ratings(get_user_id(update), update.effective_message.chat_id,
                                                context.chat_data["downtime"]["info"]["pc"], choice)
    actions = ["{}: {}".format(action[0], action[1]) for action in actions]

    message = context.chat_data["downtime"]["invocation_message"].reply_text(
        placeholders["0"], ParseMode.HTML, reply_markup=custom_kb(actions, True, 1))
    add_tag_in_telegram_data(context, ["downtime", "message"], message, "chat")
    return 0


def downtime_action_choice(update: Update, context: CallbackContext) -> int:
    context.chat_data["downtime"]["message"].delete()

    query = update.callback_query
    query.answer()
    choice = query.data

    add_tag_in_telegram_data(context, ["downtime", "info", "action"], choice, "chat")
    add_tag_in_telegram_data(context, ["downtime", "dice"], int(choice.split(": ")[1]), "chat")
    add_tag_in_telegram_data(context, ["downtime", "bonus_dice"], 0, "chat")

    send_downtime_bonus_dice(context)
    return 1


def downtime_project_choice(update: Update, context: CallbackContext) -> Optional[int]:
    if get_user_id(update) != context.chat_data["downtime"]["invoker"]:
        return
    placeholders = get_lang(context, downtime_project_choice.__name__)

    context.chat_data["downtime"]["message"].delete()

    query = update.callback_query
    query.answer()
    choice = query.data

    if choice == get_lang(context, downtime_choice.__name__)["new"]:
        message = context.chat_data["downtime"]["invocation_message"].reply_text(placeholders["0"], ParseMode.HTML)
        add_tag_in_telegram_data(context, ["downtime", "message"], message, "chat")

    else:
        name = choice.split(": ")[0]

        choice = choice.split(": ")[1]

        progress = int(choice.split("/")[0])
        segments = int(choice.split("/")[1])

        add_tag_in_telegram_data(context, ["downtime", "info", "clock", "name"], name, "chat")
        add_tag_in_telegram_data(context, ["downtime", "info", "clock", "segments"], segments, "chat")
        add_tag_in_telegram_data(context, ["downtime", "info", "clock", "progress"], progress, "chat")

        keyboard = query_attributes(True)
        message = context.chat_data["downtime"]["invocation_message"].reply_text(
            placeholders["1"], reply_markup=custom_kb(keyboard, True, 1))
        add_tag_in_telegram_data(context, ["downtime", "message"], message, "chat")

    return 50


def downtime_recover_choice(update: Update, context: CallbackContext) -> Optional[int]:
    if get_user_id(update) != context.chat_data["downtime"]["invoker"]:
        return
    placeholders = get_lang(context, downtime_recover_choice.__name__)

    context.chat_data["downtime"]["message"].delete()

    query = update.callback_query
    query.answer()
    choice = query.data

    chat_id = update.effective_message.chat_id

    add_tag_in_telegram_data(context, ["downtime", "bonus_dice"], 0, "chat")

    # NPC
    if choice == 1:
        npcs = controller.get_npcs(query_game_of_user(chat_id, get_user_id(update)))
        buttons_list = []
        buttons = []
        for i in range(len(npcs)):
            buttons.append(npcs[i])
            if (i + 1) % 8 == 0:
                buttons_list.append(buttons.copy())
                buttons.clear()
        if buttons:
            buttons_list.append(buttons.copy())
        add_tag_in_telegram_data(context, location="chat", tags=["downtime", "buttons_list"], value=buttons_list)
        add_tag_in_telegram_data(context, location="chat", tags=["downtime", "query_menu_index"], value=0)

        query_menu = context.chat_data["downtime"]["invocation_message"].reply_text(
            placeholders["1"], reply_markup=build_multi_page_kb(buttons_list[0]))

        add_tag_in_telegram_data(context, ["downtime", "query_menu"], query_menu, "chat")

        return 41

    # PC
    elif choice == 2:
        pcs = controller.get_user_characters_names(get_user_id(update), chat_id, True)
        buttons_list = ["{}: {}".format(
            pc, controller.get_pc_action_rating(get_user_id(update), chat_id, pc, "tinker")[1]) for pc in pcs]
        message = context.chat_data["downtime"]["invocation_message"].reply_text(
            placeholders["2"], reply_markup=custom_kb(buttons_list, True, 1))
        add_tag_in_telegram_data(context, ["downtime", "message"], message, "chat")
        return 42

    # Cohort
    elif choice == 3:
        cohorts = controller.get_cohorts_of_crew(chat_id, get_user_id(update))
        cohorts = ["{}: {}".format(cohort[0], cohort[1]) for cohort in cohorts]
        callbacks = [i + 1 for i in range(len(cohorts))]
        message = context.chat_data["downtime"]["invocation_message"].reply_text(
            placeholders["3"], reply_markup=custom_kb(cohorts, True, 1, callbacks))
        add_tag_in_telegram_data(context, ["downtime", "message"], message, "chat")

        return 43

    # Improvise
    else:
        add_tag_in_telegram_data(context, ["downtime", "dice"], 0, "chat")
        send_downtime_bonus_dice(context)
        return 1


def downtime_npc_selection(update: Update, context: CallbackContext) -> int:
    """
    Stores the information about an NPC or Faction target in the chat_data.
    Sends the score's plan type request.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, downtime_npc_selection.__name__)

    query = update.callback_query
    query.answer()

    choice = query.data
    index = context.chat_data["downtime"]["query_menu_index"]

    if choice == "RIGHT":
        index += 1
        if index > len(context.chat_data["downtime"]["buttons_list"]):
            index = 0
        context.chat_data["downtime"]["query_menu_index"] = index

    elif choice == "LEFT":
        index -= 1
        if index == -len(context.chat_data["downtime"]["buttons_list"]):
            index = 0

        context.chat_data["downtime"]["query_menu_index"] = index
    else:
        name = choice.split("$")[0]
        faction_name, name = name.split(" - ")
        if "$" in choice:
            add_tag_in_telegram_data(context, ["downtime", "info", "npc"], name, "chat")
            faction_name = faction_name.replace("[", "")
            faction_name = faction_name.replace("]", "")
            if faction_name != ' ':
                faction_tier = controller.get_factions(query_game_of_user(
                    update.effective_message.chat_id, get_user_id(update)), faction_name)[0].split(": ")[1]
            else:
                faction_tier = controller.get_crew_tier(query_game_of_user(
                    update.effective_message.chat_id, get_user_id(update)))
            add_tag_in_telegram_data(context, ["downtime", "dice"], int(faction_tier), "chat")
            context.chat_data["downtime"]["query_menu"].delete()
            send_downtime_bonus_dice(context)
            return 1
        else:
            npc_name = name.split(", ")[0]
            npc_role = name.split(", ")[1]
            description = query_npcs(name=npc_name,
                                     role=npc_role, as_dict=True)[0]["description"]

            if description is None or description == "":
                description = placeholders["404"]
            auto_delete_message(update.effective_message.reply_text(
                text=description, quote=False), description)
            return 41

    context.chat_data["downtime"]["query_menu"].edit_text(
        placeholders["0"], reply_markup=build_multi_page_kb(
            context.chat_data["downtime"]["buttons_list"][context.chat_data["downtime"]["query_menu_index"]]))
    return 41


def downtime_pc_selection(update: Update, context: CallbackContext) -> int:
    context.chat_data["downtime"]["message"].delete()

    query = update.callback_query
    query.answer()
    choice = query.data

    add_tag_in_telegram_data(context, ["downtime", "info", "healer"], choice, "chat")

    tinker_rating = choice.split(": ")[-1]

    add_tag_in_telegram_data(context, ["downtime", "dice"], int(tinker_rating), "chat")

    send_downtime_bonus_dice(context)
    return 1


def downtime_adjust_roll(update: Update, context: CallbackContext) -> Optional[int]:
    """
    Handles the addition or removal of bonus dice and updates the related Keyboard.
    When the user confirms, the number of dice to roll is passed to roll_dice method.
    Then, the outcome is stored in the chat_data and the final description request is sent.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation when the "DONE" button is pressed.
    """
    if get_user_id(update) != context.chat_data["downtime"]["invoker"]:
        return

    placeholders = get_lang(context, downtime_adjust_roll.__name__)

    query = update.callback_query
    query.answer()

    outcome = context.chat_data["downtime"]["info"]["outcome"]

    choice = query.data
    if "+" in choice or "-" in choice:
        if isinstance(outcome, str):
            outcome = 7
        outcome += int(choice.split(" ")[2])
        if outcome < 0:
            outcome = 0
        if outcome > 6:
            outcome = "CRIT"
        add_tag_in_telegram_data(context, location="chat", tags=["downtime", "info", "outcome"], value=outcome)
        placeholders = get_lang(context, "bonus_dice")
        context.chat_data["downtime"]["query_menu"].edit_text(
            placeholders["vice_message"],
            reply_markup=build_plus_minus_keyboard(
                [placeholders["vice_button"].format(outcome)],
                done_button=True,
                back_button=False),
            parse_mode=ParseMode.HTML)

    elif choice == "DONE":
        pc_name = context.chat_data["downtime"]["info"]["pc"]
        if not controller.has_pc_overindulged(update.effective_message.chat_id, get_user_id(update),
                                              pc_name, outcome):
            context.chat_data["downtime"]["query_menu"].delete()
            placeholders = get_lang(context, downtime_notes.__name__)
            context.chat_data["downtime"]["message"] = \
                context.chat_data["downtime"]["invocation_message"].reply_text(
                    placeholders["0"], parse_mode=ParseMode.HTML)
            return 1

        context.chat_data["downtime"]["query_menu"].delete()
        message = context.chat_data["downtime"]["invocation_message"].reply_text(
            placeholders["0"].format(pc_name), reply_markup=custom_kb(placeholders["keyboard"], True, 1,
                                                                      ["brag", "lost", "tapped", "trouble"]))
        add_tag_in_telegram_data(context, ["downtime", "message"], message, "chat")
        return 71

    else:
        bonus_dice_lang = get_lang(context, "bonus_dice")
        auto_delete_message(update.effective_message.reply_text(bonus_dice_lang["vice_extended"],
                                                                parse_mode=ParseMode.HTML),
                            bonus_dice_lang["vice_extended"])
    return 70


def downtime_master_choice(update: Update, context: CallbackContext) -> Optional[int]:
    if not controller.is_master(get_user_id(update), update.effective_message.chat_id):
        return

    placeholders = get_lang(context, downtime_master_choice.__name__)

    query = update.callback_query
    query.answer()
    choice = query.data

    add_tag_in_telegram_data(context, ["downtime", "info", "overindulge", "consequence"], choice, "chat")

    context.chat_data["downtime"]["message"].delete()

    if choice == "trouble":
        message = context.chat_data["downtime"]["invocation_message"].reply_text(
            placeholders["1"].format(choice), ParseMode.HTML)
        auto_delete_message(message, 25)
        placeholders = get_lang(context, downtime_notes.__name__)
        message = context.chat_data["downtime"]["invocation_message"].reply_text(placeholders["0"], ParseMode.HTML)
        add_tag_in_telegram_data(context, ["downtime", "message"], message, "chat")
        return 1

    message = context.chat_data["downtime"]["invocation_message"].reply_text(
        placeholders["0"].format(choice), ParseMode.HTML)
    add_tag_in_telegram_data(context, ["downtime", "message"], message, "chat")
    return 72


def downtime_overindulge_notes(update: Update, context: CallbackContext) -> Optional[int]:
    if get_user_id(update) != context.chat_data["downtime"]["invoker"]:
        return
    placeholders = get_lang(context, downtime_notes.__name__)

    context.chat_data["downtime"]["message"].delete()

    add_tag_in_telegram_data(context, ["downtime", "info", "overindulge", "notes"], update.message.text, "chat")

    message = context.chat_data["downtime"]["invocation_message"].reply_text(placeholders["0"], ParseMode.HTML)
    add_tag_in_telegram_data(context, ["downtime", "message"], message, "chat")

    update.message.delete()
    return 1


def downtime_notes(update: Update, context: CallbackContext) -> Optional[int]:
    if get_user_id(update) != context.chat_data["downtime"]["invoker"]:
        return
    placeholders = get_lang(context, downtime_notes.__name__)

    add_tag_in_telegram_data(context, ["downtime", "info", "notes"], update.message.text, "chat")

    return_dict = controller.commit_downtime_activity(update.effective_message.chat_id, get_user_id(update),
                                                      context.chat_data["downtime"]["info"])

    for key in return_dict.keys():
        context.chat_data["downtime"]["invocation_message"].reply_text(
            placeholders[str(key)].format(return_dict[key]), ParseMode.HTML)

    return downtime_end(update, context)


def downtime_end(update: Update, context: CallbackContext) -> int:
    """
    Ends the downtime activity conversation and deletes all the saved information from the user_data.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: ConversationHandler.END
    """
    delete_conv_from_telegram_data(context, "downtime", "chat")

    return end_conv(update, context)


# ------------------------------------------conv_downtimeActivity-------------------------------------------------------

def end_downtime(update: Update, context: CallbackContext):
    """
    Handles the closure of downtime activities. Checks if the game is not in score phase.
    Calls the controller method to apply the changes and sends to all the PCs who suffered trauma a notification.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    """
    placeholders = get_lang(context, end_downtime.__name__)
    if is_game_in_wrong_phase(update, context, placeholders["err"], 2):
        return
    trauma_suffers = controller.end_downtime(query_game_of_user(update.effective_message.chat_id, get_user_id(update)))

    for pc in trauma_suffers.keys():
        auto_delete_message(update.effective_message.reply_text(placeholders["trauma"].format(pc, trauma_suffers[pc]),
                                                                parse_mode=ParseMode.HTML), 15)

    auto_delete_message(update.effective_message.reply_text(placeholders["0"]), 15)


def change_vice_purveyor(update: Update, context: CallbackContext) -> int:
    """
    Handles the selection of a new vice purveyor. Checks if the game is not in init phase, if the user has an active
    PC for the game in this chat and if his PC is a Human.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, change_vice_purveyor.__name__)

    if is_game_in_wrong_phase(update, context, placeholders["err"]):
        return change_vice_purveyor_end(update, context)

    chat_id = update.effective_message.chat_id

    if chat_id not in context.user_data["active_PCs"]:
        auto_delete_message(update.effective_message.reply_text(placeholders["1"]), 10)
        return change_vice_purveyor_end(update, context)

    pc_name = context.user_data["active_PCs"][chat_id]

    if controller.get_pc_type(chat_id, get_user_id(update), pc_name).lower() != "Human".lower():
        auto_delete_message(update.effective_message.reply_text(placeholders["2"]), 10)
        return change_vice_purveyor_end(update, context)

    add_tag_in_telegram_data(context, tags=["change_vice_purveyor", "invocation_message"], value=update.message)

    message = context.user_data["change_vice_purveyor"]["invocation_message"].reply_text(placeholders["0"])

    add_tag_in_telegram_data(context, tags=["change_vice_purveyor", "message"], value=message)

    add_tag_in_telegram_data(context, tags=["change_vice_purveyor", "info", "pc"], value=pc_name)

    return 0


def change_vice_purveyor_selection(update: Update, context: CallbackContext) -> int:
    """
    Stores the new purveyor of the pc in the user_data.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: call to change_vice_purveyor_end().
    """

    context.user_data["change_vice_purveyor"]["message"].delete()

    add_tag_in_telegram_data(context, tags=["change_vice_purveyor", "info", "new_purveyor"], value=update.message.text)
    controller.change_vice_purveyor(update.effective_message.chat_id, get_user_id(update),
                                    context.user_data["change_vice_purveyor"]["info"])

    update.message.delete()

    return change_vice_purveyor_end(update, context)


def change_vice_purveyor_end(update: Update, context: CallbackContext) -> int:
    """
    Ends the change vice purveyor conversation and deletes all the saved information from the user_data.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: ConversationHandler.END
    """
    delete_conv_from_telegram_data(context, "change_vice_purveyor")

    return end_conv(update, context)


# ------------------------------------------conv_addAbility-------------------------------------------------------------


def add_ability(update: Update, context: CallbackContext) -> int:
    """
    Checks if the user is in a game and in the correct phase, then starts the conversation that handles the ability
    and sends the user the inline keyboard.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, add_ability.__name__)

    if is_game_in_wrong_phase(update, context, placeholders["err"]):
        return add_ability_end(update, context)

    add_tag_in_telegram_data(context, ["add_ability", "invocation_message"], update.message)

    buttons = build_add_ability_buttons(update, context)
    if len(buttons) == 0:
        auto_delete_message(update.effective_message.reply_text(placeholders["1"]), 10)
        return add_ability_end(update, context)
    buttons, callbacks = build_add_ability_buttons(update, context)
    if not buttons:
        message = update.message.reply_text(placeholders["noPoints"])
        auto_delete_message(message, placeholders["noPoints"])
        return add_ability_end(update, context)
    query_menu = update.message.reply_text(placeholders["0"], reply_markup=custom_kb(
        buttons, callback_data=callbacks, inline=True, split_row=1))

    add_tag_in_telegram_data(context, ["add_ability", "query_menu"], query_menu)

    return 0


def build_add_ability_buttons(update: Update, context: CallbackContext) -> Tuple[List[str], List[str]]:
    """
    Builds the list of buttons used to select between pc and crew in conv_addAbility.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: list of str representing the buttons.
    """
    placeholders = get_lang(context, add_ability.__name__)
    chat_id = update.effective_message.chat_id
    try:
        pc_name = context.user_data["active_PCs"][chat_id]
    except:
        pc_name = None
    buttons = []
    callbacks = []
    if controller.get_crew_exp_points(query_game_of_user(chat_id, get_user_id(update))) > 0:
        buttons.append(placeholders["keyboard"][0])
        callbacks.append(placeholders["callbacks"][0])
    if pc_name:
        if controller.get_pc_points(chat_id, get_user_id(update), pc_name)["Playbook"] > 0:
            buttons.append(placeholders["keyboard"][1])
            callbacks.append(placeholders["callbacks"][1])
        if controller.is_vampire(chat_id, get_user_id(update), pc_name):
            buttons.append(placeholders["keyboard"][2])
            callbacks.append(placeholders["callbacks"][2])
        if controller.is_hull(chat_id, get_user_id(update), pc_name):
            buttons.append(placeholders["keyboard"][3])
            callbacks.append(placeholders["callbacks"][3])

    return buttons, callbacks


def add_ability_owner(update: Update, context: CallbackContext) -> int:
    """
    Stores the choice made in the user_data and asks for which ability the user wants to add.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, add_ability_owner.__name__)

    query = update.callback_query
    query.answer()
    choice = query.data

    chat_id = update.effective_message.chat_id

    add_tag_in_telegram_data(context, ["add_ability", "info", "selection"], choice)

    if choice == 1:
        abilities = controller.get_crew_special_ability(chat_id, get_user_id(update))
    elif choice == 2:
        abilities = controller.get_pc_special_ability(chat_id, get_user_id(update),
                                                      context.user_data["active_PCs"][chat_id])
    elif choice == 3:
        abilities = controller.get_strictures(chat_id, get_user_id(update), context.user_data["active_PCs"][chat_id])
    else:
        abilities = controller.get_frame_features(chat_id, get_user_id(update),
                                                  context.user_data["active_PCs"][chat_id])

    buttons_list = []
    buttons = []
    for i in range(len(abilities)):
        buttons.append(abilities[i])
        if (i + 1) % 3 == 0:
            buttons_list.append(buttons.copy())
            buttons.clear()
    if buttons:
        buttons_list.append(buttons.copy())
    add_tag_in_telegram_data(context, ["add_ability", "buttons_list"], buttons_list)
    add_tag_in_telegram_data(context, ["add_ability", "query_menu_index"], 0)

    query_menu = context.user_data["add_ability"]["invocation_message"].reply_text(
        placeholders["0"], reply_markup=build_multi_page_kb(buttons_list[0])
    )
    context.user_data["add_ability"]["query_menu"].delete()

    add_tag_in_telegram_data(context, ["add_ability", "query_menu"], query_menu)
    return 1


def add_ability_selection(update: Update, context: CallbackContext) -> int:
    """
    Stores the choice in the user_data and calls commit_add_ability in the controller that updates the model.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """

    def make_buttons():
        abilities = controller.get_all_abilities(
            chat_id, user_id, context.user_data["add_ability"]["info"]["selection"], pc_name)
        buttons_list = []
        buttons = []
        for i in range(len(abilities)):
            buttons.append(abilities[i])
            if (i + 1) % 8 == 0:
                buttons_list.append(buttons.copy())
                buttons.clear()
        if buttons:
            buttons_list.append(buttons.copy())
        context.user_data["add_ability"]["buttons_list"] = buttons_list
        context.user_data["add_ability"]["query_menu_index"] = 0

        query_menu = context.user_data["add_ability"]["invocation_message"].reply_text(
            placeholders["0"], reply_markup=build_multi_page_kb(buttons_list[0])
        )
        context.user_data["add_ability"]["query_menu"].delete()

        add_tag_in_telegram_data(context, ["add_ability", "query_menu"], query_menu)

    placeholders = get_lang(context, add_ability_selection.__name__)

    query = update.callback_query
    query.answer()
    choice = query.data
    index = context.user_data["add_ability"]["query_menu_index"]

    chat_id = update.effective_message.chat_id
    user_id = get_user_id(update)
    try:
        pc_name = context.user_data["active_PCs"][chat_id]
    except:
        pc_name = None

    if choice == "RIGHT":
        index += 1
        if index >= len(context.user_data["add_ability"]["buttons_list"]):
            index = 0
        context.user_data["add_ability"]["query_menu_index"] = index

    elif choice == "LEFT":
        index -= 1
        if index < -len(context.user_data["add_ability"]["buttons_list"]):
            index = 0
        context.user_data["add_ability"]["query_menu_index"] = index
    else:
        name = choice.split("$")[0]
        if "$" in choice:

            if name.lower() == "veteran":
                make_buttons()
                return 1

            else:
                add_tag_in_telegram_data(context, ["add_ability", "info", "type"], name.lower())
                add_tag_in_telegram_data(context, ["add_ability", "info", "ability"], name)
                controller.commit_add_ability(update.effective_message.chat_id, get_user_id(update),
                                              context.user_data["add_ability"]["info"], pc_name)
                message = context.user_data["add_ability"]["invocation_message"].reply_text(placeholders["1"])
                auto_delete_message(message, placeholders["1"])
                return add_ability_end(update, context)
        else:
            name = name.split(": ")[0]
            if name.lower() == "veteran":
                description = placeholders["3"].format(context.user_data["add_ability"]["info"]["selection"])
            else:
                description = query_special_abilities(special_ability=name, as_dict=True)[0]["description"]
            if description is None:
                description = ""
            info = placeholders["2"].format(name, description)
            auto_delete_message(update.effective_message.reply_text(text=info, quote=False), info)
            return 1

    context.user_data["add_ability"]["query_menu"].edit_text(
        placeholders["0"],
        reply_markup=build_multi_page_kb(
            context.user_data["add_ability"]["buttons_list"][context.user_data["add_ability"]["query_menu_index"]]))
    return 1


def add_ability_end(update: Update, context: CallbackContext) -> int:
    """
    Ends the add ability  conversation and deletes all the saved information from the user_data.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: ConversationHandler.END
    """
    delete_conv_from_telegram_data(context, "downtime", "chat")

    return end_conv(update, context)


# ------------------------------------------conv_addAbility-------------------------------------------------------------


# ------------------------------------------conv_addHarmCohort----------------------------------------------------------


def add_harm_cohort(update: Update, context: CallbackContext) -> int:
    """
    Checks if the user is in the correct phase and starts the conversation that handles the adding of harm to a cohort.
    Adds the dict "harm_cohort" in user_data.
    Finally, sends the inline keyboard to choose the cohort.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """

    placeholders = get_lang(context, add_harm_cohort.__name__)
    if is_game_in_wrong_phase(update, context, placeholders["err"]):
        return add_harm_cohort_end(update, context)

    add_tag_in_telegram_data(context, ["harm_cohort", "invocation_message"], update.message)

    cohorts = controller.get_cohorts_of_crew(update.message.chat_id, get_user_id(update))
    if not cohorts:
        message = context.user_data["harm_cohort"]["invocation_message"].reply_text(placeholders["err2"])
        auto_delete_message(message, 15)
        return add_harm_cohort_end(update, context)
    cohorts = ["{}: {}".format(cohort[0], cohort[1]) for cohort in cohorts]
    callbacks = [i + 1 for i in range(len(cohorts))]
    message = context.user_data["harm_cohort"]["invocation_message"].reply_text(
        placeholders["0"], reply_markup=custom_kb(cohorts, True, 1, callbacks))
    add_tag_in_telegram_data(context, ["harm_cohort", "message"], message)

    return 0


def add_harm_cohort_choice(update: Update, context: CallbackContext) -> int:
    """
    Stores the chosen cohort and send the request of the harm, then advances the conversation.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, add_harm_cohort_choice.__name__)
    context.user_data["harm_cohort"]["message"].delete()

    query = update.callback_query
    query.answer()
    choice = int(query.data) - 1

    add_tag_in_telegram_data(context, ["harm_cohort", "info", "cohort"], choice)

    message = context.user_data["harm_cohort"]["invocation_message"].reply_text(placeholders["0"], ParseMode.HTML)
    add_tag_in_telegram_data(context, ["harm_cohort", "message"], message)
    return 1


def add_harm_cohort_level(update: Update, context: CallbackContext) -> int:
    """
    If the user writes a valid value, calls the controller method commit_add_cohort_harm, then calls add_harm_cohort_end.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: call to add_harm_cohort_end
    """

    placeholders = get_lang(context, add_harm_cohort_level.__name__)
    context.user_data["harm_cohort"]["message"].delete()

    try:
        harm = int(update.message.text)
    except:
        message = context.user_data["harm_cohort"]["invocation_message"].reply_text(placeholders["err"], ParseMode.HTML)
        add_tag_in_telegram_data(context, ["harm_cohort", "message"], message)
        update.message.delete()
        return 1

    add_tag_in_telegram_data(context, ["harm_cohort", "info", "harm"], harm)

    controller.commit_add_cohort_harm(query_game_of_user(update.message.chat_id, get_user_id(update)),
                                      context.user_data["harm_cohort"]["info"])
    return add_harm_cohort_end(update, context)


def add_harm_cohort_end(update: Update, context: CallbackContext) -> int:
    """
    Ends the add harm cohort conversation and deletes all the saved information from the user_data.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: ConversationHandler.END
    """
    delete_conv_from_telegram_data(context, "harm_cohort")

    return end_conv(update, context)


# ------------------------------------------conv_addHarmCohort----------------------------------------------------------


# ------------------------------------------conv_addHarm----------------------------------------------------------------


def add_harm(update: Update, context: CallbackContext) -> int:
    """
    Checks if the user is in the correct phase and starts the conversation that handles the adding of harm to the PC.
    Adds the dict "add_harm" in user_data.
    Finally, sends the request of the harm's description

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """

    placeholders = get_lang(context, add_harm.__name__)
    if is_game_in_wrong_phase(update, context, placeholders["err"]):
        return add_harm_end(update, context)

    chat_id = update.message.chat_id
    if "active_PCs" not in context.user_data or chat_id not in context.user_data["active_PCs"]:
        update.message.reply_text(placeholders["err2"], parse_mode=ParseMode.HTML)
        return add_harm_end(update, context)

    add_tag_in_telegram_data(context, ["add_harm", "invocation_message"], update.message)

    add_tag_in_telegram_data(context, ["add_harm", "info", "pc"], context.user_data["active_PCs"][chat_id])
    message = context.user_data["add_harm"]["invocation_message"].reply_text(placeholders["0"])
    add_tag_in_telegram_data(context, ["add_harm", "message"], message)

    return 0


def add_harm_description(update: Update, context: CallbackContext) -> int:
    """
    Stores the chosen cohort and send the request of the harm, then advances the conversation.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, add_harm_description.__name__)
    context.user_data["add_harm"]["message"].delete()

    add_tag_in_telegram_data(context, ["add_harm", "info", "description"], update.message.text)

    message = context.user_data["add_harm"]["invocation_message"].reply_text(
        placeholders["0"], ParseMode.HTML,
        reply_markup=custom_kb(placeholders["keyboard"], True, 1, placeholders["callbacks"]))
    add_tag_in_telegram_data(context, ["add_harm", "message"], message)

    update.message.delete()
    return 1


def add_harm_level(update: Update, context: CallbackContext) -> int:
    """
    Stores the selected level then, calls the controller method commit_add_cohort_harm, then calls add_harm_cohort_end.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: call to add_harm_cohort_end
    """
    placeholders = get_lang(context, add_harm_level.__name__)
    context.user_data["add_harm"]["message"].delete()

    query = update.callback_query
    query.answer()
    choice = query.data

    add_tag_in_telegram_data(context, ["add_harm", "info", "level"], choice)

    level = controller.commit_add_harm(update.effective_message.chat_id, get_user_id(update),
                                       context.user_data["add_harm"]["info"])
    if level is not None:
        if level == 4:
            message = context.user_data["add_harm"]["invocation_message"].reply_text(
                placeholders["1"].format(level), ParseMode.HTML)
        else:
            message = context.user_data["add_harm"]["invocation_message"].reply_text(
                placeholders["0"].format(level), ParseMode.HTML)
        auto_delete_message(message, 15)
    return add_harm_end(update, context)


def add_harm_end(update: Update, context: CallbackContext) -> int:
    """
    Ends the add harm conversation and deletes all the saved information from the user_data.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: ConversationHandler.END
    """
    delete_conv_from_telegram_data(context, "add_harm", "chat")

    return end_conv(update, context)


# ------------------------------------------conv_addHarm----------------------------------------------------------------

# ------------------------------------------conv_migratePC--------------------------------------------------------------

def migrate_pc(update: Update, context: CallbackContext) -> int:
    """
    Handles the conversation to migrate character type.
    Checks if the user has an active PC for the game in this chat.
    Gets from the controller the PC's type to give the users the possible choices of the new PC.
    Stores in the user_data the name of the PC and sends the InlineKeyboard with the possible choices.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, migrate_pc.__name__)
    chat_id = update.effective_message.chat_id

    if "active_PCs" not in context.user_data or (
            "active_PCs" in context.user_data and chat_id not in context.user_data["active_PCs"]):
        auto_delete_message(update.effective_message.reply_text(placeholders["err"]))
        return migrate_pc_end(update, context)

    add_tag_in_telegram_data(context, tags=["migrate_pc", "invocation_message"], value=update.message)
    pc_name = context.user_data["active_PCs"][chat_id]

    add_tag_in_telegram_data(context, tags=["migrate_pc", "info", "pc"], value=pc_name)

    pc_type = controller.get_pc_type(chat_id, get_user_id(update), pc_name)

    if pc_type == "Ghost":
        message = update.effective_message.reply_text(placeholders["0"], parse_mode=ParseMode.HTML,
                                                      reply_markup=custom_kb(
                                                          placeholders["GhostKeyboard"], inline=True,
                                                          callback_data=placeholders["GhostCallbacks"]))
    else:
        message = update.effective_message.reply_text(placeholders["1"].format(pc_type), parse_mode=ParseMode.HTML,
                                                      reply_markup=custom_kb(
                                                          placeholders["OthersKeyboard"], inline=True,
                                                          callback_data=placeholders["OthersCallbacks"]))
    add_tag_in_telegram_data(context, tags=["migrate_pc", "message"], value=message)

    return 0


def migrate_pc_selection(update: Update, context: CallbackContext) -> int:
    """
    Stores the user's selection in the user_data and calls the controller method to apply the migration process.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, migrate_pc_selection.__name__)
    context.user_data["migrate_pc"]["message"].delete()

    query = update.callback_query
    query.answer()
    choice = query.data

    add_tag_in_telegram_data(context, tags=["migrate_pc", "info", "migration_pc"], value=choice)

    if choice == "Vampire":
        controller.commit_pc_migration(update.effective_message.chat_id, get_user_id(update),
                                       context.user_data["migrate_pc"]["info"])

        auto_delete_message(context.user_data["migrate_pc"]["invocation_message"].reply_text(
            placeholders["0"].format(context.user_data["migrate_pc"]["info"]["pc"], placeholders[choice]),
            parse_mode=ParseMode.HTML), 10)

        return migrate_pc_end(update, context)
    elif choice == "Ghost":
        # enemies
        message = context.user_data["migrate_pc"]["invocation_message"].reply_text(placeholders[choice],
                                                                         parse_mode=ParseMode.HTML,
                                                                         reply_markup=custom_kb(
                                                                             controller.get_game_npcs(
                                                                                 query_game_of_user(
                                                                                     update.effective_message.chat_id,
                                                                                     get_user_id(update)))))
        add_tag_in_telegram_data(context, tags=["migrate_pc", "message"], value=message)
        add_tag_in_telegram_data(context, tags=["migrate_pc", "info", "ghost_enemies"], value=[])
        return 1
    elif choice == "Hull":
        # functions RK
        message = context.user_data["migrate_pc"]["invocation_message"].reply_text(placeholders[choice],
                                                                         parse_mode=ParseMode.HTML,
                                                                         reply_markup=custom_kb(
                                                                             placeholders["functions"]))
        add_tag_in_telegram_data(context, tags=["migrate_pc", "message"], value=message)
        add_tag_in_telegram_data(context, tags=["migrate_pc", "info", "hull_functions"], value=[])
        return 2


def migrate_pc_ghost_enemies(update: Update, context: CallbackContext) -> int:
    """
    Handles the selection of ghost enemies. The message is appended to the list of ghost_enemies in the user_data

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: this state of the conversation to let the user add more than one enemy.
    """
    placeholders = get_lang(context, migrate_pc_ghost_enemies.__name__)

    context.user_data["migrate_pc"]["info"]["ghost_enemies"].append(update.effective_message.text)
    context.user_data["migrate_pc"]["message"].delete()

    message = context.user_data["migrate_pc"]["invocation_message"].reply_text(
        placeholders["0"], parse_mode=ParseMode.HTML, reply_markup=custom_kb(
            controller.get_game_npcs(
                query_game_of_user(
                    update.effective_message.chat_id,
                    get_user_id(update)))
        ))
    add_tag_in_telegram_data(context, tags=["migrate_pc", "message"], value=message)
    return 1


def migrate_pc_enemies_selected(update: Update, context: CallbackContext) -> int:
    """
    Fallbacks called when the user has finished to add enemies for the Ghost.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: call to migrate_pc_end().
    """
    placeholders = get_lang(context, migrate_pc_enemies_selected.__name__)
    if "ghost_enemies" in context.user_data["migrate_pc"]["info"] and len(
            context.user_data["migrate_pc"]["info"]["ghost_enemies"]) > 1:
        controller.commit_pc_migration(update.effective_message.chat_id, get_user_id(update),
                                       context.user_data["migrate_pc"]["info"])

        auto_delete_message(context.user_data["migrate_pc"]["invocation_message"].reply_text(
            placeholders["0"].format(context.user_data["migrate_pc"]["info"]["pc"], placeholders["Ghost"]),
            parse_mode=ParseMode.HTML), 10)

        return migrate_pc_end(update, context)


def migrate_pc_hull_functions(update: Update, context: CallbackContext) -> int:
    """
    Handles the selection of the Hull's functions.
    The message is appended to the list of hull_functions in the user_data.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: this state if the user selected less than 3 functions, call to migrate_pc_end() otherwise.
    """
    placeholders = get_lang(context, migrate_pc_hull_functions.__name__)

    context.user_data["migrate_pc"]["info"]["hull_functions"].append(update.effective_message.text)
    context.user_data["migrate_pc"]["message"].delete()

    total_functions = len(context.user_data["migrate_pc"]["info"]["hull_functions"])

    if total_functions < 3:
        message = context.user_data["migrate_pc"]["invocation_message"].reply_text(placeholders["0"].format(
            3 - total_functions))
        add_tag_in_telegram_data(context, tags=["migrate_pc", "message"], value=message)
        return 2

    controller.commit_pc_migration(update.effective_message.chat_id, get_user_id(update),
                                   context.user_data["migrate_pc"]["info"])

    auto_delete_message(context.user_data["migrate_pc"]["invocation_message"].reply_text(
        placeholders["1"].format(context.user_data["migrate_pc"]["info"]["pc"], placeholders["Hull"]),
        parse_mode=ParseMode.HTML), 10)

    return migrate_pc_end(update, context)


def migrate_pc_end(update: Update, context: CallbackContext) -> int:
    """
    Ends the migrate pc conversation and deletes all the saved information from the user_data.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: ConversationHandler.END
    """
    delete_conv_from_telegram_data(context, "migrate_pc")

    return end_conv(update, context)


# ------------------------------------------conv_migratePC--------------------------------------------------------------

def add_reputation(update: Update, context: CallbackContext) -> None:
    """
    Adds the given reputation to the active pc of the user.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    """
    placeholders = get_lang(context, add_reputation.__name__)

    if is_game_in_wrong_phase(update, context, placeholders["err"]):
        return

    chat_id = update.effective_message.chat_id

    try:
        rep = int(context.args[0])
    except (ValueError, IndexError, AttributeError):
        rep = 1

    coins = controller.add_rep_to_crew(query_game_of_user(chat_id, get_user_id(update)), rep)

    if coins is not None:
        auto_delete_message(update.message.reply_text(placeholders["0"].format(coins),
                                                      parse_mode=ParseMode.HTML), 20)

    update.message.reply_text(placeholders["1"].format(rep), ParseMode.HTML)


# ------------------------------------------conv_addArmorCohort---------------------------------------------------------


def add_armor_cohort(update: Update, context: CallbackContext) -> int:
    """
    Checks if the user is in the correct phase and starts the conversation that handles the adding of armor to a cohort.
    Adds the dict "armor_cohort" in user_data.
    Finally, sends the inline keyboard to choose the cohort.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """

    placeholders = get_lang(context, add_armor_cohort.__name__)
    if is_game_in_wrong_phase(update, context, placeholders["err"]):
        return add_armor_cohort_end(update, context)

    add_tag_in_telegram_data(context, ["armor_cohort", "invocation_message"], update.message)

    cohorts = controller.get_cohorts_of_crew(update.message.chat_id, get_user_id(update))
    if not cohorts:
        message = context.user_data["armor_cohort"]["invocation_message"].reply_text(placeholders["err2"])
        auto_delete_message(message, 15)
        return add_armor_cohort_end(update, context)
    cohorts = ["{}: {}".format(cohort[0], cohort[1]) for cohort in cohorts]
    callbacks = [i + 1 for i in range(len(cohorts))]
    message = context.user_data["armor_cohort"]["invocation_message"].reply_text(
        placeholders["0"], reply_markup=custom_kb(cohorts, True, 1, callbacks))
    add_tag_in_telegram_data(context, ["armor_cohort", "message"], message)

    return 0


def add_armor_cohort_choice(update: Update, context: CallbackContext) -> int:
    """
    Stores the chosen cohort and send the request of the harm, then advances the conversation.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, add_armor_cohort_choice.__name__)
    context.user_data["armor_cohort"]["message"].delete()

    query = update.callback_query
    query.answer()
    choice = int(query.data) - 1

    add_tag_in_telegram_data(context, ["armor_cohort", "info", "cohort"], choice)

    message = context.user_data["armor_cohort"]["invocation_message"].reply_text(placeholders["0"], ParseMode.HTML)
    add_tag_in_telegram_data(context, ["armor_cohort", "message"], message)
    return 1


def add_armor_cohort_level(update: Update, context: CallbackContext) -> int:
    """
    If the user writes a valid value, calls the controller method commit_add_cohort_armor, then calls
    add_armor_cohort_end.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: call to add_armor_cohort_end
    """

    placeholders = get_lang(context, add_armor_cohort_level.__name__)
    context.user_data["armor_cohort"]["message"].delete()

    try:
        armor = int(update.message.text)
    except:
        message = context.user_data["armor_cohort"]["invocation_message"].reply_text(placeholders["err"],
                                                                                     ParseMode.HTML)
        add_tag_in_telegram_data(context, ["armor_cohort", "message"], message)
        update.message.delete()
        return 1

    add_tag_in_telegram_data(context, ["armor_cohort", "info", "armor"], armor)

    controller.commit_add_cohort_armor(query_game_of_user(update.message.chat_id, get_user_id(update)),
                                       context.user_data["armor_cohort"]["info"])
    return add_armor_cohort_end(update, context)


def add_armor_cohort_end(update: Update, context: CallbackContext) -> int:
    """
    Ends the add armor cohort conversation and deletes all the saved information from the user_data.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: ConversationHandler.END
    """
    delete_conv_from_telegram_data(context, "add_harm")

    return end_conv(update, context)


# ------------------------------------------conv_addArmorCohort---------------------------------------------------------


# ------------------------------------------conv_changePCClass----------------------------------------------------------

def change_pc_class(update: Update, context: CallbackContext) -> int:
    """
    Handles the conversation to change a character's class.
    Checks if the user has an active PC for the game in this chat.
    Checks if the active PC is a Human.
    Stores in the user_data the name of the PC and sends the ReplyKeyboard with the suggestions.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, change_pc_class.__name__)
    chat_id = update.effective_message.chat_id

    if "active_PCs" not in context.user_data or (
            "active_PCs" in context.user_data and chat_id not in context.user_data["active_PCs"]):
        auto_delete_message(update.effective_message.reply_text(placeholders["err"]))
        return change_pc_class_end(update, context)

    add_tag_in_telegram_data(context, tags=["change_pc_class", "invocation_message"], value=update.message)
    pc_name = context.user_data["active_PCs"][chat_id]

    pc_type = controller.get_pc_type(chat_id, get_user_id(update), pc_name)

    if pc_type != "Human":
        auto_delete_message(update.effective_message.reply_text(placeholders["1"], parse_mode=ParseMode.HTML), 10)
        return change_pc_class_end(update, context)
    else:
        message = update.effective_message.reply_text(placeholders["0"], parse_mode=ParseMode.HTML,
                                                      reply_markup=custom_kb(
                                                          query_character_sheets(canon=True, spirit=False),
                                                          inline=False))
        add_tag_in_telegram_data(context, tags=["change_pc_class", "info", "pc"], value=pc_name)
    add_tag_in_telegram_data(context, tags=["change_pc_class", "message"], value=message)

    return 0


def change_pc_class_selection(update: Update, context: CallbackContext) -> int:
    placeholders = get_lang(context, change_pc_class_selection.__name__)
    context.user_data["change_pc_class"]["message"].delete()

    new_class = update.effective_message.text

    if not exists_character(new_class):
        message = update.effective_message.reply_text(placeholders["0"], parse_mode=ParseMode.HTML,
                                                      reply_markup=custom_kb(
                                                          query_character_sheets(canon=True, spirit=False),
                                                          inline=False))
        add_tag_in_telegram_data(context, tags=["change_pc_class", "message"], value=message)
        return 0

    add_tag_in_telegram_data(context, tags=["change_pc_class", "info", "new_class"], value=new_class)

    controller.commit_change_pc_class(update.effective_message.chat_id, get_user_id(update),
                                      context.user_data["change_pc_class"]["info"])

    auto_delete_message(context.user_data["change_pc_class"]["invocation_message"].reply_text(
        placeholders["1"].format(context.user_data["change_pc_class"]["info"]["pc"], new_class),
        parse_mode=ParseMode.HTML), 10)

    return change_pc_class_end(update, context)


def change_pc_class_end(update: Update, context: CallbackContext) -> int:
    """
    Ends the change PC's class conversation and deletes all the saved information from the user_data.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: ConversationHandler.END
    """
    delete_conv_from_telegram_data(context, "change_pc_class")

    return end_conv(update, context)


# ------------------------------------------conv_changePCClass----------------------------------------------------------

# ------------------------------------------conv_retire-----------------------------------------------------------------


def retire(update: Update, context: CallbackContext) -> int:
    """
    Checks if the user is in the correct phase and starts the conversation that handles the retirement of the PC.
    Adds the dict "retire" in user_data.
    Finally, sends the request of the type of retirement to the user.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, retire.__name__)
    if is_game_in_wrong_phase(update, context, placeholders["err"]):
        return retire_end(update, context)

    chat_id = update.effective_message.chat_id
    if "active_PCs" not in context.user_data or chat_id not in context.user_data["active_PCs"]:
        update.message.reply_text(placeholders["err2"], parse_mode=ParseMode.HTML)
        return add_harm_end(update, context)

    add_tag_in_telegram_data(context, ["retire", "info", "pc"], context.user_data["active_PCs"][chat_id])

    add_tag_in_telegram_data(context, ["retire", "invocation_message"], update.message)

    query_menu = context.user_data["retire"]["invocation_message"].reply_text(
        placeholders["0"], parse_mode=ParseMode.HTML, reply_markup=custom_kb(
            placeholders["keyboard"], inline=True, split_row=1, callback_data=placeholders["callbacks"]))

    add_tag_in_telegram_data(context, ["retire", "query_menu"], query_menu)

    return 0


def retire_choice(update: Update, context: CallbackContext) -> int:
    """
    Stores the selected choice in the user_data, then advances the conversation.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, retire_choice.__name__)

    query = update.callback_query
    query.answer()
    choice = query.data

    add_tag_in_telegram_data(context, ["retire", "info", "choice"], choice)

    context.user_data["retire"]["query_menu"].delete()

    query_menu = context.user_data["retire"]["invocation_message"].reply_text(
        placeholders["0"].format(choice), parse_mode=ParseMode.HTML, reply_markup=custom_kb(
            placeholders["keyboard"], inline=True, split_row=1))

    add_tag_in_telegram_data(context, ["retire", "query_menu"], query_menu)

    return 1


def retire_disclaimer(update: Update, context: CallbackContext) -> int:
    """
    Stores the selected choice in the user_data, then advances the conversation.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, retire_disclaimer.__name__)

    context.user_data["retire"]["query_menu"].delete()

    message = context.user_data["retire"]["invocation_message"].reply_text(
        placeholders["0"].format(context.user_data["retire"]["info"]["choice"]), parse_mode=ParseMode.HTML)

    add_tag_in_telegram_data(context, ["retire", "message"], message)

    return 2


def retire_description(update: Update, context: CallbackContext) -> int:
    """
    Stores the description sent by the user in user_data and calls commit_retire in the controller and calls retire_end.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: calls retire_end.
    """
    placeholders = get_lang(context, retire_description.__name__)

    add_tag_in_telegram_data(context, ["retire", "info", "description"], update.effective_message.text)

    context.user_data["retire"]["message"].delete()

    controller.retire(update.effective_message.chat_id, get_user_id(update), context.user_data["retire"]["info"])

    context.user_data["active_PCs"].pop(update.effective_message.chat_id)

    message = context.user_data["retire"]["invocation_message"].reply_text(placeholders["0"], parse_mode=ParseMode.HTML)

    auto_delete_message(message, 10)

    return retire_end(update, context)


def retire_end(update: Update, context: CallbackContext) -> int:
    """
    Ends the retire conversation and deletes all the saved information from the user_data.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: ConversationHandler.END
    """
    delete_conv_from_telegram_data(context, "retire", "user")

    return end_conv(update, context)


# ------------------------------------------conv_retire-----------------------------------------------------------------


# ------------------------------------------conv_flashback--------------------------------------------------------------


def flashback(update: Update, context: CallbackContext) -> int:
    """
    Checks if the user controls a PC in this chat and starts the conversation of the flashback roll.
    Adds the dict "flashback" in chat_data and stores the ID of the invoker and his active PC in it.
    Finally, sends the goal request.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """

    placeholders = get_lang(context, flashback.__name__)
    if is_game_in_wrong_phase(update, context, placeholders["err"], 3):
        return flashback_end(update, context)

    chat_id = update.effective_message.chat_id
    if "active_PCs" not in context.user_data or chat_id not in context.user_data["active_PCs"]:
        update.message.reply_text(placeholders["err2"], parse_mode=ParseMode.HTML)
        return flashback_end(update, context)

    add_tag_in_telegram_data(context, ["flashback", "invoker"], get_user_id(update), "chat")

    add_tag_in_telegram_data(context, ["flashback", "info", "pc"], context.user_data["active_PCs"][chat_id], "chat")

    add_tag_in_telegram_data(context, ["flashback", "invocation_message"], update.message, "chat")

    message = context.chat_data["flashback"]["invocation_message"].reply_text(
        placeholders["0"], parse_mode=ParseMode.HTML)

    add_tag_in_telegram_data(context, ["flashback", "message"], message, "chat")

    return 0


def flashback_goal(update: Update, context: CallbackContext) -> Optional[int]:
    """
    Stores the goal's description in the chat_data and sends the master the stress request.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: he next state of the conversation.
    """
    placeholders = get_lang(context, flashback_goal.__name__)
    if context.chat_data["flashback"]["invoker"] != get_user_id(update):
        return

    add_tag_in_telegram_data(context, ["flashback", "info", "goal"], update.message.text, "chat")

    message = context.chat_data["flashback"]["invocation_message"].reply_text(
        placeholders["0"].format(context.chat_data["flashback"]["info"]["pc"], update.message.text),
        parse_mode=ParseMode.HTML)

    add_tag_in_telegram_data(context, ["flashback", "message"], message, "chat")

    return 1


def flashback_stress(update: Update, context: CallbackContext) -> Optional[int]:
    """
    Stores the amount of stress to pay selected by the GM and asks him what the flashback will entail.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    if not controller.is_master(get_user_id(update), update.effective_message.chat_id):
        return

    placeholders = get_lang(context, flashback_stress.__name__)
    context.chat_data["flashback"]["message"].delete()
    try:
        stress = int(update.message.text)
    except:
        message = context.chat_data["flashback"]["invocation_message"].reply_text(placeholders["err"], ParseMode.HTML)
        add_tag_in_telegram_data(context, ["flashback", "message"], message, "chat")
        update.message.delete()
        return 1

    add_tag_in_telegram_data(context, ["flashback", "info", "stress"], stress, "chat")

    message = context.chat_data["flashback"]["invocation_message"].reply_text(
        placeholders["0"], ParseMode.HTML,
        reply_markup=custom_kb(placeholders["keyboard"], True, 1, placeholders["callbacks"]))
    add_tag_in_telegram_data(context, ["flashback", "message"], message, "chat")

    return 0


def flashback_entail(update: Update, context: CallbackContext) -> int:
    """
    Stores the entailment selected by the GM, then calls the commit_flashback method of the controller
    and ends the conversation.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, flashback_entail.__name__)

    query = update.callback_query
    query.answer()
    choice = query.data

    if choice == "/actionRoll" or choice == "/fortuneRoll":
        entail = choice == "/actionRoll"
        add_tag_in_telegram_data(context, ["flashback", "info", "entail"], entail, "chat")

        context.chat_data["flashback"]["invocation_message"].reply_text(placeholders["0"].format(choice),
                                                                        ParseMode.HTML)
    else:
        context.chat_data["flashback"]["invocation_message"].reply_text(placeholders["1"], ParseMode.HTML)

    traumas = controller.commit_flashback(update.effective_message.chat_id, context.chat_data["flashback"]["invoker"],
                                          context.chat_data["flashback"]["info"])

    if traumas is not None:
        message = context.chat_data["flashback"]["invocation_message"].reply_text(
            placeholders["2"].format(traumas), ParseMode.HTML)
        auto_delete_message(message, 20)

    return flashback_end(update, context)


def flashback_end(update: Update, context: CallbackContext) -> int:
    """
    Ends the flashback conversation and deletes all the saved information from the user_data.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: ConversationHandler.END
    """
    delete_conv_from_telegram_data(context, "flashback", "user")

    return end_conv(update, context)


# ------------------------------------------conv_flashback--------------------------------------------------------------


# ------------------------------------------conv_incarceration----------------------------------------------------------


def incarceration_roll(update: Update, context: CallbackContext) -> int:
    """
    Handles the conversation of the incarceration roll.
    Adds the dict "incarceration" and sends the inline keyboard used to choose the "target" of the roll: an NPC or the
    active pc of the user (if present).

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, incarceration_roll.__name__)
    if is_game_in_wrong_phase(update, context, placeholders["err"]):
        return incarceration_roll_end(update, context)

    chat_id = update.effective_message.chat_id
    keyboard = placeholders["keyboard"].copy()
    callbacks = placeholders["callbacks"].copy()
    if "active_PCs" not in context.user_data or chat_id not in context.user_data["active_PCs"]:
        keyboard.pop(0)
        callbacks.pop(0)

    add_tag_in_telegram_data(context, ["incarceration", "invocation_message"], update.message)

    message = context.user_data["incarceration"]["invocation_message"].reply_text(
        placeholders["0"], parse_mode=ParseMode.HTML, reply_markup=custom_kb(keyboard, True, 1, callbacks))

    add_tag_in_telegram_data(context, ["incarceration", "message"], message)

    return 0


def incarceration_roll_choice(update: Update, context: CallbackContext) -> int:
    """
    Stores the choice of the user and sends the bonus dice request if the choice was its active pc,
    or the inline keyboard to select the npc for the roll.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, incarceration_roll_choice.__name__)
    context.user_data["incarceration"]["message"].delete()

    query = update.callback_query
    query.answer()
    choice = query.data

    chat_id = update.effective_message.chat_id
    game_id = query_game_of_user(chat_id, get_user_id(update))

    crew_tier = controller.get_crew_tier(game_id)
    add_tag_in_telegram_data(context, ["incarceration", "tier"], crew_tier)

    add_tag_in_telegram_data(context, ["incarceration", "bonus_dice"], 0)

    # Active PC
    if choice == 1:
        add_tag_in_telegram_data(context, ["incarceration", "roll", "type"], "pc")
        placeholders = get_lang(context, "bonus_dice")
        add_tag_in_telegram_data(context, ["incarceration", "roll", "pc"],
                                 context.user_data["active_PCs"][chat_id])
        query_menu = context.user_data["incarceration"]["invocation_message"].reply_text(
            placeholders["message"].format(crew_tier), parse_mode=ParseMode.HTML,
            reply_markup=build_plus_minus_keyboard(
                [placeholders["button"].format(0)], done_button=True, back_button=False))

        add_tag_in_telegram_data(context, ["incarceration", "query_menu"], query_menu)
        return 2
    # NPC
    else:
        add_tag_in_telegram_data(context, ["incarceration", "roll", "type"], "npc")
        npcs = controller.get_npcs_contacts(game_id)
        buttons_list = []
        buttons = []
        for i in range(len(npcs)):
            buttons.append(npcs[i])
            if (i + 1) % 5 == 0:
                buttons_list.append(buttons.copy())
                buttons.clear()
        if buttons:
            buttons_list.append(buttons.copy())
        add_tag_in_telegram_data(context, tags=["incarceration", "buttons_list"], value=buttons_list)
        add_tag_in_telegram_data(context, tags=["incarceration", "query_menu_index"], value=0)

        context.user_data["incarceration"]["query_menu"] = \
            context.user_data["incarceration"]["invocation_message"].reply_text(placeholders["0"],
                                                                                parse_mode=ParseMode.HTML,
                                                                                reply_markup=build_multi_page_kb(
                                                                                    buttons_list[0]))
        return 1


def incarceration_roll_npc(update: Update, context: CallbackContext) -> int:
    """
    Stores the npc selected and sends the bonus dice request.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, incarceration_roll_npc.__name__)

    query = update.callback_query
    query.answer()

    choice = query.data
    index = context.user_data["incarceration"]["query_menu_index"]

    if choice == "RIGHT":
        index += 1
        if index >= len(context.user_data["incarceration"]["buttons_list"]):
            index = 0
        context.user_data["incarceration"]["query_menu_index"] = index

    elif choice == "LEFT":
        index -= 1
        if index == -len(context.user_data["incarceration"]["buttons_list"]):
            index = 0

        context.user_data["incarceration"]["query_menu_index"] = index
    else:
        name = choice.split("$")[0]
        if "$" in choice:
            placeholders = get_lang(context, "bonus_dice")
            add_tag_in_telegram_data(context, tags=["incarceration", "roll", "pc"], value=name)
            context.user_data["incarceration"]["query_menu"].delete()
            query_menu = context.user_data["incarceration"]["invocation_message"].reply_text(
                placeholders["message"].format(context.user_data["incarceration"]["tier"]),
                parse_mode=ParseMode.HTML,
                reply_markup=build_plus_minus_keyboard(
                    [placeholders["button"].format(0)], done_button=True, back_button=False))

            add_tag_in_telegram_data(context, ["incarceration", "query_menu"], query_menu)
            return 2
        else:
            npc_name = name.split(", ")[0]
            npc_role = name.split(", ")[1]
            description = query_npcs(name=npc_name,
                                     role=npc_role, as_dict=True)[0]["description"]

            if description is None or description == "":
                description = placeholders["404"]
            auto_delete_message(update.effective_message.reply_text(
                text=description, quote=False), description)
            return 1

    context.user_data["incarceration"]["query_menu"].edit_text(
        placeholders["0"], reply_markup=build_multi_page_kb(
            context.user_data["incarceration"]["buttons_list"][context.user_data["incarceration"]["query_menu_index"]]))
    return 1


def incarceration_roll_bonus_dice(update: Update, context: CallbackContext) -> int:
    """
    Handles the addition or removal of bonus dice and updates the related Keyboard.
    When the user confirms, the number of dice to roll is passed to roll_dice method.
    Then, the outcome is stored in the user_data and the final description request is sent.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation when the "DONE" button is pressed.
    """
    placeholders = get_lang(context, incarceration_roll_bonus_dice.__name__)

    query = update.callback_query
    query.answer()

    bonus_dice = context.user_data["incarceration"]["bonus_dice"]
    tier = context.user_data["incarceration"]["tier"]

    choice = query.data
    if "+" in choice or "-" in choice:
        tags = ["incarceration", "bonus_dice"]
        bonus_dice += int(choice.split(" ")[2])
        add_tag_in_telegram_data(context, tags=tags, value=bonus_dice)

        update_bonus_dice_kb(context, tags, bonus_dice + tier, "user")

    elif choice == "DONE":
        dice_to_roll = bonus_dice + tier

        context.user_data["incarceration"]["query_menu"].delete()

        roll_dice(update, context, dice_to_roll, ["incarceration", "roll", "outcome"], "user")

        context.user_data["incarceration"]["message"] = \
            context.user_data["incarceration"]["invocation_message"].reply_text(
                placeholders["0"], parse_mode=ParseMode.HTML)
        return 3

    else:
        bonus_dice_lang = get_lang(context, "bonus_dice")
        auto_delete_message(update.effective_message.reply_text(bonus_dice_lang["extended"], parse_mode=ParseMode.HTML),
                            bonus_dice_lang["extended"])

    return 2


def incarceration_roll_notes(update: Update, context: CallbackContext) -> int:
    """
    Stores the final description of the incarceration roll in the user_data,
    calls the controller method to apply the roll's
    effects and eventually sends the notification about the effect of thhe roll.
    Finally, calls resistance_roll_end.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: call to incarceration_roll_end
    """
    placeholders = get_lang(context, incarceration_roll_notes.__name__)

    add_tag_in_telegram_data(context, ["incarceration", "roll", "notes"], update.message.text)

    return_dict = controller.commit_incarceration_roll(query_game_of_user(update.message.chat_id, get_user_id(update)),
                                                       context.user_data["incarceration"]["roll"])
    for key in return_dict.keys():
        context.user_data["incarceration"]["invocation_message"].reply_text(
            placeholders[str(key)].format(return_dict[key]), ParseMode.HTML)

    return incarceration_roll_end(update, context)


def incarceration_roll_end(update: Update, context: CallbackContext) -> int:
    """
    Ends the incarceration roll conversation and deletes all the saved information from the user_data.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: ConversationHandler.END
    """
    delete_conv_from_telegram_data(context, "incarceration", "user")

    return end_conv(update, context)


# ------------------------------------------conv_incarceration----------------------------------------------------------


# ------------------------------------------conv_addNote----------------------------------------------------------------


def add_note(update: Update, context: CallbackContext) -> int:
    """
    Send the user the request for the title of the note.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, add_note.__name__)

    add_tag_in_telegram_data(context, ["add_note", "invocation_message"], update.effective_message)

    message = update.effective_message.reply_text(placeholders["0"])

    add_tag_in_telegram_data(context, ["add_note", "message"], message)

    return 0


def add_note_title(update: Update, context: CallbackContext) -> int:
    """
    Stores the title in the user data and asks the user for the text of the note.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, add_note_title.__name__)

    add_tag_in_telegram_data(context, ["add_note", "info", "title"], update.effective_message.text)

    context.user_data["add_note"]["message"].delete()
    update.message.delete()

    message = context.user_data["add_note"]["invocation_message"].reply_text(placeholders["0"])

    add_tag_in_telegram_data(context, ["add_note", "message"], message)

    return 1


def add_note_text(update: Update, context: CallbackContext) -> int:
    """
    Stores the text of the not in the user data and calls commit_add_note.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: add_note_end
    """

    add_tag_in_telegram_data(context, ["add_note", "info", "text"], update.effective_message.text)

    context.user_data["add_note"]["message"].delete()

    controller.commit_add_note(
        update.effective_message.chat_id, get_user_id(update), context.user_data["add_note"]["info"])

    return add_note_end(update, context)


def add_note_end(update: Update, context: CallbackContext) -> int:
    """
    Ends the add note conversation and deletes all the saved information from the user_data.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: ConversationHandler.END
    """
    delete_conv_from_telegram_data(context, "add_note", "user")

    return end_conv(update, context)


# ------------------------------------------conv_addNote----------------------------------------------------------------


# ------------------------------------------conv_editNote---------------------------------------------------------------


def edit_note(update: Update, context: CallbackContext) -> int:
    """
    Asks the user for the position of the note that will be modified.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, edit_note.__name__)

    add_tag_in_telegram_data(context, ["edit_note", "invocation_message"], update.effective_message)

    message = update.effective_message.reply_text(placeholders["0"])

    add_tag_in_telegram_data(context, ["edit_note", "message"], message)

    return 0


def edit_note_position(update: Update, context: CallbackContext) -> int:
    """
    Save the position in the user data, displays the chosen note and asks the user if it's the right note.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, edit_note_position.__name__)

    position = update.effective_message.text

    try:
        if int(position) <= 0:
            message = context.user_data["edit_note"]["invocation_message"].reply_text(placeholders["err"])
            auto_delete_message(message, placeholders["err"])
            return 0
    except:
        message = context.user_data["edit_note"]["invocation_message"].reply_text(placeholders["err1"])
        auto_delete_message(message, placeholders["err"])
        return 0

    position = int(position)

    context.user_data["edit_note"]["message"].delete()
    update.message.delete()

    add_tag_in_telegram_data(context, ["edit_note", "info", "number"], position)

    note = controller.get_note(update.effective_message.chat_id, get_user_id(update), position)

    if note is None:
        message = context.user_data["edit_note"]["invocation_message"].reply_text(placeholders["err2"])
        auto_delete_message(message, placeholders["err2"])
        return 0

    query_menu = context.user_data["edit_note"]["invocation_message"].reply_text(
        placeholders["0"].format(note), reply_markup=custom_kb(placeholders["keyboard"], inline=True,
                                                               callback_data=placeholders["callback"]),
        parse_mode=ParseMode.HTML)

    add_tag_in_telegram_data(context, ["edit_note", "query_menu"], query_menu)

    return 1


def edit_note_correct(update: Update, context: CallbackContext) -> int:
    """
    If the position is correct asks for the text, otherwise end the conversation.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, edit_note_correct.__name__)

    query = update.callback_query
    query.answer()
    choice = query.data

    context.user_data["edit_note"]["query_menu"].delete()

    if choice == "No":
        return edit_note_end(update, context)

    message = context.user_data["edit_note"]["invocation_message"].reply_text(placeholders["0"])

    add_tag_in_telegram_data(context, ["edit_note", "message"], message)

    return 2


def edit_note_text(update: Update, context: CallbackContext) -> int:
    """
    Stores the new text of the note in the user data, calls commit_edit_note and ends the conversation.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: calls edit_note_end
    """
    add_tag_in_telegram_data(context, ["edit_note", "info", "new_note"], update.effective_message.text)

    context.user_data["edit_note"]["message"].delete()

    controller.commit_edit_note(
        update.effective_message.chat_id, get_user_id(update), context.user_data["edit_note"]["info"])

    return edit_note_end(update, context)


def edit_note_end(update: Update, context: CallbackContext) -> int:
    """
    Ends the edit note conversation and deletes all the saved information from the user_data.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: ConversationHandler.END
    """
    delete_conv_from_telegram_data(context, "edit_note", "user")

    return end_conv(update, context)


# ------------------------------------------conv_editNote---------------------------------------------------------------


# ------------------------------------------conv_endGame----------------------------------------------------------------


def end_game(update: Update, context: CallbackContext) -> int:
    """
    Starts the conversation to end a game and sends the user the inline keyboard to verify their intention.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, end_game.__name__)

    add_tag_in_telegram_data(context, ["end_game", "invocation_message"], update.message)

    message = update.message.reply_text(placeholders["0"], ParseMode.HTML, reply_markup=custom_kb(
        placeholders["keyboard"], True, 1, placeholders["callbacks"]))

    add_tag_in_telegram_data(context, ["end_game", "message"], message)

    return 0


def end_game_choice(update: Update, context: CallbackContext) -> int:
    """
    If the users it's confident the request of the final notes is sent; the conversation is ended otherwise

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, end_game_choice.__name__)

    query = update.callback_query
    query.answer()
    choice = query.data

    if choice == 2:
        return end_game_end(update, context)

    context.user_data["end_game"]["message"].delete()

    message = context.user_data["end_game"]["invocation_message"].reply_text(placeholders["0"], ParseMode.HTML)

    add_tag_in_telegram_data(context, ["end_game", "message"], message)

    return 1


def end_game_notes(update: Update, context: CallbackContext) -> int:
    """
    Calls the controller method end game, then ends the conversation after sending all the game files to the user
    using a separate thread.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, end_game_notes.__name__)
    context.user_data["end_game"]["message"].delete()

    game_obj = controller.end_game(
        query_game_of_user(update.effective_message.chat_id, get_user_id(update)), update.message.text)

    context.user_data["end_game"]["invocation_message"].reply_text(placeholders["0"], ParseMode.HTML)

    def execute() -> None:
        for obj in game_obj:
            context.bot.send_document(update.effective_message.chat_id, obj[0], obj[1])
            time.sleep(3)

    t = Thread(target=execute)
    t.start()

    update.message.delete()
    return end_game_end(update, context)


def end_game_end(update: Update, context: CallbackContext) -> int:
    """
    Ends the end game conversation and deletes all the saved information from the user_data.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: ConversationHandler.END
    """
    delete_conv_from_telegram_data(context, "end_game", "user")

    return end_conv(update, context)


# ------------------------------------------conv_endGame----------------------------------------------------------------


# ------------------------------------------conv_change_frame_size------------------------------------------------------


def change_frame_size(update: Update, context: CallbackContext) -> int:
    """
    Starts the conversation to change the frame size and sends the user the inline keyboard with the options if
    their active pc is an Hull.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, change_frame_size.__name__)

    chat_id = update.message.chat_id

    if "active_PCs" not in context.user_data or chat_id not in context.user_data["active_PCs"]:
        auto_delete_message(update.message.reply_text(placeholders["err"], ParseMode.HTML))
        return change_frame_size_end(update, context)

    pc_name = context.user_data["active_PCs"][chat_id]
    if controller.get_pc_type(chat_id, get_user_id(update), pc_name) != "Hull":
        auto_delete_message(update.message.reply_text(placeholders["err2"], ParseMode.HTML))
        return change_frame_size_end(update, context)

    add_tag_in_telegram_data(context, ["frame_size", "invocation_message"], update.message)

    add_tag_in_telegram_data(context, ["frame_size", "pc"], pc_name)

    message = update.message.reply_text(placeholders["0"], ParseMode.HTML, reply_markup=custom_kb(
        placeholders["keyboard"], True, 1, placeholders["callbacks"]))

    add_tag_in_telegram_data(context, ["frame_size", "message"], message)

    return 0


def change_frame_size_choice(update: Update, context: CallbackContext) -> int:
    """
    If the users it's confident the request of the final notes is sent; the conversation is ended otherwise

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    query = update.callback_query
    query.answer()
    choice = query.data

    controller.commit_change_frame_size(update.effective_message.chat_id, get_user_id(update),
                                        context.user_data["frame_size"]["pc"], choice)

    return change_frame_size_end(update, context)


def change_frame_size_end(update: Update, context: CallbackContext) -> int:
    """
    Ends the end change frame size end and deletes all the saved information from the user_data.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: ConversationHandler.END
    """
    delete_conv_from_telegram_data(context, "frame_size", "user")

    return end_conv(update, context)


# ------------------------------------------conv_change_frame_size------------------------------------------------------


# ------------------------------------------conv_addTypeCohort----------------------------------------------------------


def add_type_cohort(update: Update, context: CallbackContext) -> int:
    """
    Checks if the user is in the correct phase and starts the conversation that handles the adding of type to a cohort.
    Adds the dict "type_cohort" in user_data.
    Finally, sends the inline keyboard to choose the cohort.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """

    placeholders = get_lang(context, add_type_cohort.__name__)
    if is_game_in_wrong_phase(update, context, placeholders["err"]):
        return add_type_cohort_end(update, context)

    if controller.get_crew_upgrade_points(query_game_of_user(update.message.chat_id, get_user_id(update))) < 2:
        message = update.message.reply_text(placeholders["err2"])
        auto_delete_message(message, 15)
        return add_type_cohort_end(update, context)

    add_tag_in_telegram_data(context, ["type_cohort", "invocation_message"], update.message)

    cohorts = controller.get_cohorts_of_crew(update.message.chat_id, get_user_id(update))
    if not cohorts:
        message = context.user_data["type_cohort"]["invocation_message"].reply_text(placeholders["err3"])
        auto_delete_message(message, 15)
        return add_type_cohort_end(update, context)
    cohorts = ["{}: {}".format(cohort[0], cohort[1]) for cohort in cohorts]
    callbacks = [(cohorts[i], i + 1) for i in range(len(cohorts))]
    message = context.user_data["type_cohort"]["invocation_message"].reply_text(
        placeholders["0"], reply_markup=custom_kb(cohorts, True, 1, callbacks))
    add_tag_in_telegram_data(context, ["type_cohort", "message"], message)

    return 0


def add_type_cohort_choice(update: Update, context: CallbackContext) -> int:
    """
    Stores the chosen cohort and send the request of the new type to add, then advances the conversation.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, add_type_cohort_choice.__name__)
    context.user_data["type_cohort"]["message"].delete()

    query = update.callback_query
    query.answer()
    choice = int(query.data[1]) - 1
    cohort_type = query.data[0].split("[")[1]
    cohort_type = cohort_type.split("]")[0]

    add_tag_in_telegram_data(context, ["type_cohort", "info", "cohort"], choice)

    message = context.user_data["type_cohort"]["invocation_message"].reply_text(
        placeholders["0"], ParseMode.HTML, reply_markup=custom_kb(
            placeholders["keyboard_{}".format(cohort_type.lower())]))
    add_tag_in_telegram_data(context, ["type_cohort", "message"], message)
    return 1


def add_type_cohort_type(update: Update, context: CallbackContext) -> int:
    """
    Calls the controller method commit_add_cohort_type, then calls
    add_type_cohort_end.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: call to add_type_cohort_end
    """
    context.user_data["type_cohort"]["message"].delete()

    add_tag_in_telegram_data(context, ["type_cohort", "info", "type"], update.message.text)

    controller.commit_add_cohort_type(query_game_of_user(update.message.chat_id, get_user_id(update)),
                                      context.user_data["type_cohort"]["info"])
    return add_type_cohort_end(update, context)


def add_type_cohort_end(update: Update, context: CallbackContext) -> int:
    """
    Ends the add type cohort conversation and deletes all the saved information from the user_data.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: ConversationHandler.END
    """
    delete_conv_from_telegram_data(context, "type_cohort")

    return end_conv(update, context)


# ------------------------------------------conv_addTypeCohort----------------------------------------------------------


# ------------------------------------------conv_addDarkServant---------------------------------------------------------


def add_servant(update: Update, context: CallbackContext) -> int:
    """
    Checks if the user is in the correct phase and starts the conversation that handles the adding of a servant.
    Adds the dict "add_servant" in user_data.
    Finally, sends the inline keyboard to choose the servant.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """

    placeholders = get_lang(context, add_servant.__name__)
    if is_game_in_wrong_phase(update, context, placeholders["err"]):
        return add_servant_end(update, context)

    chat_id = update.message.chat_id
    if "active_PCs" not in context.user_data or chat_id not in context.user_data["active_PCs"]:
        auto_delete_message(update.message.reply_text(placeholders["err2"], ParseMode.HTML), 15)
        return add_servant_end(update, context)

    pc_name = context.user_data["active_PCs"][chat_id]

    if controller.get_pc_type(chat_id, get_user_id(update), pc_name) != "Vampire":
        auto_delete_message(update.message.reply_text(placeholders["err3"], ParseMode.HTML), 15)
        return add_servant_end(update, context)

    add_tag_in_telegram_data(context, ["add_servant", "info", "pc"], pc_name)

    add_tag_in_telegram_data(context, ["add_servant", "invocation_message"], update.message)

    npcs = [npc["name"] + ", " + npc["role"] for npc in query_char_strange_friends("Vampire", as_dict=True)]

    query_menu = context.user_data["add_servant"]["invocation_message"].reply_text(
        placeholders["0"], reply_markup=custom_kb(npcs, True, 1))
    add_tag_in_telegram_data(context, ["add_servant", "query_menu"], query_menu)

    return 0


def add_servant_choice(update: Update, context: CallbackContext) -> int:
    """
    Stores the information about the servant in the user_data, then calls the controller method add_servant.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: calls add_servant_end.
    """
    query = update.callback_query
    query.answer()
    choice = query.data

    add_tag_in_telegram_data(context, ["add_servant", "info", "servant"], choice)

    controller.add_servant(update.effective_message.chat_id, get_user_id(update),
                           context.user_data["add_servant"]["info"])

    return add_servant_end(update, context)


def add_servant_end(update: Update, context: CallbackContext) -> int:
    """
    Ends the add servant conversation and deletes all the saved information from the user_data.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: ConversationHandler.END
    """
    delete_conv_from_telegram_data(context, "add_servant")

    return end_conv(update, context)


# ------------------------------------------conv_addDarkServant---------------------------------------------------------


# ------------------------------------------conv_createSpecialAbility---------------------------------------------------


def create_sa(update: Update, context: CallbackContext) -> int:
    """
    Starts the conversation that handles the creation of a new special ability and ask the user the name of it.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """

    placeholders = get_lang(context, create_sa.__name__)

    add_tag_in_telegram_data(context, ["create_sa", "invocation_message"], update.message)

    message = context.user_data["create_sa"]["invocation_message"].reply_text(placeholders["0"], ParseMode.HTML)
    add_tag_in_telegram_data(context, ["create_sa", "message"], message)

    return 0


def create_sa_name(update: Update, context: CallbackContext) -> int:
    """
    Stores the information about the special ability name in the user_data, then asks for the description.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, create_sa_name.__name__)
    context.user_data["create_sa"]["message"].delete()

    name = update.message.text
    if name in [sa["name"] for sa in query_special_abilities(as_dict=True)]:
        message = context.user_data["create_sa"]["invocation_message"].reply_text(placeholders["err"], ParseMode.HTML)
        add_tag_in_telegram_data(context, ["create_sa", "message"], message)
        return 0

    add_tag_in_telegram_data(context, ["create_sa", "info", "name"], name)

    message = context.user_data["create_sa"]["invocation_message"].reply_text(placeholders["0"], ParseMode.HTML)
    add_tag_in_telegram_data(context, ["create_sa", "message"], message)

    update.message.delete()
    return 1


def create_sa_description(update: Update, context: CallbackContext) -> int:
    """
    Stores the information about the description in the user_data, then adds the new special ability to the database.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: calls create_sa_end.
    """
    placeholders = get_lang(context, create_sa_description.__name__)
    context.user_data["create_sa"]["message"].delete()

    add_tag_in_telegram_data(context, ["create_sa", "info", "description"], update.message.text)

    insert_special_ability(**context.user_data["create_sa"]["info"])

    message = context.user_data["create_sa"]["invocation_message"].reply_text(placeholders["0"], ParseMode.HTML)
    auto_delete_message(message, 10)

    return create_sa_end(update, context)


def create_sa_end(update: Update, context: CallbackContext) -> int:
    """
    Ends the creation of the creation of a special ability conversation and
    deletes all the saved information from the user_data.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: ConversationHandler.END
    """
    delete_conv_from_telegram_data(context, "create_sa")

    return end_conv(update, context)


# ------------------------------------------conv_createSpecialAbility---------------------------------------------------


# ------------------------------------------conv_createXpTrigger--------------------------------------------------------


def create_xp_trigger(update: Update, context: CallbackContext) -> int:
    """
    Starts the conversation that handles the creation of a new special ability and ask the user the name of it.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """

    placeholders = get_lang(context, create_xp_trigger.__name__)

    add_tag_in_telegram_data(context, ["create_xp_trigger", "invocation_message"], update.message)

    message = context.user_data["create_xp_trigger"]["invocation_message"].reply_text(placeholders["0"], ParseMode.HTML)
    add_tag_in_telegram_data(context, ["create_xp_trigger", "message"], message)

    return 0


def create_xp_trigger_name(update: Update, context: CallbackContext) -> int:
    """
    Stores the information about the xp trigger description in the user_data,
    then asks if is a trigger for a crew or not.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, create_xp_trigger_name.__name__)
    context.user_data["create_xp_trigger"]["message"].delete()

    add_tag_in_telegram_data(context, ["create_xp_trigger", "info", "description"], update.message.text)

    message = context.user_data["create_xp_trigger"]["invocation_message"].reply_text(
        placeholders["0"], ParseMode.HTML,
        reply_markup=custom_kb(placeholders["keyboard"], True, 1, placeholders["callbacks"]))
    add_tag_in_telegram_data(context, ["create_xp_trigger", "message"], message)

    update.message.delete()
    return 1


def create_xp_trigger_crew_char(update: Update, context: CallbackContext) -> int:
    """
    Stores the information in the user_data, then adds the new xp trigger to the database.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, create_xp_trigger_crew_char.__name__)
    context.user_data["create_xp_trigger"]["message"].delete()

    query = update.callback_query
    query.answer()
    choice = query.data

    add_tag_in_telegram_data(context, ["create_xp_trigger", "info", "crew_char"], choice == 1)

    insert_xp_trigger(**context.user_data["create_xp_trigger"]["info"])

    message = context.user_data["create_xp_trigger"]["invocation_message"].reply_text(placeholders["0"], ParseMode.HTML)
    auto_delete_message(message, 10)

    return create_xp_trigger_end(update, context)


def create_xp_trigger_end(update: Update, context: CallbackContext) -> int:
    """
    Ends the creation of the creation of a xp trigger conversation and
    deletes all the saved information from the user_data.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: ConversationHandler.END
    """
    delete_conv_from_telegram_data(context, "create_xp_trigger")

    return end_conv(update, context)


# ------------------------------------------conv_createXpTrigger--------------------------------------------------------


# ------------------------------------------conv_createItem-------------------------------------------------------------


def create_item(update: Update, context: CallbackContext) -> int:
    """
    Starts the conversation that handles the creation of a new special ability and ask the user the name of it.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """

    placeholders = get_lang(context, create_item.__name__)

    add_tag_in_telegram_data(context, ["create_item", "invocation_message"], update.message)

    message = context.user_data["create_item"]["invocation_message"].reply_text(placeholders["0"], ParseMode.HTML)
    add_tag_in_telegram_data(context, ["create_item", "message"], message)

    return 0


def create_item_name(update: Update, context: CallbackContext) -> int:
    """
    Stores the information about the xp trigger description in the user_data,
    then asks if is a trigger for a crew or not.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, create_item_name.__name__)
    context.user_data["create_item"]["message"].delete()

    name = update.message.text
    if query_items(name):
        message = context.user_data["create_item"]["invocation_message"].reply_text(placeholders["err"], ParseMode.HTML)
        add_tag_in_telegram_data(context, ["create_item", "message"], message)
        return 0

    add_tag_in_telegram_data(context, ["create_item", "info", "name"], update.message.text)

    message = context.user_data["create_item"]["invocation_message"].reply_text(
        placeholders["0"], ParseMode.HTML)
    add_tag_in_telegram_data(context, ["create_item", "message"], message)

    update.message.delete()
    return 1


def create_item_description(update: Update, context: CallbackContext) -> int:
    """
    Stores the information about the description in the user_data, then adds the new special ability to the database.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, create_item_description.__name__)
    context.user_data["create_item"]["message"].delete()

    add_tag_in_telegram_data(context, ["create_item", "info", "description"], update.message.text)

    message = context.user_data["create_item"]["invocation_message"].reply_text(placeholders["0"], ParseMode.HTML)
    add_tag_in_telegram_data(context, ["create_item", "message"], message)

    update.message.delete()
    return 2


def create_item_weight(update: Update, context: CallbackContext) -> int:
    """
    Stores the information about the description in the user_data, then adds the new special ability to the database.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, create_item_weight.__name__)
    context.user_data["create_item"]["message"].delete()

    try:
        weight = int(update.message.text)
        if weight < 0:
            raise Exception
    except:
        message = context.user_data["create_item"]["invocation_message"].reply_text(placeholders["err"], ParseMode.HTML)
        add_tag_in_telegram_data(context, ["create_item", "message"], message)
        update.message.delete()
        return 2

    add_tag_in_telegram_data(context, ["create_item", "info", "weight"], weight)

    message = context.user_data["create_item"]["invocation_message"].reply_text(placeholders["0"], ParseMode.HTML)
    add_tag_in_telegram_data(context, ["create_item", "message"], message)

    update.message.delete()
    return 3


def create_item_usages(update: Update, context: CallbackContext) -> int:
    """
    Stores the information about the description in the user_data, then adds the new special ability to the database.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, create_item_usages.__name__)
    context.user_data["create_item"]["message"].delete()

    try:
        usages = int(update.message.text)
        if usages < -1:
            raise Exception
    except:
        message = context.user_data["create_item"]["invocation_message"].reply_text(placeholders["err"], ParseMode.HTML)
        add_tag_in_telegram_data(context, ["create_item", "message"], message)
        update.message.delete()
        return 3

    add_tag_in_telegram_data(context, ["create_item", "info", "usages"], usages)

    insert_item(**context.user_data["create_item"]["info"])

    message = context.user_data["create_item"]["invocation_message"].reply_text(placeholders["0"], ParseMode.HTML)
    auto_delete_message(message, 15)

    return create_item_end(update, context)


def create_item_end(update: Update, context: CallbackContext) -> int:
    """
    Ends the creation of an item conversation and
    deletes all the saved information from the user_data.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: ConversationHandler.END
    """
    delete_conv_from_telegram_data(context, "create_item")

    return end_conv(update, context)


# ------------------------------------------conv_createItem-------------------------------------------------------------


# ------------------------------------------conv_createCharSheet--------------------------------------------------------


def create_char_sheet(update: Update, context: CallbackContext) -> int:
    """
    Starts the conversation that handles the creation of a new character sheet and ask the user the name of it.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """

    placeholders = get_lang(context, create_char_sheet.__name__)

    add_tag_in_telegram_data(context, ["char_sheet", "invocation_message"], update.message)

    message = context.user_data["char_sheet"]["invocation_message"].reply_text(placeholders["0"], ParseMode.HTML)
    add_tag_in_telegram_data(context, ["char_sheet", "message"], message)

    return 0


def create_char_sheet_name(update: Update, context: CallbackContext) -> int:
    """
    Stores the information about the xp trigger description in the user_data,
    then asks if is a trigger for a crew or not.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, create_char_sheet_name.__name__)
    context.user_data["char_sheet"]["message"].delete()

    name = update.message.text

    if name.lower in [sheet.lower for sheet in query_character_sheets()]:
        message = context.user_data["char_sheet"]["invocation_message"].reply_text(
            placeholders["err"], ParseMode.HTML)
        add_tag_in_telegram_data(context, ["char_sheet", "message"], message)
        return 0

    add_tag_in_telegram_data(context, ["char_sheet", "name"], name)

    message = context.user_data["char_sheet"]["invocation_message"].reply_text(
        placeholders["0"], ParseMode.HTML)
    add_tag_in_telegram_data(context, ["char_sheet", "message"], message)

    update.message.delete()
    return 1


def create_char_sheet_description(update: Update, context: CallbackContext) -> int:
    """
    Stores the information about the description in the user_data, then adds the new special ability to the database.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, create_char_sheet_description.__name__)
    context.user_data["char_sheet"]["message"].delete()

    add_tag_in_telegram_data(context, ["char_sheet", "CharacterSheet", "description"], update.message.text)

    add_tag_in_telegram_data(context, ["char_sheet", "Char_Action", "action_dots"], {})

    message = context.user_data["char_sheet"]["invocation_message"].reply_text \
        (placeholders["0"], ParseMode.HTML, reply_markup=custom_kb([action[0] for action in query_actions()]))
    add_tag_in_telegram_data(context, ["char_sheet", "message"], message)

    update.message.delete()
    return 2


def create_char_sheet_dots(update: Update, context: CallbackContext) -> int:
    """
    Stores the information about the actions in the user_data, .

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, create_char_sheet_dots.__name__)
    context.user_data["char_sheet"]["message"].delete()

    action = update.message.text

    if action not in [action[0] for action in query_actions()]:
        message = context.user_data["char_sheet"]["invocation_message"].reply_text(
            placeholders["err"], ParseMode.HTML, reply_markup=custom_kb([action[0] for action in query_actions()]))
        add_tag_in_telegram_data(context, ["char_sheet", "message"], message)
        update.message.delete()
        return 2

    action_dots = context.user_data["char_sheet"]["Char_Action"]["action_dots"]
    if action in action_dots:
        action_dots[action] += 1
    else:
        action_dots[action] = 1

    update.message.delete()

    number_of_actions = 0
    for key in action_dots.keys():
        number_of_actions += action_dots[key]
    if number_of_actions >= 3:
        npcs = [npc["name"] + ", " + npc["role"] for npc in query_npcs(as_dict=True)]

        buttons_list = []
        buttons = []
        for i in range(len(npcs)):
            buttons.append(npcs[i])
            if (i + 1) % 8 == 0:
                buttons_list.append(buttons.copy())
                buttons.clear()
        if buttons:
            buttons_list.append(buttons.copy())
        add_tag_in_telegram_data(context, ["char_sheet", "buttons_list"], buttons_list)
        add_tag_in_telegram_data(context, ["char_sheet", "query_menu_index"], 0)

        add_tag_in_telegram_data(context, ["char_sheet", "Char_Friend", "NPCs"], [])

        context.user_data["char_sheet"]["query_menu"] = context.user_data["char_sheet"][
            "invocation_message"].reply_text(
            placeholders["0"],
            parse_mode=ParseMode.HTML,
            reply_markup=build_multi_page_kb(buttons_list[0]))
        return 3

    else:
        message = context.user_data["char_sheet"]["invocation_message"].reply_text(
            placeholders["1"].format(number_of_actions), ParseMode.HTML,
            reply_markup=custom_kb([action[0] for action in query_actions()]))
        add_tag_in_telegram_data(context, ["char_sheet", "message"], message)
        return 2


def create_char_sheet_friends(update: Update, context: CallbackContext) -> int:
    """
    Stores the information about an NPC or Faction target in the chat_data.
    Sends the score's plan type request.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, create_char_sheet_friends.__name__)

    query = update.callback_query
    query.answer()

    choice = query.data
    index = context.user_data["char_sheet"]["query_menu_index"]

    npcs = context.user_data["char_sheet"]["Char_Friend"]["NPCs"]

    if choice == "RIGHT":
        index += 1
        if index > len(context.user_data["char_sheet"]["buttons_list"]):
            index = 0
        context.user_data["char_sheet"]["query_menu_index"] = index

    elif choice == "LEFT":
        index -= 1
        if index == -len(context.user_data["char_sheet"]["buttons_list"]):
            index = 0

        context.user_data["char_sheet"]["query_menu_index"] = index
    else:
        name = choice.split("$")[0]
        name, role = name.split(", ")
        if "$" in choice:
            npcs.append(query_npc_id(name, role))

            if len(npcs) >= 5:
                items = [item["name"] for item in query_items(as_dict=True)]

                buttons_list = []
                buttons = []
                for i in range(len(items)):
                    buttons.append(items[i])
                    if (i + 1) % 8 == 0:
                        buttons_list.append(buttons.copy())
                        buttons.clear()
                if buttons:
                    buttons_list.append(buttons.copy())
                add_tag_in_telegram_data(context, ["char_sheet", "buttons_list"], buttons_list)
                add_tag_in_telegram_data(context, ["char_sheet", "query_menu_index"], 0)

                add_tag_in_telegram_data(context, ["char_sheet", "Char_Item", "items"], [])

                context.user_data["char_sheet"]["query_menu"].delete()

                context.user_data["char_sheet"]["query_menu"] = context.user_data["char_sheet"][
                    "invocation_message"].reply_text(
                    placeholders["1"],
                    parse_mode=ParseMode.HTML,
                    reply_markup=build_multi_page_kb(buttons_list[0]))
                return 4

        else:

            description = query_npcs(name=name, role=role, as_dict=True)[0]["description"]

            if description is None or description == "":
                description = placeholders["404"]
            auto_delete_message(update.effective_message.reply_text(
                text=description, quote=False), description)
            return 3

    context.user_data["char_sheet"]["query_menu"].edit_text(
        placeholders["0"].format(len(npcs)), reply_markup=build_multi_page_kb(
            context.user_data["char_sheet"]["buttons_list"][context.user_data["char_sheet"]["query_menu_index"]]))
    return 3


def create_char_sheet_items(update: Update, context: CallbackContext) -> int:
    """
    Stores the information about an NPC or Faction target in the chat_data.
    Sends the score's plan type request.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, create_char_sheet_items.__name__)

    query = update.callback_query
    query.answer()

    choice = query.data
    index = context.user_data["char_sheet"]["query_menu_index"]

    items = context.user_data["char_sheet"]["Char_Item"]["items"]

    if choice == "RIGHT":
        index += 1
        if index > len(context.user_data["char_sheet"]["buttons_list"]):
            index = 0
        context.user_data["char_sheet"]["query_menu_index"] = index

    elif choice == "LEFT":
        index -= 1
        if index == -len(context.user_data["char_sheet"]["buttons_list"]):
            index = 0

        context.user_data["char_sheet"]["query_menu_index"] = index
    else:
        name = choice
        if "$" in choice:
            items.append(name)

            if len(items) >= 6:
                sa = [sa["name"] for sa in query_special_abilities(pc=True, as_dict=True)]

                buttons_list = []
                buttons = []
                for i in range(len(sa)):
                    buttons.append(sa[i])
                    if (i + 1) % 8 == 0:
                        buttons_list.append(buttons.copy())
                        buttons.clear()
                if buttons:
                    buttons_list.append(buttons.copy())
                add_tag_in_telegram_data(context, ["char_sheet", "buttons_list"], buttons_list)
                add_tag_in_telegram_data(context, ["char_sheet", "query_menu_index"], 0)

                add_tag_in_telegram_data(context, ["char_sheet", "Char_Sa", "sas"], [])

                context.user_data["char_sheet"]["query_menu"].delete()

                context.user_data["char_sheet"]["query_menu"] = context.user_data["char_sheet"][
                    "invocation_message"].reply_text(
                    placeholders["1"],
                    parse_mode=ParseMode.HTML,
                    reply_markup=build_multi_page_kb(buttons_list[0]))
                return 5

        else:
            item_dict = query_items(name, as_dict=True)[0]
            description = item_dict["description"] + "\nweight: " + str(item_dict["weight"]) + "\nusages: " + str(
                item_dict["usages"])

            if description is None or description == "":
                description = placeholders["404"]
            auto_delete_message(update.effective_message.reply_text(
                text=description, quote=False), description)
            return 4

    context.user_data["char_sheet"]["query_menu"].edit_text(
        placeholders["0"].format(len(items)), reply_markup=build_multi_page_kb(
            context.user_data["char_sheet"]["buttons_list"][context.user_data["char_sheet"]["query_menu_index"]]))
    return 4


def create_char_sheet_sa(update: Update, context: CallbackContext) -> int:
    """
    Stores the information about an NPC or Faction target in the chat_data.
    Sends the score's plan type request.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, create_char_sheet_sa.__name__)

    query = update.callback_query
    query.answer()

    choice = query.data
    index = context.user_data["char_sheet"]["query_menu_index"]

    sas = context.user_data["char_sheet"]["Char_Sa"]["sas"]

    if choice == "RIGHT":
        index += 1
        if index > len(context.user_data["char_sheet"]["buttons_list"]):
            index = 0
        context.user_data["char_sheet"]["query_menu_index"] = index

    elif choice == "LEFT":
        index -= 1
        if index == -len(context.user_data["char_sheet"]["buttons_list"]):
            index = 0

        context.user_data["char_sheet"]["query_menu_index"] = index
    else:
        name = choice
        if "$" in choice:
            sas.append(name)

            if len(sas) >= 8:
                triggers = [str(trigger[0]) for trigger in query_xp_triggers_id_description()]

                buttons_list = []
                buttons = []
                for i in range(len(triggers)):
                    buttons.append(triggers[i])
                    if (i + 1) % 8 == 0:
                        buttons_list.append(buttons.copy())
                        buttons.clear()
                if buttons:
                    buttons_list.append(buttons.copy())
                add_tag_in_telegram_data(context, ["char_sheet", "buttons_list"], buttons_list)
                add_tag_in_telegram_data(context, ["char_sheet", "query_menu_index"], 0)

                context.user_data["char_sheet"]["query_menu"].delete()

                context.user_data["char_sheet"]["query_menu"] = context.user_data["char_sheet"][
                    "invocation_message"].reply_text(
                    placeholders["1"],
                    parse_mode=ParseMode.HTML,
                    reply_markup=build_multi_page_kb(buttons_list[0]))
                return 6

        else:
            description = query_special_abilities(special_ability=name, as_dict=True)[0]["description"]
            if description is None or description == "":
                description = placeholders["404"]
            auto_delete_message(update.effective_message.reply_text(
                text=description, quote=False), description)
            return 5

    context.user_data["char_sheet"]["query_menu"].edit_text(
        placeholders["0"].format(len(sas)), reply_markup=build_multi_page_kb(
            context.user_data["char_sheet"]["buttons_list"][context.user_data["char_sheet"]["query_menu_index"]]))
    return 5


def create_char_sheet_xp(update: Update, context: CallbackContext) -> int:
    """
    Stores the information about an NPC or Faction target in the chat_data.
    Sends the score's plan type request.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, create_char_sheet_xp.__name__)

    query = update.callback_query
    query.answer()

    choice = query.data
    index = context.user_data["char_sheet"]["query_menu_index"]

    if choice == "RIGHT":
        index += 1
        if index > len(context.user_data["char_sheet"]["buttons_list"]):
            index = 0
        context.user_data["char_sheet"]["query_menu_index"] = index

    elif choice == "LEFT":
        index -= 1
        if index == -len(context.user_data["char_sheet"]["buttons_list"]):
            index = 0

        context.user_data["char_sheet"]["query_menu_index"] = index
    else:
        if "$" in choice:
            choice = choice.split("$")[0]
            add_tag_in_telegram_data(context, ["char_sheet", "Char_Xp", "xp_id"], int(choice))

            sheet_name = context.user_data["char_sheet"]["name"]
            info = context.user_data["char_sheet"]

            insert_character_sheet(sheet_name, **info["CharacterSheet"])
            for key in info["Char_Action"]["action_dots"].keys():
                insert_char_action(sheet_name, key, info["Char_Action"]["action_dots"][key])
            for npc in info["Char_Friend"]["NPCs"]:
                insert_char_friend(sheet_name, npc)
            for item in info["Char_Item"]["items"]:
                insert_char_item(sheet_name, item)
            insert_char_sa(sheet_name, info["Char_Sa"]["sas"][0], True)
            info["Char_Sa"]["sas"].pop(0)
            for special_ability in info["Char_Sa"]["sas"]:
                insert_char_sa(sheet_name, special_ability)
            for i in range(1, 4):
                insert_char_xp(sheet_name, i, False)
            insert_char_xp(sheet_name, info["Char_Xp"]["xp_id"], True)

            message = context.user_data["char_sheet"]["invocation_message"].reply_text(placeholders["1"])
            auto_delete_message(message, 15)

            return create_char_sheet_end(update, context)

        else:
            description = query_xp_triggers_id_description(int(choice))[0][1]
            if description is None or description == "":
                description = placeholders["404"]
            auto_delete_message(update.effective_message.reply_text(
                text=description, quote=False), description)
            return 6

    context.user_data["char_sheet"]["query_menu"].edit_text(
        placeholders["0"], reply_markup=build_multi_page_kb(
            context.user_data["char_sheet"]["buttons_list"][context.user_data["char_sheet"]["query_menu_index"]]))
    return 6


def create_char_sheet_end(update: Update, context: CallbackContext) -> int:
    """
    Ends the creation of an item conversation and
    deletes all the saved information from the user_data.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: ConversationHandler.END
    """
    delete_conv_from_telegram_data(context, "char_sheet")

    return end_conv(update, context)


# ------------------------------------------conv_createCharSheet--------------------------------------------------------


# ------------------------------------------conv_createHuntingGround----------------------------------------------------


def create_hg(update: Update, context: CallbackContext) -> int:
    """
    Starts the conversation that handles the creation of a new special ability and ask the user the name of it.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """

    placeholders = get_lang(context, create_hg.__name__)

    add_tag_in_telegram_data(context, ["create_hg", "invocation_message"], update.message)

    message = context.user_data["create_hg"]["invocation_message"].reply_text(placeholders["0"], ParseMode.HTML)
    add_tag_in_telegram_data(context, ["create_hg", "message"], message)

    return 0


def create_hg_name(update: Update, context: CallbackContext) -> int:
    """
    Stores the information about the special ability name in the user_data, then asks for the description.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, create_hg_name.__name__)
    context.user_data["create_hg"]["message"].delete()

    name = update.message.text
    if name in [sa["name"] for sa in query_special_abilities(as_dict=True)]:
        message = context.user_data["create_hg"]["invocation_message"].reply_text(placeholders["err"], ParseMode.HTML)
        add_tag_in_telegram_data(context, ["create_hg", "message"], message)
        return 0

    add_tag_in_telegram_data(context, ["create_hg", "info", "name"], name)

    message = context.user_data["create_hg"]["invocation_message"].reply_text(placeholders["0"], ParseMode.HTML)
    add_tag_in_telegram_data(context, ["create_hg", "message"], message)

    update.message.delete()
    return 1


def create_hg_description(update: Update, context: CallbackContext) -> int:
    """
    Stores the information about the description in the user_data, then adds the new special ability to the database.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: calls create_hg_end.
    """
    placeholders = get_lang(context, create_hg_description.__name__)
    context.user_data["create_hg"]["message"].delete()

    add_tag_in_telegram_data(context, ["create_hg", "info", "description"], update.message.text)

    insert_hunting_ground(**context.user_data["create_hg"]["info"])

    message = context.user_data["create_hg"]["invocation_message"].reply_text(placeholders["0"], ParseMode.HTML)
    auto_delete_message(message, 10)

    return create_hg_end(update, context)


def create_hg_end(update: Update, context: CallbackContext) -> int:
    """
    Ends the creation of the creation of a special ability conversation and
    deletes all the saved information from the user_data.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: ConversationHandler.END
    """
    delete_conv_from_telegram_data(context, "create_hg")

    return end_conv(update, context)


# ------------------------------------------conv_createHuntingGround----------------------------------------------------


# ------------------------------------------conv_createUpgrade----------------------------------------------------------


def create_upgrade(update: Update, context: CallbackContext) -> int:
    """
    Starts the conversation that handles the creation of a new upgrade and ask the user the name of it.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """

    placeholders = get_lang(context, create_upgrade.__name__)

    add_tag_in_telegram_data(context, ["create_upgrade", "invocation_message"], update.message)

    message = context.user_data["create_upgrade"]["invocation_message"].reply_text(placeholders["0"], ParseMode.HTML)
    add_tag_in_telegram_data(context, ["create_upgrade", "message"], message)

    return 0


def create_upgrade_name(update: Update, context: CallbackContext) -> int:
    """
    Stores the information about the upgrade name in the user_data,
    then asks if is a trigger for a crew or not.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, create_upgrade_name.__name__)
    context.user_data["create_upgrade"]["message"].delete()

    name = update.message.text
    if query_upgrades(name):
        message = context.user_data["create_upgrade"]["invocation_message"].reply_text(
            placeholders["err"], ParseMode.HTML)
        add_tag_in_telegram_data(context, ["create_upgrade", "message"], message)
        return 0

    add_tag_in_telegram_data(context, ["create_upgrade", "info", "name"], update.message.text)

    message = context.user_data["create_upgrade"]["invocation_message"].reply_text(
        placeholders["0"], ParseMode.HTML)
    add_tag_in_telegram_data(context, ["create_upgrade", "message"], message)

    update.message.delete()
    return 1


def create_upgrade_description(update: Update, context: CallbackContext) -> int:
    """
    Stores the information about the description in the user_data.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, create_upgrade_description.__name__)
    context.user_data["create_upgrade"]["message"].delete()

    add_tag_in_telegram_data(context, ["create_upgrade", "info", "description"], update.message.text)

    message = context.user_data["create_upgrade"]["invocation_message"].reply_text(placeholders["0"], ParseMode.HTML)
    add_tag_in_telegram_data(context, ["create_upgrade", "message"], message)

    update.message.delete()
    return 2


def create_upgrade_tot_quality(update: Update, context: CallbackContext) -> int:
    """
    Stores the information about the tot quality in the user_data, then adds the new upgrade to the database.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, create_upgrade_tot_quality.__name__)
    context.user_data["create_upgrade"]["message"].delete()

    try:
        tot_quality = int(update.message.text)
        if 1 > tot_quality > 4:
            raise Exception
    except:
        message = context.user_data["create_upgrade"]["invocation_message"].reply_text(
            placeholders["err"], ParseMode.HTML)
        add_tag_in_telegram_data(context, ["create_upgrade", "message"], message)
        update.message.delete()
        return 3

    add_tag_in_telegram_data(context, ["create_upgrade", "info", "quality"], tot_quality)

    insert_upgrade(**context.user_data["create_upgrade"]["info"])

    message = context.user_data["create_upgrade"]["invocation_message"].reply_text(placeholders["0"], ParseMode.HTML)
    auto_delete_message(message, 15)

    return create_upgrade_end(update, context)


def create_upgrade_end(update: Update, context: CallbackContext) -> int:
    """
    Ends the creation of an upgrade conversation and
    deletes all the saved information from the user_data.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: ConversationHandler.END
    """
    delete_conv_from_telegram_data(context, "create_upgrade")

    return end_conv(update, context)


# ------------------------------------------conv_createUpgrade----------------------------------------------------------


# ------------------------------------------conv_createNPC--------------------------------------------------------------


def create_npc(update: Update, context: CallbackContext) -> int:
    """
    Starts the conversation that handles the creation of a new special ability and ask the user the name of it.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """

    placeholders = get_lang(context, create_npc.__name__)

    add_tag_in_telegram_data(context, ["create_npc", "invocation_message"], update.message)

    message = context.user_data["create_npc"]["invocation_message"].reply_text(placeholders["0"], ParseMode.HTML)
    add_tag_in_telegram_data(context, ["create_npc", "message"], message)

    return 0


def create_npc_name(update: Update, context: CallbackContext) -> int:
    """
    Stores the information about the special ability name in the user_data, then asks for the description.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, create_npc_name.__name__)
    context.user_data["create_npc"]["message"].delete()

    name = update.message.text

    add_tag_in_telegram_data(context, ["create_npc", "info", "name"], name)

    message = context.user_data["create_npc"]["invocation_message"].reply_text(placeholders["0"], ParseMode.HTML)
    add_tag_in_telegram_data(context, ["create_npc", "message"], message)

    update.message.delete()
    return 1


def create_npc_role(update: Update, context: CallbackContext) -> int:
    """
    Stores the information about the special ability name in the user_data, then asks for the description.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    placeholders = get_lang(context, create_npc_role.__name__)
    context.user_data["create_npc"]["message"].delete()

    add_tag_in_telegram_data(context, ["create_npc", "info", "role"], update.message.text)

    factions = [faction["name"] + ": " + str(faction["tier"]) for faction in query_factions(as_dict=True)]

    buttons_list = []
    buttons = []
    for i in range(len(factions)):
        buttons.append(factions[i])
        if (i + 1) % 8 == 0:
            buttons_list.append(buttons.copy())
            buttons.clear()
    if buttons:
        buttons_list.append(buttons.copy())
    add_tag_in_telegram_data(context, ["create_npc", "buttons_list"], buttons_list)
    add_tag_in_telegram_data(context, ["create_npc", "query_menu_index"], 0)

    query_menu = context.user_data["create_npc"]["invocation_message"].reply_text(
        placeholders["0"], ParseMode.HTML, reply_markup=build_multi_page_kb(buttons_list[0]))

    add_tag_in_telegram_data(context, ["create_npc", "query_menu"], query_menu)

    update.message.delete()
    return 2


def create_npc_faction(update: Update, context: CallbackContext) -> int:
    """
    Handles the choice of the faction used to perform the roll.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """

    placeholders = get_lang(context, create_npc_faction.__name__)

    query = update.callback_query
    query.answer()

    choice = query.data
    index = context.user_data["create_npc"]["query_menu_index"]

    if choice == "RIGHT":
        index += 1
        if index >= len(context.user_data["create_npc"]["buttons_list"]):
            index = 0
        context.user_data["create_npc"]["query_menu_index"] = index

    elif choice == "LEFT":
        index -= 1
        if index == -len(context.user_data["create_npc"]["buttons_list"]):
            index = 0

        context.user_data["create_npc"]["query_menu_index"] = index
    else:
        name = choice.split("$")[0]
        name = name.split(": ")[0]
        if "$" in choice:
            add_tag_in_telegram_data(context, tags=["create_npc", "info", "faction"],
                                     value=name)

            context.user_data["create_npc"]["query_menu"].delete()

            message = context.user_data["create_npc"]["invocation_message"].reply_text(placeholders["1"],
                                                                                       ParseMode.HTML)
            add_tag_in_telegram_data(context, ["create_npc", "message"], message)

            return 3
        else:
            description = query_factions(name=name, as_dict=True)[0]["description"]

            if description is None or description == "":
                description = placeholders["404"]
            auto_delete_message(update.effective_message.reply_text(
                text=description, quote=False), description)
            return 2

    context.user_data["create_npc"]["query_menu"].edit_text(
        placeholders["0"], reply_markup=build_multi_page_kb(
            context.user_data["create_npc"]["buttons_list"][
                context.user_data["create_npc"]["query_menu_index"]]))
    return 2


def create_npc_description(update: Update, context: CallbackContext) -> int:
    """
    Stores the information about the description in the user_data, then adds the new special ability to the database.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: calls create_npc_end.
    """
    placeholders = get_lang(context, create_npc_description.__name__)
    context.user_data["create_npc"]["message"].delete()

    add_tag_in_telegram_data(context, ["create_npc", "info", "description"], update.message.text)

    insert_npc(**context.user_data["create_npc"]["info"])

    message = context.user_data["create_npc"]["invocation_message"].reply_text(placeholders["0"], ParseMode.HTML)
    auto_delete_message(message, 10)

    return create_npc_end(update, context)


def create_npc_end(update: Update, context: CallbackContext) -> int:
    """
    Ends the creation of the creation of a special ability conversation and
    deletes all the saved information from the user_data.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: ConversationHandler.END
    """
    delete_conv_from_telegram_data(context, "create_npc")

    return end_conv(update, context)


# ------------------------------------------conv_createNPC--------------------------------------------------------------


def greet_chat_members(update: Update, context: CallbackContext) -> None:
    """
    Greets new users in chats and announces when someone leaves.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    """
    placeholders = get_lang(context, greet_chat_members.__name__)

    result = extract_status_change(update.chat_member)
    if result is None:
        return

    was_member, is_member = result
    cause_name = update.chat_member.from_user.mention_html()
    member_name = update.chat_member.new_chat_member.user.mention_html()

    if not was_member and is_member:
        update.effective_chat.send_message(
            placeholders["0"].format(member_name, cause_name), parse_mode=ParseMode.HTML)
    elif was_member and not is_member:
        update.effective_chat.send_message(placeholders["1"].format(cause_name, member_name), parse_mode=ParseMode.HTML)


def track_chats(update: Update, context: CallbackContext) -> None:
    """
    Tracks the chats the bot is in.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    """
    result = extract_status_change(update.my_chat_member)
    if result is None:
        return
    was_member, is_member = result

    # Handle chat types differently:
    chat = update.effective_chat
    if chat.type == Chat.PRIVATE:
        if not was_member and is_member:
            context.bot_data.setdefault("user_ids", set()).add(chat.id)
        elif was_member and not is_member:
            context.bot_data.setdefault("user_ids", set()).discard(chat.id)
    elif chat.type in [Chat.GROUP, Chat.SUPERGROUP]:
        if not was_member and is_member:
            context.bot_data.setdefault("group_ids", set()).add(chat.id)
        elif was_member and not is_member:
            context.bot_data.setdefault("group_ids", set()).discard(chat.id)
    else:
        if not was_member and is_member:
            context.bot_data.setdefault("channel_ids", set()).add(chat.id)
        elif was_member and not is_member:
            context.bot_data.setdefault("channel_ids", set()).discard(chat.id)
