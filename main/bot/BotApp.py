from bot.BotCallbacks import *


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

    dispatcher.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler("createCrew".casefold(), create_crew)],
            states={
                0: [MessageHandler(Filters.text & ~Filters.command, create_crew_type)],
                1: [CallbackQueryHandler(create_crew_state_switcher)],
                2: [MessageHandler(Filters.text & ~Filters.command, create_crew_name)],
                3: [MessageHandler(Filters.text & ~Filters.command, create_crew_reputation)],
                4: [MessageHandler(Filters.text & ~Filters.command, create_crew_description)],
                5: [MessageHandler(Filters.text & ~Filters.command, create_crew_lair_location)],
                6: [CallbackQueryHandler(create_crew_upgrades)],
                7: [MessageHandler(Filters.text & ~Filters.command, create_crew_ability)],
                8: [MessageHandler(Filters.text & ~Filters.command, create_crew_contact)],
                9: [MessageHandler(Filters.text & ~Filters.command, create_crew_lair_description)],
                10: [CallbackQueryHandler(create_crew_upgrade_selection)],
            },
            fallbacks=[CommandHandler("cancel".casefold(), create_crew_end),
                       CommandHandler("done".casefold(), create_crew_end)],
            name="conv_createCrew",
            persistent=True
        )
    )

    dispatcher.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler(["changeState".casefold(), "setState".casefold(), "state".casefold()],
                                         change_state)],
            states={
                0: [CallbackQueryHandler(change_state_choice)],
            },
            fallbacks=[CommandHandler("cancel".casefold(), change_state_end)],
            name="conv_changeState",
            persistent=True
        )
    )

    dispatcher.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler("actionRoll".casefold(), action_roll)],
            states={
                0: [MessageHandler(Filters.text & ~Filters.command, end_conv)],
            },
            fallbacks=[CommandHandler("cancel".casefold(), end_conv)],
            name="conv_actionRoll",
            persistent=True
        )
    )

    # -----------------------------------------START--------------------------------------------------------------------

    dispatcher.add_handler(CommandHandler("start".casefold(), start))

    # ------------------------------------------------------------------------------------------------------------------

    updater.start_polling(allowed_updates=Update.ALL_TYPES)
    updater.idle()


if __name__ == "__main__":
    start_bot()
