import copy
from threading import Thread
import time
from typing import *

from telegram.ext import *
from telegram import *
from telegram.utils import helpers

from controller.Controller import Controller
from controller.DBreader import *
from controller.DBwriter import *
from utility.FilesManager import *

# instantiates the Controller.
controller = Controller()

# loading of default language dict.
with open(path_finder('ENG.json'), 'r', encoding="utf8") as lang_f:
    default_lang = json.load(lang_f)["Bot"]


def extract_status_change(chat_member_update: ChatMemberUpdated) -> Optional[Tuple[bool, bool]]:
    """
    Extracts whether the 'old_chat_member' was a member
    of the chat and whether the 'new_chat_member' is a member of the chat.

    :param chat_member_update: the ChatMemberUpdated instance.
    :return: None, if the status didn't change. A Tuple[bool, bool] representing respectively if the user 'was a member'
    and if the user 'is a member'.
    """
    status_change = chat_member_update.difference().get("status")
    old_is_member, new_is_member = chat_member_update.difference().get("is_member", (None, None))

    if status_change is None:
        return None

    old_status, new_status = status_change
    was_member = (
            old_status
            in [
                ChatMember.MEMBER,
                ChatMember.CREATOR,
                ChatMember.ADMINISTRATOR,
            ]
            or (old_status == ChatMember.RESTRICTED and old_is_member is True)
    )
    is_member = (
            new_status
            in [
                ChatMember.MEMBER,
                ChatMember.CREATOR,
                ChatMember.ADMINISTRATOR,
            ]
            or (new_status == ChatMember.RESTRICTED and new_is_member is True)
    )

    return was_member, is_member


def get_lang(context: CallbackContext, method: str = None) -> dict:
    """
    Extracts the user's language preference dictionary, sets the default_lang (ENG) if not present.

    :param context: instance of CallbackContext linked to the user to extract the user_data.
    :param method: if not None the specific method lang dictionary is returned.
    :return: a dict.
    """
    # TODO: remove after testing
    context.user_data["lang"] = default_lang
    # --------------------------------------

    if "lang" in context.user_data:
        if method is not None:
            if method in context.user_data["lang"]:
                return context.user_data["lang"][method]
        else:
            return context.user_data["lang"]
    else:
        context.user_data["lang"] = default_lang
        return get_lang(context, method)


def get_user_id(update: Update) -> int:
    """
    Gets the user's id given an Update.

    :param update: instance of Update sent by the user
    :return: the user's id.
    """
    if update.message is not None:
        return update.message.from_user.id
    elif update.callback_query is not None:
        return update.callback_query.from_user.id


def get_user_pc(context: CallbackContext) -> List[str]:
    """
    Searches the user_data in order to find (if present) the user's created characters.

    :param context: instance of CallbackContext linked to the user.
    :return: a list of the names of the user's characters. An empty list if the user has no characters yet.
    """
    if "myPCs" in context.user_data:
        return list(context.user_data["myPCs"].keys())

    return []


def user_is_registered(update: Update, context: CallbackContext) -> bool:
    """
    Checks if the user is registered in the Database. If not, it sends a message with the request of login.

    :param update: update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: True if the user is registered, False otherwise.
    """

    placeholders = get_lang(context, user_is_registered.__name__)

    user_id = get_user_id(update)
    if not exists_user(user_id):
        update.message.reply_text(placeholders["0"])
        return False
    return True


def test(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Test done")
    context.user_data.setdefault("myPCs", {})["pippo"] = {'name': 'Pippo', 'alias': 'Giovannino', 'look': 'Goofy',
                                                          'heritage': 'Akoros', 'background': 'Underworld',
                                                          'pc_class': 'Whisper', 'vice': {'name': "Weird",
                                                                                          'description': 'better not',
                                                                                          'purveyor': "Topolino's house"
                                                                                          },
                                                          'description': 'yes'}

    print("TEST")
    print("Sender Data: ")
    print("\t{}".format(update.message.from_user))
    print("-----------------user_data NO LANG--------------------------------------------")
    new_user_data = {}
    for key in context.user_data:
        if key != "lang":
            new_user_data[key] = context.user_data[key]
    print(new_user_data)
    print("------------------------------------------------------------------------------")
    print("-----------------chat_data----------------------------------------------------")
    print(context.chat_data)
    print("------------------------------------------------------------------------------")
    print("-----------------bot_data----------------------------------------------------")
    print(context.bot_data)
    print("------------------------------------------------------------------------------")
    print("-----------------callback_query-----------------------------------------------")
    print(update.callback_query)
    print("------------------------------------------------------------------------------")


def print_controller(update: Update, context: CallbackContext):
    update.message.reply_text("Controller printed")
    print("-----------------CONTROLLER----------------------------------------------------")
    print(controller)
    print("------------------------------------------------------------------------------")


def custom_kb(buttons: List[str], inline: bool = False, split_row: int = None, callback_data: List[str] = None,
              input_field_placeholder: str = None) -> ReplyMarkup:
    """
    Builds a parametric customized keyboard.

    :param buttons: list of buttons' labels. If empty a ReplyKeyboardRemove object is returned.
    :param inline: False if the custom keyboard should be a ReplyKeyboardMarkup, True if an InlineKeyboard.
    :param split_row: specifies the number of buttons per row. If not specified it is automatically calculated.
    :param callback_data: list of callback_data associated to each button.
    If the length of this list differs from the length of the buttons list,
    the button list is used also for callback_data.
    :param input_field_placeholder: the placeholder shown in the input field when the reply is active.
    :return: a ReplyMarkup object.
    """
    if not buttons:
        return ReplyKeyboardRemove()

    if callback_data is None:
        callback_data = buttons

    elif len(callback_data) != len(buttons):
        callback_data = buttons

    total = len(buttons)
    while split_row is None:
        for j in range(2, 5):
            if total % j == 0:
                split_row = j
        total += 1

    keyboard = []
    k_row = []
    for i in range(len(buttons)):
        if inline:
            k_row.append(InlineKeyboardButton(buttons[i], callback_data=callback_data[i]))
        else:
            k_row.append(KeyboardButton(buttons[i], callback_data=callback_data[i]))
        if (i + 1) % split_row == 0:
            keyboard.append(k_row)
            k_row = []

    if k_row:
        keyboard.append(k_row)

    if inline:
        return InlineKeyboardMarkup(keyboard)
    return ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, selective=True,
                               input_field_placeholder=input_field_placeholder)


def build_plus_minus_keyboard(central_buttons: List[str], back_button: bool = True,
                              inline: bool = True, split_row: int = 3) -> ReplyMarkup:
    """
    Builds a custom keyboard with buttons surrounded with others buttons with + and - symbols.

    :param central_buttons: list of the central buttons.
    :param back_button: True if the BACK button must be added at the end of the keyboard, False otherwise.
    :param inline: False if the custom keyboard should be a ReplyKeyboardMarkup, True if an InlineKeyboard.
    :param split_row: specifies the number of buttons per row. If not specified it is automatically calculated.
    :return: a ReplyMarkup object.
    """
    buttons = []
    callbacks = []
    for button in central_buttons:
        buttons.append("➖")
        buttons.append(button)
        buttons.append("➕")

        button = button.split(":")[0]
        callbacks.append(button + " -1")
        callbacks.append(button)
        callbacks.append(button + " +1")

    if back_button:
        buttons.append("🔙 BACK")
        callbacks.append("BACK")

    return custom_kb(buttons, inline, split_row, callbacks)


def store_value_and_update_kb(update: Update, context: CallbackContext, tags: List[str], value: Union[str, dict, list],
                              lang_source: str = None, btn_label: str = None, split_row: int = None):
    """
    Update the Inline keyboard of the conversation, according to the last section chosen and filled by the user.
    It also stores the last information received during the conversation.
    It calls add_tag_in_user_data and update_inline_keyboard.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :param tags: the list of tags representing the target key dict in user_data.
    :param value: the value to store in the target dict.
    :param lang_source: the tag representing the target dict in the language dictionary.
            If None the first element of tags' list is used.
    :param btn_label: the text of the selected button.
            If None the last element of tags' list is used.
    :param split_row: specifies the number of buttons per row. If not specified it is automatically calculated.
    """
    if btn_label is None:
        btn_label = tags[-1]
    if lang_source is None:
        lang_source = tags[0]

    add_tag_in_user_data(context, tags, value)
    update_inline_keyboard(update, context, tags[0], btn_label, lang_source, split_row)


def add_tag_in_user_data(context: CallbackContext, tags: List[str], value: Union[str, dict]):
    """
    Stores the passed value in the target dict.

    :param context: instance of CallbackContext linked to the user.
    :param tags: the list of tags representing the target key dict in user_data.
    :param value: the value to store in the target dict.
    """
    pointer = context.user_data
    for i in range(len(tags) - 1):
        pointer.setdefault(tags[i], {})
        pointer = pointer[tags[i]]
    pointer[tags[-1]] = value


def update_inline_keyboard(update: Update, context: CallbackContext, command: str, btn_label: str,
                           lang_source: str, split_row: int = None):
    """
    Update the Inline keyboard of the conversation, according to the last section chosen and filled by the user.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :param command: represents the command that starts the conversation.
    :param btn_label: the text of the selected button.
            If None the last element of tags' list is used.
    :param lang_source: the tag representing the target dict in the language dictionary.
            If None the first element of tags' list is used.
    :param split_row: specifies the number of buttons per row. If not specified it is automatically calculated.
    """
    context.user_data[command]["message"].delete()
    placeholders = get_lang(context, lang_source)

    user_id = get_user_id(update)
    updated_kb = context.user_data[command]["keyboard"]
    print(btn_label)

    for i in range(len(updated_kb)):
        print(updated_kb[i])
        if btn_label.lower() in updated_kb[i].lower():
            print("found")
            updated_kb[i] = btn_label.capitalize() + " ✅"

    query_menu = context.bot.sendMessage(text=placeholders["1"], chat_id=user_id,
                                         reply_markup=custom_kb(updated_kb, split_row=split_row, inline=True))

    context.user_data[command]["query_menu"] = query_menu


def query_state_switcher(update: Update, context: CallbackContext, conversation: str, placeholders: dict,
                         keyboards: List[List[str]], index_inlines: List[int] = None, starting_state: int = 1) -> int:
    """
    Handles the callback query from an Inline keyboard by redirecting the user in the correct state of the conversation
    and sending him the associated message.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :param conversation: represents the btn_label of the conversation in the user_data.
    :param placeholders: is the dictionary containing all the phrases to send.
    :param keyboards: the list of the keyboards to send as reply_markup for each state.
    :param index_inlines: list of the indexes of the keyboards that must be inline.
    :param starting_state: the first state among the possible switches.
    :return: the next state of the specified conversation.
    """
    if index_inlines is None:
        index_inlines = []

    query = update.callback_query
    query.answer()

    choice = query.data

    keyboard = context.user_data[conversation]["keyboard"]

    for i in range(len(keyboard)):
        inline = False
        if choice == keyboard[i]:
            if i in index_inlines:
                inline = True
            query.delete_message()
            context.user_data[conversation]["message"] = context.bot.sendMessage(chat_id=get_user_id(update),
                                                                                 text=placeholders[str(i)],
                                                                                 reply_markup=custom_kb(
                                                                                     keyboards[i], inline=inline))
            return i + starting_state
    return 0


def invalid_state_choice(update: Update, context: CallbackContext, command: str, placeholders: dict):
    """
    Handles an invalid choice of the user during a state of a conversation.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :param command: represents the command that starts the conversation.
    :param placeholders: is the dict containing the replies to send.
    """
    context.user_data[command]["message"].delete()
    auto_delete_message(update.message.reply_text(placeholders["0"]))
    context.user_data[command]["message"] = update.message.reply_text(text=placeholders["1"])
    update.message.delete()


def end_conv(update: Update, context: CallbackContext) -> int:
    """
    Handles the abort of a conversation.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: ConversationHandler.END
    """
    placeholders = get_lang(context, end_conv.__name__)

    message = update.message.reply_text(placeholders["0"], reply_markup=ReplyKeyboardRemove())
    auto_delete_message(update.message, 3.0)

    auto_delete_message(message, 3.0)
    return ConversationHandler.END


def auto_delete_message(message: Message, timer: float = 5.0) -> None:
    """
    Delete the given message after the specified amount of time (in seconds)
    running a separate Thread using a self-contained function.

    :param message: the message to delete
    :param timer: the time to wait before the deletion.
    """

    def execute(m: Message, t: float) -> None:
        time.sleep(t)
        m.delete()

    Thread(target=execute, args=(message, timer)).start()


def show_pc(update: Update, context: CallbackContext) -> None:
    """
    Displays the PCs stored in the user_data of the sender.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    """
    if "myPCs" not in context.user_data:
        update.message.reply_text("You don't have any PCs yet. Use /createPC to make one")
        return

    text = "<b>Your PCs</b>🔪:\n"
    for pc in context.user_data["myPCs"]:
        text += "\n"
        text += "<b><i>{}</i></b>:\n".format(pc["name"])
        for key in pc:
            if key != "name":
                text += "\t<i><u>{}</u></i>: {}\n".format(key, pc[key])
    update.message.reply_text(text, parse_mode=ParseMode.HTML)


def start_bot():
    """
    Starts the telegram bot. It loads the token from 'Token.txt', sets the persistence and instantiate the Updater
    and the Dispatcher, adding to it all the necessary Handlers
    """
    with open(path_finder('Token.txt'), 'r') as f:
        TOKEN = f.read()

    persistence = PicklePersistence(filename=os.path.join(get_resources_folder(), "BotPersistence"),
                                    store_callback_data=True)

    updater = Updater(TOKEN, persistence=persistence, arbitrary_callback_data=True)
    dispatcher: Dispatcher = updater.dispatcher

    # -----------------------------------------------Handlers-----------------------------------------------------------

    # Handle members joining/leaving chats.
    dispatcher.add_handler(ChatMemberHandler(greet_chat_members, ChatMemberHandler.CHAT_MEMBER))
    # Keep track of which chats the bot is in
    dispatcher.add_handler(ChatMemberHandler(track_chats, ChatMemberHandler.MY_CHAT_MEMBER))

    dispatcher.add_handler(CommandHandler("test".casefold(), test))
    dispatcher.add_handler(CommandHandler("controller".casefold(), print_controller))

    dispatcher.add_handler(CommandHandler("help".casefold(), help_msg))

    dispatcher.add_handler(CommandHandler("login".casefold(), start_login))
    dispatcher.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler("start", login, Filters.regex("login-BladesInTheDark-BotTelegram"))],
            states={
                0: [MessageHandler(Filters.text & ~Filters.command, login_receive_username)],
            },
            fallbacks=[CommandHandler("cancel".casefold(), end_conv)],
            name="conv_login",
            persistent=True
        )
    )

    dispatcher.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler("createPC".casefold(), create_pc)],
            states={
                0: [CallbackQueryHandler(create_pc_state_switcher)],
                1: [MessageHandler(Filters.text & ~Filters.command, create_pc_name)],
                2: [MessageHandler(Filters.text & ~Filters.command, create_pc_alias)],
                3: [MessageHandler(Filters.text & ~Filters.command, create_pc_look)],
                4: [MessageHandler(Filters.text & ~Filters.command, create_pc_heritage)],
                5: [MessageHandler(Filters.text & ~Filters.command, create_pc_background)],
                6: [MessageHandler(Filters.text & ~Filters.command, create_pc_description)],
                7: [MessageHandler(Filters.text & ~Filters.command, create_pc_class)],
                8: [MessageHandler(Filters.text & ~Filters.command, create_pc_vice_name)],
                9: [MessageHandler(Filters.text & ~Filters.command, create_pc_vice_description)],
                10: [MessageHandler(Filters.text & ~Filters.command, create_pc_vice_purveyor)]
            },
            per_chat=False,
            fallbacks=[CommandHandler("cancel".casefold(), create_pc_end),
                       CommandHandler("done".casefold(), create_pc_end)],
            name="conv_createPC",
            persistent=True
        )
    )

    dispatcher.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler("createGame".casefold(), create_game)],
            states={
                0: [MessageHandler(Filters.text & ~Filters.command, create_game_title)]
            },
            fallbacks=[CommandHandler("cancel".casefold(), end_conv)],
            name="conv_createGame",
            persistent=True
        )
    )

    dispatcher.add_handler(CommandHandler("myPCs".casefold(), show_pc))

    dispatcher.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler("join".casefold(), join)],
            states={
                0: [MessageHandler(Filters.text & ~Filters.command, join_game_name)],
                1: [MessageHandler(Filters.text & ~Filters.command, join_add_player)],
                2: [CallbackQueryHandler(join_complete_pc_state_switcher)],
                3: [MessageHandler(Filters.text & ~Filters.command, join_complete_pc_ability)],
                4: [CallbackQueryHandler(join_complete_pc_dots)],
                5: [MessageHandler(Filters.text & ~Filters.command, join_complete_pc_friend)],
                6: [MessageHandler(Filters.text & ~Filters.command, join_complete_pc_enemy)],
                7: [CallbackQueryHandler(join_complete_pc_action_selection)]
            },
            per_chat=False,
            fallbacks=[CommandHandler("cancel".casefold(), join_end),
                       CommandHandler("done".casefold(), join_end)],
            name="conv_join",
            persistent=True
        )
    )

    # -----------------------------------------START--------------------------------------------------------------------

    dispatcher.add_handler(CommandHandler("start".casefold(), start))

    # ------------------------------------------------------------------------------------------------------------------

    updater.start_polling(allowed_updates=Update.ALL_TYPES)
    updater.idle()


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
                                                                       inline=True))

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
    update.message.reply_text(placeholders["0"])

    return 0


def create_game_title(update: Update, context: CallbackContext) -> None:
    """
    Handles the choice of the Game's title and adds it to the Controller's games list

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: ConversationHandler.END
    """
    placeholders = get_lang(context, create_game_title.__name__)

    game_id = controller.add_game(update.message.chat_id, update.message.text)

    update.message.reply_text(placeholders["0"].format(update.message.text, game_id), parse_mode=ParseMode.HTML)

    return ConversationHandler.END


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

    context.user_data["join"]["game_name"] = update.message.text

    buttons = get_user_pc(context)
    buttons.append("as Master")
    context.user_data["join"]["message"] = update.message.reply_text(placeholders["1"], reply_markup=custom_kb(buttons))

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
        return ConversationHandler.END

    is_master = False
    if update.message.text.lower() == "as master":
        is_master = True
    controller.update_user_in_game(get_user_id(update), update.message.chat_id,
                                   context.user_data["join"]["game_name"], is_master)

    if is_master:
        update.message.reply_text(placeholders["0"].format(update.message.from_user.username,
                                                           context.user_data["join"]["game_name"]),
                                  parse_mode=ParseMode.HTML)
        update.message.delete()
        return end_conv(update, context)
    else:
        update.message.reply_text(placeholders["1"].format(update.message.from_user.username,
                                                           context.user_data["join"]["game_name"],
                                                           update.message.text),
                                  parse_mode=ParseMode.HTML,
                                  quote=False)

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
                                           reply_to_message_id=update.message.message_id,
                                           parse_mode=ParseMode.HTML)

    query_menu = update.message.bot.sendMessage(text=placeholders["1"], chat_id=user_id,
                                                reply_markup=custom_kb(placeholders["keyboard"],
                                                                       inline=True))

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
                                  btn_label="ability", lang_source="join_complete_pc")

        return 2
    else:
        invalid_state_choice(update, context, "join", placeholders)
        return 4


def join_complete_pc_dots(update: Update, context: CallbackContext) -> int:
    """
    If the user chooses a valid option, sends the information associated with this state ("Action dots")
    to store_value_and_update_kb method.

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

    context.user_data["join"]["message"].delete()
    context.user_data["join"]["message"] = context.bot.sendMessage(chat_id=get_user_id(update),
                                                                   text=placeholders["0"].format(
                                                                       7 - calc_total_dots(action_dots)),
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
            print("end")
            store_value_and_update_kb(update, context, tags=["join", "pc", "action_dots"], value=action_dots,
                                      btn_label="Action Dots", lang_source="join_complete_pc")
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
        auto_delete_message(context.bot.sendMessage(chat_id=get_user_id(update),
                                                    text="Sample Text Action Description",
                                                    ))
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
                                  lang_source="join_complete_pc")

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
                                  lang_source="join_complete_pc")

        return 2
    else:
        invalid_state_choice(update, context, "join", placeholders)
        return 6


def join_end(update: Update, context: CallbackContext) -> int:
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
    placeholders = get_lang(context, join_end.__name__)

    if "done".casefold() in command:
        if {"name", "alias", "look", "heritage", "background", "pc_class", "vice",
            "abilities", "action_dots", "friend", "enemy"}.issubset(
                context.user_data["join"]["pc"].keys()):

            controller.update_user_in_game(get_user_id(update), context.user_data["join"]["chat_id"],
                                           context.user_data["join"]["game_name"], pc=context.user_data["join"]["pc"])
        else:
            auto_delete_message(update.message.reply_text(placeholders["0"]))
            update.message.delete()
            return 0

    delete_conv_from_user_data(context, "join")

    return end_conv(update, context)


def delete_conv_from_user_data(context: CallbackContext, command: str):
    """
    Deletes the stored info in the user_data about the received command's conversation.

    :param context: instance of CallbackContext linked to the user.
    :param command: represents the the key of the conversaton in the user_data dict.
    """
    dict_command = context.user_data[command]
    try:
        dict_command["query_menu"].delete()
    except:
        pass

    try:
        dict_command["message"].delete()
    except:
        pass

    context.user_data.pop(command)


# ------------------------------------------conv_join-------------------------------------------------------------------


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


if __name__ == "__main__":
    start_bot()
