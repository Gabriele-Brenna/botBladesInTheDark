import copy

from telegram.utils import helpers
from bot.BotUtils import *


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
        for i in range(len(placeholders["default"])):
            update.message.reply_text(placeholders["default"][str(i)], parse_mode=ParseMode.HTML)
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
        update.effective_chat.send_message(placeholders["0"].format(update.message.from_user.username, url),
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

    add_tag_in_user_data(context, ["create_pc", "pc", "vice", "name"], update.message.text)

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
    add_tag_in_user_data(context, ["create_pc", "pc", "vice", "description"], update.message.text)

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
            add_tag_in_user_data(context, tags=["myPCs", dict_create_pc["pc"]["name"].lower()],
                                 value=dict_create_pc["pc"])
        else:
            auto_delete_message(update.message.reply_text(placeholders["0"]))
            update.message.delete()
            return 0

    try:
        dict_create_pc["query_menu"].delete()
    except:
        pass

    try:
        dict_create_pc["message"].delete()
    except:
        pass

    context.user_data.pop("create_pc")

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

    delete_conv_from_user_data(context, "create_game")
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
        auto_delete_message(update.message.reply_text(placeholders[""]), 10)
        delete_conv_from_user_data(context, "join")
        return end_conv(update, context)

    if update.message.text.lower() == "as master":
        controller.update_user_in_game(get_user_id(update), update.message.chat_id,
                                       context.user_data["join"]["game_name"], True)

        update.message.reply_text(placeholders["0"].format(query_users_names(get_user_id(update))[0],
                                                           context.user_data["join"]["game_name"]),
                                  parse_mode=ParseMode.HTML,
                                  quote=False)
        delete_conv_from_user_data(context, "join")
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
        update.effective_chat.send_message(placeholders["0"].format(update.message.from_user.username,
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
        else:
            auto_delete_message(update.message.reply_text(placeholders["1"]))
            update.message.delete()
            return 0

    delete_conv_from_user_data(context, "join")

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

    add_tag_in_user_data(context, ["create_crew", "crew", "lair", "location"], update.message.text)

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
        for i in range(1, len(choice)-1):
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

        if upgrade["name"].split("(")[0].lower() in upgrades_names:
            buttons.append("{}: {}/{}".format(upgrade["name"].split("(")[0],
                                              upgrades_quality[
                                                  upgrades_names.index(upgrade["name"].split("(")[0].lower())],
                                              upgrade["tot_quality"]))
        else:
            buttons.append("{}: 0/{}".format(upgrade["name"].split("(")[0], upgrade["tot_quality"]))
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

    delete_conv_from_user_data(context, "create_crew")

    return end_conv(update, context)


# ------------------------------------------conv_createCrew-------------------------------------------------------------


# ------------------------------------------conv_actionRoll-------------------------------------------------------------


def action_roll(update: Update, context: CallbackContext) -> int:
    return end_conv(update, context)


# ------------------------------------------conv_actionRoll-------------------------------------------------------------


# ------------------------------------------conv_changeState-------------------------------------------------------------


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

    controller.change_state(query_game_of_user(update.effective_message.chat_id, get_user_id(update)), choice[1])
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
    dict_change_state = context.user_data["change_state"]

    try:
        dict_change_state["query_menu"].delete()
    except:
        pass

    try:
        dict_change_state["message"].delete()
    except:
        pass

    context.user_data.pop("change_state")

    return end_conv(update, context)

# ------------------------------------------conv_changeState-------------------------------------------------------------


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
