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

def create_pc_update_inline_keyboard(update: Update, context: CallbackContext, tag: str, wrapper_tag: str = None):
    """
    Update the Inline keyboard of the conv_createPC, according to the last section chosen and filled by the user.
    It also stores the last information received during the conversation.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :param tag: is the tag to check in the user_data.
    :param wrapper_tag: is an optional tag that wraps the tag.
    """
    placeholders = get_lang(context, create_pc.__name__)
    user_id = get_user_id(update)
    context.user_data["create_pc"]["message"].delete()

    if wrapper_tag is None:
        context.user_data.setdefault("create_pc", {}).setdefault("pc", {})[tag] = update.message.text
    else:
        context.user_data.setdefault("create_pc",
                                     {}).setdefault("pc",
                                                    {}).setdefault(wrapper_tag,
                                                                   {})[tag] = update.message.text

    updated_kb = context.user_data["create_pc"]["keyboard"]

    if tag == "description":
        tag = "notes"
    if tag == "pc_class":
        tag = "class"
    if wrapper_tag is not None:
        tag = wrapper_tag
    for i in range(len(updated_kb)):
        if tag in updated_kb[i].casefold():
            updated_kb[i] = tag.capitalize() + " ✅"

    query_menu = update.message.bot.sendMessage(text=placeholders["1"], chat_id=user_id,
                                                reply_markup=custom_kb(updated_kb, split_row=4, inline=True))

    context.user_data["create_pc"]["query_menu"] = query_menu


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
    context.user_data["create_pc"]["query_menu"] = query_menu

    return 0


def create_pc_state_switcher(update: Update, context: CallbackContext) -> int:
    """
    Handles the callback query from the Inline keyboard by redirecting the user in the correct state of the creation
    and sending him the associated message.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.:
    :return: next conversation's state.
    """
    placeholders = get_lang(context, create_pc_state_switcher.__name__)
    keyboard = context.user_data["create_pc"]["keyboard"]

    query = update.callback_query
    query.answer()

    choice = query.data

    for i in range(len(keyboard)):
        if choice == keyboard[i]:
            #context.bot.callback_data_cache.clear_callback_data()
            #context.bot.callback_data_cache.clear_callback_queries()
            user_id = query.from_user.id
            query.delete_message()
            context.user_data["create_pc"]["message"] = context.bot.sendMessage(chat_id=user_id,
                                                                                text=placeholders[str(i)],
                                                                                reply_markup=custom_kb(
                                                                                    placeholders[
                                                                                        "keyboard_" + str(i)]))
            return i + 1
    return 0


def create_pc_name(update: Update, context: CallbackContext) -> int:
    """
    Sends the tag associated with this state ("name") to create_pc_update_inline_keyboard method.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.:
    :return: the state of the conversation switcher.
    """
    # TODO: controllare se negli user_data se è gia presente un pc con questo nome? altrimenti come glieli mostriamo?
    create_pc_update_inline_keyboard(update, context, "name")
    update.message.delete()

    return 0


def create_pc_alias(update: Update, context: CallbackContext) -> int:
    """
    Sends the tag associated with this state ("alias") to create_pc_update_inline_keyboard method.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.:
    :return: the state of the conversation switcher.
    """
    create_pc_update_inline_keyboard(update, context, "alias")
    update.message.delete()

    return 0


def create_pc_look(update: Update, context: CallbackContext) -> int:
    """
    Sends the tag associated with this state ("look") to create_pc_update_inline_keyboard method.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.:
    :return: the state of the conversation switcher.
    """
    create_pc_update_inline_keyboard(update, context, "look")
    update.message.delete()

    return 0


def create_pc_heritage(update: Update, context: CallbackContext) -> int:
    """
    Sends the tag associated with this state ("heritage") to create_pc_update_inline_keyboard method.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.:
    :return: the state of the conversation switcher.
    """
    create_pc_update_inline_keyboard(update, context, "heritage")
    update.message.delete()

    return 0


def create_pc_background(update: Update, context: CallbackContext) -> int:
    """
    Sends the tag associated with this state ("background") to create_pc_update_inline_keyboard method.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.:
    :return: the state of the conversation switcher.
    """
    create_pc_update_inline_keyboard(update, context, "background")
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

    context.user_data.setdefault("create_pc",
                                 {}).setdefault("pc",
                                                {}).setdefault("vice",
                                                               {})["name"] = update.message.text

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
    context.user_data.setdefault("create_pc",
                                 {}).setdefault("pc",
                                                {}).setdefault("vice",
                                                               {})["description"] = update.message.text

    placeholders = get_lang(context, create_pc_vice_description.__name__)

    context.user_data["create_pc"]["message"].edit_text(placeholders["0"])
    update.message.delete()

    return 10


def create_pc_vice_purveyor(update: Update, context: CallbackContext) -> int:
    """
    Sends the tags associated with this state ("vice" and "purveyor") to create_pc_update_inline_keyboard method.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.:
    :return: the state of the conversation switcher.
    """
    create_pc_update_inline_keyboard(update, context, "purveyor", "vice")
    update.message.delete()

    return 0


def create_pc_description(update: Update, context: CallbackContext) -> int:
    """
    Sends the tag associated with this state ("description") to create_pc_update_inline_keyboard method.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.:
    :return: the state of the conversation switcher.
    """
    create_pc_update_inline_keyboard(update, context, "description")
    update.message.delete()

    return 0


def create_pc_class(update: Update, context: CallbackContext) -> int:
    """
    Calls a DBmanager method to check if the received class exists and, if so,
    sends the tag associated with this state ("class") to create_pc_update_inline_keyboard method.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the state of the conversation switcher.
    """
    placeholders = get_lang(context, create_pc_class.__name__)

    if exists_character(update.message.text):
        create_pc_update_inline_keyboard(update, context, "pc_class")
        update.message.delete()

        return 0
    else:
        context.user_data["create_pc"]["message"].delete()
        message = update.message.reply_text(placeholders["0"])
        auto_delete_message(message, 5.0)
        context.user_data["create_pc"]["message"] = update.message.reply_text(text=placeholders["1"])
        update.message.delete()
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

    if "done".casefold() in command:
        if {"name", "alias", "look", "heritage", "background", "pc_class", "vice"}.issubset(
                context.user_data["create_pc"]["pc"].keys()):
            context.user_data.setdefault("myPCs", []).append(context.user_data["create_pc"]["pc"])
        else:
            update.message.reply_text(placeholders["0"])
            return 0

    try:
        context.user_data["create_pc"]["query_menu"].delete()
    except:
        pass

    try:
        context.user_data["create_pc"]["message"].delete()
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

    print(controller.games)
    return ConversationHandler.END


# ------------------------------------------conv_createGame------------------------------------------------------------


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
