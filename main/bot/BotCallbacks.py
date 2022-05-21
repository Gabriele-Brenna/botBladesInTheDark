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
    Stores the effect decided by the GM in the chat_data and brings back the conversation to the invoker of the command.
    Sends the keyboard with the "Push Yourself", "Devil's Bargain" and "No Thanks" option.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the next state of the conversation.
    """
    context.chat_data["action_roll"]["message"].delete()

    placeholders = get_lang(context, action_roll_effect.__name__)

    add_tag_in_telegram_data(context, location="chat", tags=["action_roll", "roll", "effect"],
                             value=update.message.text)

    auto_delete_message(
        update.message.reply_text(placeholders["0"].format(context.chat_data["action_roll"]["roll"]["pc"],
                                                           context.chat_data["action_roll"]["roll"]["goal"]),
                                  quote=False, parse_mode=ParseMode.HTML), 20)

    context.chat_data["action_roll"]["message"] = context.chat_data["action_roll"]["invocation_message"].reply_text(
        placeholders["1"], reply_markup=custom_kb(buttons=placeholders["keyboard"],
                                                  callback_data=placeholders["callbacks"],
                                                  inline=True, split_row=1))

    update.message.delete()
    return 2


def action_roll_assistance(update: Update, context: CallbackContext) -> None:
    """
    Stores the PC of the user who decided to assist the invoker's PC in the chat_data if the sender of this command has
    actually a PC and if he is not the invoker of the action roll.
    This command can be executed in any time of the action roll's conversation.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    """
    placeholders = get_lang(context, action_roll_assistance.__name__)

    user_id = get_user_id(update)
    chat_id = update.effective_message.chat_id
    invoker_id = context.chat_data["action_roll"]["invoker"]
    if user_id != invoker_id:
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
                    update_bonus_dice_kb(context, "action_roll")

                auto_delete_message(
                    update.message.reply_text(placeholders["0"].format(context.user_data["active_PCs"][chat_id]),
                                              parse_mode=ParseMode.HTML), 18)
                return

    auto_delete_message(
        update.message.reply_text(placeholders["2"], parse_mode=ParseMode.HTML), 18)


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
        context.chat_data["action_roll"]["master_message"].delete()
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

    add_tag_in_telegram_data(context, location="chat",
                             tags=["action_roll", "roll", "devil_bargain"], value=update.message.text)

    bonus_dice_lang = get_lang(context, "bonus_dice")
    add_tag_in_telegram_data(context, location="chat", tags=["action_roll", "roll", "bonus_dice"], value=0)
    query_menu = context.chat_data["action_roll"]["invocation_message"].reply_text(bonus_dice_lang["message"].format(
        action_roll_calc_total_dice(context.chat_data["action_roll"]["roll"])),
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
    Then, the final description request is sent.

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

        update_bonus_dice_kb(context, "action_roll")

    elif choice == "DONE":
        dice_to_roll = action_roll_calc_total_dice(context.chat_data["action_roll"]["roll"])
        context.args = []
        context.args.append(dice_to_roll)
        context.args.append(["action_roll", "roll", "outcome"])

        context.chat_data["action_roll"]["query_menu"].delete()

        roll_dice(update, context)

        context.chat_data["action_roll"]["message"] = \
            context.chat_data["action_roll"]["invocation_message"].reply_text(
                placeholders["0"], parse_mode=ParseMode.HTML)
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

    trauma_victims = controller.commit_action_roll(update.effective_message.chat_id,
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


def roll_dice(update: Update, context: CallbackContext) -> None:
    """
    Rolls the specified amount of dice and interprets the result, according to BitD rules.
    If no parameters are passed after "/roll", only one die is rolled.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    """
    dice = 1
    if context.args:
        try:
            dice = int(context.args[0])
        except ValueError:
            update.message.reply_text(get_lang(context, roll_dice.__name__)["nan"].format(context.args[0]),
                                      parse_mode=ParseMode.HTML)
            return

    result, rolls = DiceRoller.roll_dice(dice)

    def execute(r: List[int]) -> None:
        for i in range(len(r)):
            auto_delete_message(update.effective_message.reply_sticker(sticker=dice_stickers[str(r[i])],
                                                                       quote=False), (len(r) - i) * 3 + 3)
            time.sleep(3)
        time.sleep(3)

    if dice != 1:
        t = Thread(target=execute, kwargs={"r": rolls})
        t.start()
        t.join()

    update.effective_message.reply_text(get_lang(context, roll_dice.__name__)[str(result)], parse_mode=ParseMode.HTML,
                                        quote=False)
    update.effective_message.reply_sticker(sticker=dice_stickers[str(result)], quote=False)

    try:
        add_tag_in_telegram_data(context, tags=list(context.args[1]), location="chat", value=result)
    except IndexError:
        pass
    except:
        traceback.print_exc()


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

    add_tag_in_telegram_data(context, ["create_clock", "clock", "name"], update.message.text)

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
            add_tag_in_telegram_data(context, ["add_claim", "claim", "name"], description)

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

    return end_conv(update, context, True)


# ------------------------------------------conv_addClaim---------------------------------------------------------------

# ------------------------------------------send_sheets-----------------------------------------------------------------

def send_character_sheet(update: Update, context: CallbackContext) -> None:
    placeholders = get_lang(context, send_character_sheet.__name__)
    chat_id = update.effective_message.chat_id
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
        img_bytes, file_name = controller.get_crew_sheet_image(chat_id, get_user_id(update))
        update.effective_message.reply_photo(photo=img_bytes, filename=file_name, caption=placeholders["1"])
    else:
        update.message.reply_text(placeholders["0"])


# ------------------------------------------send_sheets-----------------------------------------------------------------


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
