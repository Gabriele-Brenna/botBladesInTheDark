from typing import *

from telegram.ext import *
from telegram import *
from telegram.utils import helpers

from controller.DBreader import *
from controller.DBwriter import *
from utility.FilesManager import *


# loading of default language dict
with open(path_finder('Eng.json'), 'r', encoding="utf8") as lang_f:
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
    # TODO: remove after testing

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
        if isinstance(update.message.from_user["id"], int):
            return update.message.from_user["id"]


def test(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Test done")
    print("TEST")
    print("Sender: " + str(update.message.from_user["id"]))
    print("-----------------user_data----------------------------------------------------")
    print(context.user_data)
    print("------------------------------------------------------------------------------")
    print("-----------------chat_data----------------------------------------------------")
    print(context.chat_data)
    print("------------------------------------------------------------------------------")
    print("-----------------bot_data----------------------------------------------------")
    print(context.bot_data)
    print("------------------------------------------------------------------------------")


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

    dispatcher.add_handler(CommandHandler("login", start_login))
    dispatcher.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler("start", login, Filters.regex("login-BladesInTheDark-BotTelegram"))],
            states={
                0: [MessageHandler(Filters.text & ~Filters.command, login_receive_username)],
            },
            fallbacks=[CommandHandler("cancel", cancel)],
            name="conv_login",
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
        update.message.reply_text(placeholders["commands"][context.args[0]], parse_mode=ParseMode.HTML)


def cancel(update: Update, context: CallbackContext) -> int:
    """
    Handles the abort of a conversation.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: ConversationHandler.END
    """
    placeholders = get_lang(context, cancel.__name__)

    update.message.reply_text(placeholders["0"], reply_markup=ReplyKeyboardRemove(), timeout=5)
    return ConversationHandler.END


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
