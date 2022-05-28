from threading import Thread
import time
from typing import *

from telegram.ext import *
from telegram import *
from telegram.error import BadRequest
from controller.DBreader import *
from controller.DBwriter import *
from utility.FilesManager import *
from controller.Controller import Controller

# instantiates the Controller.
controller = Controller()

# loading of default language dict.
with open(path_finder('ENG.json'), 'r', encoding="utf8") as lang_f:
    default_lang = json.load(lang_f)["Bot"]

# loading the dice stickers dict.
with open(path_finder('stickers/dice.json'), 'r', encoding="utf8") as dice_f:
    dice_stickers = json.load(dice_f)


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


def is_user_not_in_game(update: Update, message_text: str) -> bool:
    """
    Checks if the user is in a game.

    :param update: update: instance of Update sent by the user.
    :param message_text: the error text to send the user if he is not in a game.
    :return: True if the user is NOT in a game, False otherwise.
    """
    if query_game_of_user(update.message.chat_id, get_user_id(update)) is None:
        update.message.reply_text(message_text, parse_mode=ParseMode.HTML)
        return True
    return False


def is_game_in_wrong_phase(update: Update, context: CallbackContext, message_text: str, phase: int = 0) -> bool:
    """
    Checks if the user's game is in the wrong phase to call a certain command
    (also checks if he even is in a game calling is_user_not_in_game()).

    :param update: update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :param message_text: the error text to send the user if he is not in a game.
    :param phase: the phase where the user's game should not be in order to use a specific commmand.
    :return: True if the user's game is in the specified wrong phase or the INIT phase,
        and he cannot perform the selected command, False otherwise
    """
    placeholders = get_lang(context, is_game_in_wrong_phase.__name__)

    if is_user_not_in_game(update, message_text):
        return True

    game_state = controller.get_game_state(query_game_of_user(update.message.chat_id, get_user_id(update)))
    if game_state == phase or game_state == 0:
        update.message.reply_text(placeholders[str(game_state)].format(update.message.text), parse_mode=ParseMode.HTML)
        return True

    return False


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


def custom_kb(buttons: List[str], inline: bool = False, split_row: int = None,
              callback_data: List[Union[str, int]] = None,
              selective: bool = True, input_field_placeholder: str = None) -> ReplyMarkup:
    """
    Builds a parametric customized keyboard.

    :param buttons: list of buttons' labels. If empty a ReplyKeyboardRemove object is returned.
    :param inline: False if the custom keyboard should be a ReplyKeyboardMarkup, True if an InlineKeyboard.
    :param split_row: specifies the number of buttons per row. If not specified it is automatically calculated.
    :param callback_data: list of callback_data associated to each button.
    If the length of this list differs from the length of the buttons list,
    the button list is used also for callback_data.
    :param selective: True if the KB should be sent only to the user in conversation, False otherwise.
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
    return ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, selective=selective,
                               input_field_placeholder=input_field_placeholder)


def build_plus_minus_keyboard(central_buttons: List[str], back_button: bool = True, done_button: bool = False,
                              inline: bool = True, split_row: int = 3) -> ReplyMarkup:
    """
    Builds a custom keyboard with buttons surrounded with others buttons with + and - symbols.

    :param central_buttons: list of the central buttons.
    :param back_button: True if the BACK button must be added at the end of the keyboard, False otherwise.
    :param done_button: True if the DONE button must be added at the end of the keyboard, False otherwise.
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

    if done_button:
        buttons.append("\u2611\uFE0F DONE")
        callbacks.append("DONE")

    return custom_kb(buttons, inline, split_row, callbacks)


def build_multi_page_kb(object_buttons: List[str], inline: bool = True):
    buttons = []
    callbacks = []

    for button in object_buttons:
        buttons.append(button)
        buttons.append("✅")

        callbacks.append(button)
        callbacks.append(button + "$")

    buttons.append("\u2B05\uFE0F")
    buttons.append("\u27A1\uFE0F")
    callbacks.append("LEFT")
    callbacks.append("RIGHT")

    return custom_kb(buttons, inline, 2, callbacks)


def store_value_and_update_kb(update: Update, context: CallbackContext, tags: List[str], value: Union[str, dict, list],
                              lang_source: str = None, btn_label: str = None, split_row: int = None,
                              reply_in_group: bool = False):
    """
    Update the Inline keyboard of the conversation, according to the last section chosen and filled by the user.
    It also stores the last information received during the conversation.
    It calls add_tag_in_telegram_data and update_inline_keyboard.


    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :param tags: the list of tags representing the target key dict in user_data.
    :param value: the value to store in the target dict.
    :param lang_source: the tag representing the target dict in the language dictionary.
            If None the first element of tags' list is used.
    :param btn_label: the text of the selected button.
            If None the last element of tags' list is used.
    :param split_row: specifies the number of buttons per row. If not specified it is automatically calculated.
    :param reply_in_group: the id of the chat where the messages need to be sent.
        If None the message is sent to the user's private chat
    """
    if btn_label is None:
        btn_label = tags[-1]
    if lang_source is None:
        lang_source = tags[0]

    add_tag_in_telegram_data(context, tags, value)
    update_inline_keyboard(update, context, tags[0], btn_label, lang_source, split_row, reply_in_group)


def add_tag_in_telegram_data(context: CallbackContext, tags: List[str], value: Any,
                             location: str = "user"):
    """
    Stores the passed value in the target dict.

    :param context: instance of CallbackContext linked to the user.
    :param tags: the list of tags representing the target key dict in user_data.
    :param value: the value to store in the target dict.
    :param location: specifies the dict in the telegram data ("user", "chat" or "bot"). By default it's user_data.
    """

    if location.casefold() == "chat":
        pointer = context.chat_data
    elif location.casefold() == "bot":
        pointer = context.bot_data
    else:
        pointer = context.user_data

    for i in range(len(tags) - 1):
        pointer.setdefault(tags[i], {})
        pointer = pointer[tags[i]]
    pointer[tags[-1]] = value


def update_inline_keyboard(update: Update, context: CallbackContext, command: str, btn_label: str,
                           lang_source: str, split_row: int = None, reply_in_group: bool = False):
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
    :param reply_in_group: the id of the chat where the messages need to be sent.
        If None the message is sent to the user's private chat
    """
    context.user_data[command]["message"].delete()
    placeholders = get_lang(context, lang_source)

    updated_kb = context.user_data[command]["keyboard"]

    for i in range(len(updated_kb)):
        if btn_label.lower() in updated_kb[i].lower():
            updated_kb[i] = btn_label.capitalize() + " ✅"

    if not reply_in_group:
        query_menu = context.bot.sendMessage(text=placeholders["1"], chat_id=get_user_id(update),
                                             reply_markup=custom_kb(updated_kb, split_row=split_row, inline=True))
    else:
        query_menu = context.user_data[command]["invocation_message"].reply_text(text=placeholders["1"],
                                                                                 reply_markup=custom_kb(
                                                                                     updated_kb,
                                                                                     split_row=split_row,
                                                                                     inline=True))

    context.user_data[command]["query_menu"] = query_menu


def update_bonus_dice_kb(context: CallbackContext, tags: List[str], tot_dice: int, location: str = "chat",
                         message_tag: str = "message", button_tag: str = "button"):
    """
    Utility method to update the InlineKeyboard of a bonus dice request.
    Edits the message with the current total number of dice and the kb button with the number of bonus dice selected.

    :param location: specifies the dict in the telegram data ("user", "chat" or "bot"). By default it's chat_data.
    :param tags: list of tag to get the bonus dice.
    :param tot_dice: total amount of dice to roll.
    :param message_tag: is the tag of the dict to use for the message text.
    :param button_tag: is the tag of the dict to use for the button text.
    :param context: instance of CallbackContext linked to the user.
    """

    if location.casefold() == "user":
        pointer = context.user_data
    elif location.casefold() == "bot":
        pointer = context.bot_data
    else:
        pointer = context.chat_data

    bonus_dice = pointer
    for i in range(len(tags)):
        bonus_dice = bonus_dice[tags[i]]

    bonus_dice_lang = get_lang(context, "bonus_dice")

    pointer[tags[0]]["query_menu"].edit_text(bonus_dice_lang[message_tag].format(tot_dice),
                                             reply_markup=build_plus_minus_keyboard(
                                                 [bonus_dice_lang[button_tag].format(bonus_dice)],
                                                 done_button=True,
                                                 back_button=False),
                                             parse_mode=ParseMode.HTML)


def action_roll_calc_total_dice(ar_info: dict) -> int:
    """
    Utility method to calculate the amount of dice that will be rolled for the action roll.

    :param ar_info: the dictionary containing all the necessary action roll's information.
    :return: the actual amount of dice.
    """
    total = 0

    total += int(ar_info["action"].split(": ")[1])

    if ar_info["push"]:
        total += 1
    if "devil_bargain" in ar_info:
        total += 1
    if "assistants" in ar_info:
        total += len(ar_info["assistants"])
    if "cohort" in ar_info:
        total += int(ar_info["cohort"][1])

    total += ar_info["bonus_dice"]

    return total


def resistance_roll_calc_total_dice(rr_info: dict) -> int:
    """
    Utility method to calculate the amount of dice that will be rolled for the resistance roll.

    :param rr_info: the dictionary containing all the necessary resistance roll's information.
    :return: the actual amount of dice.
    """
    return rr_info["bonus_dice"] + int(rr_info["attribute"].split(": ")[1])


def group_action_calc_total_dice(update: Update, context: CallbackContext) -> int:
    """
    Utility method to calculate the amount of dice that will be rolled for the group action.

    :param update: instance of Update sent by the user.
    :param context: instance of CallbackContext linked to the user.
    :return: the actual amount of dice.
    """
    total = 0

    pc_name = context.chat_data["action_roll"]["group_action"][0][1]

    total += controller.get_pc_action_rating(get_user_id(update), update.effective_message.chat_id, pc_name,
                                             context.chat_data["action_roll"]["roll"]["action"].split(":")[0])[1]

    ar_info = context.chat_data["action_roll"]["roll"]["participants"][pc_name]

    if ar_info["push"]:
        total += 1
    if "devil_bargain" in ar_info:
        total += 1

    total += ar_info["bonus_dice"]

    return total


def query_state_switcher(update: Update, context: CallbackContext, conversation: str, placeholders: dict,
                         keyboards: List[List[str]], index_inlines: List[int] = None, starting_state: int = 1,
                         split_inline_row: int = None,
                         reply_in_group: bool = False) -> int:
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
    :param split_inline_row: specifies the number of buttons per row for the inline keyboards only.
        If not specified it is automatically calculated.
    :param reply_in_group: the id of the chat where the messages need to be sent.
        If None the message is sent to the user's private chat
    :return: the next state of the specified conversation.
    """
    if index_inlines is None:
        index_inlines = []

    query = update.callback_query
    query.answer()

    choice = query.data

    keyboard = context.user_data[conversation]["keyboard"]

    for i in range(len(keyboard)):
        split_row = None
        inline = False
        if choice == keyboard[i]:
            if i in index_inlines:
                inline = True
                split_row = split_inline_row
            query.delete_message()
            if not reply_in_group:
                context.user_data[conversation]["message"] = context.bot.sendMessage(chat_id=get_user_id(update),
                                                                                     text=placeholders[str(i)],
                                                                                     reply_markup=custom_kb(
                                                                                         keyboards[i], inline=inline,
                                                                                         split_row=split_row))
            else:
                context.user_data[conversation]["message"] = \
                    context.user_data[conversation]["invocation_message"].reply_text(text=placeholders[str(i)],
                                                                                     reply_markup=custom_kb(
                                                                                         keyboards[i], inline=inline,
                                                                                         split_row=split_row))

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

    try:
        message = update.effective_message.reply_text(placeholders["0"], reply_markup=ReplyKeyboardRemove())
    except:
        message = context.bot.send_message(chat_id=update.effective_message.chat_id, text=placeholders["0"],
                                           reply_markup=ReplyKeyboardRemove())

    auto_delete_message(update.effective_message, 3.0)

    auto_delete_message(message, 3.0)
    return ConversationHandler.END


def delete_conv_from_telegram_data(context: CallbackContext, command: str, location: str = "user"):
    """
    Deletes the stored info in the user_data about the received command's conversation.

    :param context: instance of CallbackContext linked to the user.
    :param command: represents the the key of the conversaton in the user_data dict.
    :param location: specifies the dict in the telegram data ("user", "chat" or "bot"). By default it's user_data.
    """
    if location.casefold() == "chat":
        pointer = context.chat_data
    elif location.casefold() == "bot":
        pointer = context.bot_data
    else:
        pointer = context.user_data

    if command not in pointer:
        return

    dict_command = pointer[command]
    try:
        dict_command["query_menu"].delete()
    except:
        pass

    try:
        dict_command["message"].delete()
    except:
        pass

    pointer.pop(command)


def auto_delete_message(message: Message, timer: Union[float, str] = 5.0) -> None:
    """
    Delete the given message after the specified amount of time (in seconds)
    running a separate Thread using a self-contained function.

    :param message: the message to delete
    :param timer: the time to wait before the deletion.
    """
    if isinstance(timer, str):
        timer = len(timer) / 14

    def execute(m: Message, t: float) -> None:
        time.sleep(t)
        try:
            m.delete()
        except:
            pass

    Thread(target=execute, args=(message, timer)).start()
