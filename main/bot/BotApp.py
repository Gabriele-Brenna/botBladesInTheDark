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

    dispatcher.add_handler(CommandHandler(["myPC".casefold(), "PCsheet".casefold(), "myPCsheet".casefold(),
                                           "activePC".casefold(), "characterSheet".casefold()], send_character_sheet))
    dispatcher.add_handler(CommandHandler(["myCrew".casefold(), "CrewSheet".casefold(), "myCrewsheet".casefold()],
                                          send_crew_sheet))

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
            entry_points=[CommandHandler(["pcSelection".casefold(), "switchPC".casefold(), "changePC".casefold()],
                                         pc_selection)],
            states={
                0: [CallbackQueryHandler(pc_selection_choice)],
            },
            fallbacks=[CommandHandler("cancel".casefold(), pc_selection_end)],
            name="conv_pcSelection",
            persistent=True
        )
    )

    dispatcher.add_handler(CommandHandler("roll".casefold(), roll_dice))

    dispatcher.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler(["actionRoll".casefold(), "ar".casefold()], action_roll),
                          CommandHandler(["groupActionCohort".casefold(), "leadCohort".casefold(), "lC".casefold()],
                                         group_action_cohort),
                          CommandHandler(["groupAction".casefold(), "leadAction".casefold(), "ga".casefold()],
                                         group_action)],
            states={
                10: [CallbackQueryHandler(group_action_cohort_choice)],
                0: [ConversationHandler(
                    entry_points=[MessageHandler(Filters.text & ~Filters.command, action_roll_goal)],
                    states={
                        0: [MessageHandler(Filters.text & ~Filters.command, action_roll_rating)]
                    },
                    fallbacks=[CommandHandler("cancel".casefold(), action_roll_end)],
                    name="player_conv_actionRoll1",
                    persistent=True,
                    map_to_parent={
                        ConversationHandler.END: ConversationHandler.END,
                        1: 1
                    }
                )],
                1: [ConversationHandler(
                    entry_points=[CommandHandler("reply_action_roll".casefold(), master_reply)],
                    states={
                        0: [MessageHandler(Filters.text & ~Filters.command, action_roll_position)],
                        1: [MessageHandler(Filters.text & ~Filters.command, action_roll_effect)]
                    },
                    fallbacks=[CommandHandler("cancel".casefold(), action_roll_end)],
                    name="master_conv_actionRoll",
                    persistent=True,
                    map_to_parent={
                        ConversationHandler.END: ConversationHandler.END,
                        2: 2,
                        20: 20
                    }
                )],
                2: [ConversationHandler(
                    entry_points=[CallbackQueryHandler(action_roll_bargains)],
                    states={
                        0: [MessageHandler(Filters.text & ~Filters.command, action_roll_devil_bargains)],
                        1: [CallbackQueryHandler(action_roll_bonus_dice)],
                        2: [MessageHandler(Filters.text & ~Filters.command, action_roll_notes)]
                    },
                    fallbacks=[CommandHandler("cancel".casefold(), action_roll_end)],
                    name="player_conv_actionRoll2",
                    persistent=True,
                    map_to_parent={
                        ConversationHandler.END: ConversationHandler.END
                    }
                )],
                20: [ConversationHandler(
                    entry_points=[CallbackQueryHandler(group_action_bargains)],
                    states={
                        0: [MessageHandler(Filters.text & ~Filters.command, action_roll_devil_bargains)],
                        1: [CallbackQueryHandler(group_action_bonus_dice)]
                    },
                    fallbacks=[CommandHandler("cancel".casefold(), action_roll_end)],
                    name="player_conv_groupAction",
                    persistent=True,
                    map_to_parent={
                        20: 20,
                        2: 2,
                        ConversationHandler.END: ConversationHandler.END
                    }
                )]
            },
            fallbacks=[CommandHandler("cancel".casefold(), action_roll_end),
                       CommandHandler("assist".casefold(), action_roll_assistance),
                       CommandHandler("unite".casefold(), group_action_participate)],
            name="conv_actionRoll",
            per_user=False,
            persistent=True
        )
    )

    dispatcher.add_handler(CommandHandler(["journal".casefold(), "log".casefold()], send_journal))
    dispatcher.add_handler(CommandHandler(["map".casefold(), "DoskvolMap".casefold()], send_map))

    dispatcher.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler("addCohort".casefold(), add_cohort)],
            states={
                0: [CallbackQueryHandler(add_cohort_choice)],
                1: [MessageHandler(Filters.text & ~Filters.command, add_cohort_type)],
                2: [MessageHandler(Filters.text & ~Filters.command, add_cohort_edgflaw_num)],
                3: [MessageHandler(Filters.text & ~Filters.command, add_cohort_edges)],
                4: [MessageHandler(Filters.text & ~Filters.command, add_cohort_flaws)],
            },
            fallbacks=[CommandHandler("cancel".casefold(), add_cohort_end)],
            name="conv_addCohort",
            persistent=True
        )
    )

    dispatcher.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler(["createClock".casefold(), "newClock".casefold(), "addClock".casefold()],
                                         create_clock),
                          CommandHandler("createClock_longTermProject", create_project_clock)],
            states={
                0: [MessageHandler(Filters.text & ~Filters.command, create_clock_name)],
                1: [MessageHandler(Filters.text & ~Filters.command, create_clock_segments)],
            },
            fallbacks=[CommandHandler("cancel".casefold(), create_clock_end)],
            name="conv_createClock",
            persistent=True
        )
    )

    dispatcher.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler(["tick".casefold(), "tickClock".casefold(), "advanceClock".casefold()],
                                         tick_clock)],
            states={
                0: [CallbackQueryHandler(tick_clock_choice)],
                1: [MessageHandler(Filters.text & ~Filters.command, tick_clock_progress)],
            },
            fallbacks=[CommandHandler("cancel".casefold(), tick_clock_end)],
            name="conv_tickClock",
            persistent=True
        )
    )

    dispatcher.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler(["addClaim".casefold(), "newClaim".casefold()],
                                         add_claim)],
            states={
                0: [CallbackQueryHandler(add_claim_type)],
                1: [CallbackQueryHandler(add_claim_name)]
            },
            fallbacks=[CommandHandler("cancel".casefold(), add_claim_end)],
            name="conv_addClaim",
            persistent=True
        )
    )

    dispatcher.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler(["resistanceRoll".casefold(), "rr".casefold()], resistance_roll)],
            states={
                0: [MessageHandler(Filters.text & ~Filters.command, resistance_roll_description)],
                1: [ConversationHandler(
                    entry_points=[CommandHandler(["reply_resistance_roll".casefold()], master_reply)],
                    states={
                        0: [CallbackQueryHandler(resistance_roll_damage)],
                        1: [CallbackQueryHandler(resistance_roll_attribute)]
                    },
                    fallbacks=[CommandHandler("cancel".casefold(), resistance_roll_end)],
                    name="master_conv_resistanceRoll",
                    persistent=True,
                    map_to_parent={
                        2: 2,
                        ConversationHandler.END: ConversationHandler.END
                    }
                )],
                2: [ConversationHandler(
                    entry_points=[CallbackQueryHandler(resistance_roll_bonus_dice)],
                    states={
                        0: [MessageHandler(Filters.text & ~Filters.command, resistance_roll_notes)]
                    },
                    fallbacks=[CommandHandler("cancel".casefold(), resistance_roll_end)],
                    name="user_conv_resistanceRoll",
                    persistent=True,
                    map_to_parent={
                        2: 2,
                        ConversationHandler.END: ConversationHandler.END
                    }
                )]
            },
            fallbacks=[CommandHandler("cancel".casefold(), resistance_roll_end)],
            name="conv_resistanceRoll",
            persistent=True,
            per_user=False
        )
    )

    dispatcher.add_handler(CommandHandler(["addStress", "stress".casefold()], add_stress))

    dispatcher.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler(["addTrauma", "trauma".casefold()], add_trauma)],
            states={
                0: [MessageHandler(Filters.text & ~Filters.command, add_trauma_name)],
            },
            fallbacks=[CommandHandler("cancel".casefold(), add_trauma_end)],
            name="conv_addTrauma",
            persistent=True
        )
    )

    dispatcher.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler(["score".casefold(), "newScore".casefold()], score)],
            states={
                0: [ConversationHandler(
                    entry_points=[MessageHandler(Filters.text & ~Filters.command, score_category)],
                    states={
                        0: [CallbackQueryHandler(score_target)],
                        1: [CallbackQueryHandler(score_target_selection)],
                        2: [MessageHandler(Filters.text & ~Filters.command, score_target_custom)],
                        3: [MessageHandler(Filters.text & ~Filters.command, score_plan_type)],
                        4: [MessageHandler(Filters.text & ~Filters.command, score_plan_details)],
                        5: [MessageHandler(Filters.text & ~Filters.command, score_title)]
                    },
                    fallbacks=[CommandHandler("cancel".casefold(), score_end)],
                    map_to_parent={
                        ConversationHandler.END: ConversationHandler.END,
                        6: 1
                    },
                    name="conv_score_creator1",
                    persistent=True
                )],
                1: [MessageHandler(Filters.text & ~Filters.command, score_pcs_loads)],
                2: [ConversationHandler(
                    entry_points=[CallbackQueryHandler(score_engagement)],
                    states={
                        0: [CallbackQueryHandler(score_engagement)],
                        1: [MessageHandler(Filters.text & ~Filters.command, score_notes)]
                    },
                    fallbacks=[CommandHandler("cancel".casefold(), score_end)],
                    map_to_parent={
                        ConversationHandler.END: ConversationHandler.END
                    },
                    name="conv_score_creator2",
                    persistent=True

                )]
            },
            fallbacks=[CommandHandler("cancel".casefold(), score_end),
                       CommandHandler("load".casefold(), score_load)],
            name="conv_score",
            per_user=False,
            persistent=True
        )
    )

    dispatcher.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler(["heat".casefold()], heat)],
            states={
                0: [CallbackQueryHandler(heat_score_nature)],
                1: [CallbackQueryHandler(heat_target_profile)],
                2: [CallbackQueryHandler(heat_turf_hostility)],
                3: [CallbackQueryHandler(heat_war_situation)],
                4: [CallbackQueryHandler(heat_killing)],
                5: [CallbackQueryHandler(heat_extra)]
            },
            fallbacks=[CommandHandler("cancel".casefold(), heat_end)],
            name="conv_heat",
            persistent=True
        )
    )

    dispatcher.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler(["entanglement".casefold(), "ent".casefold()], entanglement),
                          CommandHandler(["secretEntanglement".casefold(), "secretEnt".casefold()],
                                         secret_entanglement)],
            states={
                0: [MessageHandler(Filters.text & ~Filters.command, entanglement_name)],
                1: [MessageHandler(Filters.text & ~Filters.command, entanglement_description)],
            },
            fallbacks=[CommandHandler("cancel".casefold(), entanglement_end)],
            name="conv_entanglement",
            persistent=True,
            per_chat=False
        )
    )

    dispatcher.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler(["endScore".casefold(), "scoreEnd".casefold()], end_score)],
            states={
                0: [MessageHandler(Filters.text & ~Filters.command, end_score_outcome)],
                1: [MessageHandler(Filters.text & ~Filters.command, end_score_notes)],
                2: [CallbackQueryHandler(end_score_rep)]
            },
            fallbacks=[CommandHandler("cancel".casefold(), end_score_end)],
            name="conv_end_score",
            persistent=True
        )
    )

    dispatcher.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler(["payoff".casefold(), "payment".casefold()], payoff)],
            states={
                0: [MessageHandler(Filters.text & ~Filters.command, payoff_amount)],
                1: [CallbackQueryHandler(payoff_choice)],
                2: [MessageHandler(Filters.text & ~Filters.command, payoff_notes)]
            },
            fallbacks=[CommandHandler("cancel".casefold(), payoff_end)],
            name="conv_payoff",
            persistent=True
        )
    )

    dispatcher.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler(["useArmor".casefold(), "armorUse".casefold()], armor_use)],
            states={
                0: [CallbackQueryHandler(armor_use_type)],
                1: [MessageHandler(Filters.text & ~Filters.command, armor_use_description)]
            },
            fallbacks=[CommandHandler("cancel".casefold(), armor_use_end)],
            name="conv_armor_use",
            persistent=True
        )
    )

    dispatcher.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler(["useItem".casefold(), "ui".casefold()], use_item)],
            states={
                0: [CallbackQueryHandler(use_item_name)],
                1: [MessageHandler(Filters.text & ~Filters.command, use_item_description)]
            },
            fallbacks=[CommandHandler("cancel".casefold(), use_item_end)],
            name="conv_use_item",
            persistent=True
        )
    )

    dispatcher.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler(["coin".casefold(), "addCoin".casefold()], add_coin)],
            states={
                0: [CallbackQueryHandler(add_coin_amount)]
            },
            fallbacks=[CommandHandler("cancel".casefold(), add_coin_end)],
            name="conv_add_coin",
            persistent=True
        )
    )

    dispatcher.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler(
                ["vaultCapacity".casefold(), "setVaultCapacity".casefold(), "setVault".casefold(), "vault".casefold()],
                vault_capacity
            )],
            states={
                0: [CallbackQueryHandler(vault_capacity_kb)]
            },
            fallbacks=[CommandHandler("cancel".casefold(), vault_capacity_end)],
            name="conv_vault_capacity",
            persistent=True
        )
    )

    dispatcher.add_handler(CommandHandler(["upgradeCrew".casefold(), "addCrewTier".casefold(),
                                           "upCrew".casefold()], upgrade_crew))

    dispatcher.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler(["factionsStatus".casefold(), "factions".casefold()], factions_status)],
            states={
                0: [CallbackQueryHandler(factions_status_selection)],
                1: [CallbackQueryHandler(factions_status_update)]
            },
            fallbacks=[CommandHandler("cancel".casefold(), factions_status_end)],
            name="conv_factions_status",
            persistent=True
        )
    )

    dispatcher.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler(["fortuneRoll".casefold(), "fortune".casefold(), "fr".casefold()],
                                         fortune_roll)],
            states={
                0: [MessageHandler(Filters.text & ~Filters.command, fortune_roll_goal)],
                1: [CallbackQueryHandler(fortune_roll_choice)],
                2: [CallbackQueryHandler(fortune_roll_what)],
                3: [CallbackQueryHandler(fortune_roll_bonus_dice)],
                4: [MessageHandler(Filters.text & ~Filters.command, fortune_roll_notes)],
                10: [CallbackQueryHandler(fortune_roll_action)],
                20: [CallbackQueryHandler(fortune_roll_faction)],
                30: [CallbackQueryHandler(fortune_roll_item)]
            },
            fallbacks=[CommandHandler("cancel".casefold(), fortune_roll_end)],
            name="conv_fortuneRoll",
            persistent=True
        )
    )

    dispatcher.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler(["addExp".casefold(), "exp".casefold()], add_exp)],
            states={
                0: [CallbackQueryHandler(add_exp_amount)]
            },
            fallbacks=[CommandHandler("cancel".casefold(), add_exp_end)],
            name="conv_add_exp",
            persistent=True
        )
    )

    dispatcher.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler(["addDots".casefold(), "addActionDots".casefold(), "dots".casefold(),
                                          "spendActionPoints".casefold(), "ap".casefold(), "ad".casefold()],
                                         add_action_dots)],
            states={
                0: [CallbackQueryHandler(add_action_dots_attribute_selection)],
                1: [CallbackQueryHandler(add_action_dots_keyboard)]
            },
            fallbacks=[CommandHandler("cancel".casefold(), factions_status_end)],
            name="conv_add_action_dots",
            persistent=True
        )
    )

    dispatcher.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler(["downtime".casefold(), "downtimeActivity".casefold(),
                                          "dtActivity".casefold()], downtime)],
            states={
                0: [CallbackQueryHandler(downtime_choice)],
                1: [MessageHandler(Filters.text & ~Filters.command, downtime_notes)],
                10: [MessageHandler(Filters.text & ~Filters.command, downtime_asset)],
                20: [MessageHandler(Filters.text & ~Filters.command, downtime_item)],
                30: [CallbackQueryHandler(downtime_project_choice)],
                40: [ConversationHandler(
                    entry_points=[CallbackQueryHandler(downtime_recover_choice)],
                    states={
                        1: [CallbackQueryHandler(downtime_bonus_dice)],
                        41: [CallbackQueryHandler(downtime_npc_selection)],
                        42: [CallbackQueryHandler(downtime_pc_selection)],
                        43: [CallbackQueryHandler(downtime_cohort_choice)]
                    },
                    fallbacks=[CommandHandler("cancel".casefold(), downtime_end)],
                    name="conv_Recover",
                    persistent=True,
                    map_to_parent={
                        2: 1,
                        ConversationHandler.END: ConversationHandler.END
                    }
                )],
                50: [ConversationHandler(
                    entry_points=[CallbackQueryHandler(downtime_attribute_choice)],
                    states={
                        0: [CallbackQueryHandler(downtime_action_choice)],
                        1: [CallbackQueryHandler(downtime_bonus_dice)]
                    },
                    fallbacks=[CommandHandler("cancel".casefold(), downtime_end)],
                    name="conv_ReduceHeat",
                    persistent=True,
                    map_to_parent={
                        2: 1,
                        ConversationHandler.END: ConversationHandler.END
                    }
                )],
                60: [CallbackQueryHandler(downtime_attribute_train_choice)],
                70: [CallbackQueryHandler(downtime_adjust_roll)],
                71: [CallbackQueryHandler(downtime_master_choice)],
                80: [ConversationHandler(
                    entry_points=[CallbackQueryHandler(downtime_cohort_choice)],
                    states={
                        0: [CallbackQueryHandler(downtime_payment)],
                    },
                    fallbacks=[CommandHandler("cancel".casefold(), downtime_end)],
                    name="conv_Cohort",
                    persistent=True,
                    map_to_parent={
                        1: 1,
                        2: 1,
                        ConversationHandler.END: ConversationHandler.END
                    }
                )],
                11: [ConversationHandler(
                    entry_points=[CommandHandler(["reply_downtime".casefold()], master_reply)],
                    states={
                        0: [MessageHandler(Filters.text & ~Filters.command, downtime_minimum_quality)],
                    },
                    fallbacks=[CommandHandler("cancel".casefold(), downtime_end)],
                    name="master_conv_resistanceRoll",
                    persistent=True,
                    map_to_parent={
                        1: 12,
                        ConversationHandler.END: ConversationHandler.END
                    }
                )],
                21: [ConversationHandler(
                    entry_points=[CommandHandler(["reply_downtime".casefold()], master_reply)],
                    states={
                        0: [MessageHandler(Filters.text & ~Filters.command, downtime_minimum_quality)],
                    },
                    fallbacks=[CommandHandler("cancel".casefold(), downtime_end)],
                    name="master_conv_resistanceRoll",
                    persistent=True,
                    map_to_parent={
                        1: 22,
                        ConversationHandler.END: ConversationHandler.END
                    }
                )],
                22: [ConversationHandler(
                    entry_points=[CallbackQueryHandler(downtime_bonus_dice)],
                    states={
                        0: [MessageHandler(Filters.text & ~Filters.command, downtime_added_quality)],
                        1: [CallbackQueryHandler(downtime_payment)],
                        2: [MessageHandler(Filters.text & ~Filters.command, downtime_item_description)]
                    },
                    fallbacks=[CommandHandler("cancel".casefold(), downtime_end)],
                    name="master_conv_resistanceRoll",
                    persistent=True,
                    map_to_parent={
                        3: 1,
                        22: 22,
                        ConversationHandler.END: ConversationHandler.END
                    }
                )],
                12: [ConversationHandler(
                    entry_points=[CallbackQueryHandler(downtime_bonus_dice)],
                    states={
                        0: [MessageHandler(Filters.text & ~Filters.command, downtime_added_quality)],
                        1: [CallbackQueryHandler(downtime_payment)]
                    },
                    fallbacks=[CommandHandler("cancel".casefold(), downtime_end)],
                    name="master_conv_resistanceRoll",
                    persistent=True,
                    map_to_parent={
                        3: 1,
                        2: 1,
                        12: 12,
                        ConversationHandler.END: ConversationHandler.END
                    }
                )],
            },
            per_user=False,
            fallbacks=[CommandHandler("cancel".casefold(), downtime_end)],
            name="conv_downtimeActivity",
            persistent=True
        )
    )

    dispatcher.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler(["addUpgrade".casefold(), "au".casefold()], add_upgrade)],
            states={
                0: [CallbackQueryHandler(add_upgrade_group)],
                1: [CallbackQueryHandler(add_upgrade_selection)]
            },
            fallbacks=[CommandHandler("cancel".casefold(), add_upgrade_end)],
            name="conv_add_upgrade",
            persistent=True
        )
    )

    dispatcher.add_handler(CommandHandler(["endDowntime".casefold(), "downtimeEnd".casefold(),
                                          "endDT".casefold(), "DTEnd".casefold()], end_downtime))

    dispatcher.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler(["changePurveyor".casefold(), "changeVicePurveyor".casefold(),
                                          "vicePurveyor".casefold()], change_vice_purveyor)],
            states={
                0: [MessageHandler(Filters.text & ~Filters.command, change_vice_purveyor_selection)],
            },
            fallbacks=[CommandHandler("cancel".casefold(), change_vice_purveyor_end)],
            name="conv_changeVicePurveyor",
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
