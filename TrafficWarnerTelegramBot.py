#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2019 Pedro Gabaldón

if __name__ == "__main__":
    import sys
    import json
    import subprocess
    import codecs
    import time

    import telebot
    from geopy import Nominatim

    try:
        bot = telebot.TeleBot(sys.argv[1])
    except IndexError:
        sys.exit("Usage: %s TOKEN" % sys.argv[0])

    indexTravel = 0
    indexRoute = 0    

    inlineKeyboardButtonNextTravel = telebot.types.InlineKeyboardButton("Next travel", callback_data="next_travel")
    inlineKeyboardButtonPreviousTravel = telebot.types.InlineKeyboardButton("Previous travel", callback_data="previous_travel")
    inlineKeyboardButtonNextRoute = telebot.types.InlineKeyboardButton("Next route", callback_data="next_route")
    inlineKeyboardButtonPreviousRoute = telebot.types.InlineKeyboardButton("Previous route", callback_data="previous_route")
    inlineKeyboardTravelRoute = telebot.types.InlineKeyboardMarkup(row_width=2)
    inlineKeyboardTravelRoute.add(inlineKeyboardButtonPreviousTravel, inlineKeyboardButtonNextTravel, 
        inlineKeyboardButtonPreviousRoute, inlineKeyboardButtonNextRoute)

    inlineKeyboardButtonConfirm = telebot.types.InlineKeyboardButton("Confirm", callback_data="confirm_new_travel")
    inlineKeyboardButtonTolls = telebot.types.InlineKeyboardButton("\U000026AA Avoid Tolls", callback_data="avoid_tolls")
    inlineKeyboardButtonFerries = telebot.types.InlineKeyboardButton("\U000026AA Avoid Ferries", callback_data="avoid_ferries")
    inlineKeyboardButtonHighways = telebot.types.InlineKeyboardButton("\U000026AA Avoid Highways", callback_data="avoid_highways")
    inlineKeyboardAddTravel = telebot.types.InlineKeyboardMarkup(row_width=1)
    inlineKeyboardAddTravel.add(inlineKeyboardButtonTolls, inlineKeyboardButtonFerries, 
        inlineKeyboardButtonHighways, inlineKeyboardButtonConfirm)

    avoid_tolls = False
    avoid_ferries = False
    avoid_highways = False

    last_origin_msg = ""
    last_destination_msg = ""

    welcomeMessage = "This bot shows traffic status of a preloaded list of "\
        "travels. Send /help to view all options and information about them."\

    helpMessage = "/start - Starts the bot.\n"\
        "/show - This command will send you a message with actual traffic info. (Updated every 30 minutes). Orignal set names "\
        "will be shown between parentheses. You can iterate through different routes.\n"\
        "/update - It will trigger an update and it will send you new traffic information. (Only admins)\n"\
        "/allowuser - For admins, this will let a new user use this bot.\n"\
        "/disallowuser - For admins, this will remove an allowed user\n"\
        "/add - Add a new travel to the list. (Admins only)"

    showMessage = "Travel:\n*{:s}* ({:s}) → *{:s}* ({:s}):\n\n"\
        "Via: *{:s}*. {:.2f} km in {:.2f} minutes. Traffic status: *{:s}*, {:.2f} minutes.\n\nLast update at: {:s}\n\n"\
        "See more [here](https://www.google.es/maps/dir/?api=1&origin={:s}&destination={:s})."

    TrafficLevels = ["Normal", "Bit slow", "Slow", "Heavy"]

    with open("AllowedUsers.json", "r") as f:
        allowedUsers = json.load(f)    

    with open("last_update.json", "r") as f:
        lastUpdate = json.load(f)

    allowedID = [tid.get("TelegramID") for tid in allowedUsers]

    @bot.message_handler(func=lambda message: message.chat.type != "private")
    def no_groups(message):
        # TODO
        bot.send_message(message.chat.id, "This bot does not support groups, channels and supergroups yet.\U0001f614")
        bot.leave_chat(message.chat.id)

    @bot.message_handler(func=lambda message: message.from_user.id not in allowedID)
    def unauthorized(message):
        bot.reply_to(message, "You are not allowed to use this bot.")

    @bot.message_handler(commands=["start"])
    def welcome(message):
        bot.reply_to(message, "Hey " + message.from_user.first_name + "!")
        bot.send_message(message.chat.id, welcomeMessage)

        with open("ChatsID.txt", "a+") as f:
            chats = f.readlines()
            if str(message.chat.id) not in chats:
                f.write(str(message.chat.id) + "\n")

    @bot.message_handler(commands=["help"])
    def help(message):
        bot.send_message(message.chat.id, helpMessage)

    @bot.message_handler(commands=["show"])
    def show(message):
        with open("last_update.json", "r") as f:
            global lastUpdate
            lastUpdate = json.load(f)
        
        if lastUpdate:        
            bot.send_message(message.chat.id, showMessage.format(lastUpdate[indexTravel][indexRoute]["origin"],
             lastUpdate[indexTravel][indexRoute]["original_origin"],
             lastUpdate[indexTravel][indexRoute]["destination"], lastUpdate[indexTravel][indexRoute]["original_destination"], 
             lastUpdate[indexTravel][indexRoute]["summary"], lastUpdate[indexTravel][indexRoute]["distance"],
             lastUpdate[indexTravel][indexRoute]["duration"], TrafficLevels[lastUpdate[indexTravel][indexRoute]["traffic_level"]],
             lastUpdate[indexTravel][indexRoute]["duration_traffic"], lastUpdate[indexTravel][indexRoute]["time"], lastUpdate[indexTravel][indexRoute]["original_origin"],
             lastUpdate[indexTravel][indexRoute]["original_destination"]),
             parse_mode="Markdown", reply_markup=inlineKeyboardTravelRoute)
        else:
        	bot.send_message(message.chat.id, "No travels added yet\U0001f614")

    @bot.message_handler(commands=["update"])
    def update(message):
        if allowedUsers[allowedID.index(message.from_user.id)]["administrator"]:
            bot.send_chat_action(message.chat.id, "typing")
            subprocess.call(["python", "./TrafficWarner.py"])
            time.sleep(3)

            with open("last_update.json", "r") as f:
                global lastUpdate
                lastUpdate = json.load(f)

            show(message)
        else:
            bot.reply_to(message, "You are not an administrator, so you are not allowed to use this command.")    

    @bot.message_handler(commands=["allowuser"])
    def allow_user(message):
        if allowedUsers[allowedID.index(message.from_user.id)]["administrator"]:
            sent = bot.send_message(message.chat.id, "Send me the contact or Telegram ID.")
            bot.register_next_step_handler(sent, allow_user_next_step)
        else:
            bot.reply_to(message, "You are not an administrator, so you are not allowed to use this command.")

    def allow_user_next_step(message):
        global allowedID
        global allowedUsers
        if message.text:
            try:
                if int(message.text) not in allowedID:
                    allowedUsers.append({"TelegramID" : int(message.text), "administrator" : False})
                    with open("AllowedUsers.json", "w") as f:
                        json.dump(allowedUsers, f, indent=4, sort_keys=True)
                    bot.send_message(message.chat.id, "New user added.")
                else:
                    bot.send_message(message.chat.id, "User already allowed.")    
            except ValueError:
                bot.send_message(message.chat.id, "That is not a Telegram ID.")
        elif message.contact:
            if message.contact.user_id:
                if message.contact.user_id not in allowedID:
                    allowedUsers.append({"TelegramID" : int(message.contact.user_id), "administrator" : False})
                    with open("AllowedUsers.json", "w") as f:
                        json.dump(allowedUsers, f, indent=4, sort_keys=True)
                    bot.send_message(message.chat.id, "New user added.")
                else:
                    bot.send_message(message.chat.id, "User already allowed.")    
            else:
                bot.send_message(message.chat.id, "This contact is not in Telegram.")        
        else:
            bot.send_message(message.chat.id, "That is not what I expected.")

        allowedID = [tid.get("TelegramID") for tid in allowedUsers]    

    @bot.message_handler(commands=["disallowuser"])
    def disallow_user(message):
        if allowedUsers[allowedID.index(message.from_user.id)]["administrator"]:
            sent = bot.send_message(message.chat.id, "Send me the contact or Telegram ID.")
            bot.register_next_step_handler(sent, disallow_user_next_step)
        else:
            bot.reply_to(message, "You are not an administrator, so you are not allowed to use this command.")

    def disallow_user_next_step(message):
        global allowedID
        global allowedUsers
        if message.text:
            try:
                index = allowedID.index(int(message.text))
                allowedUsers.pop(index)
                with open("AllowedUsers.json", "w") as f:
                    json.dump(allowedUsers, f, indent=4, sort_keys=True)
                bot.send_message(message.chat.id, "User disallowed.")
            except ValueError:
                bot.send_message(message.chat.id, "Invalid Telegram ID.")
        elif message.contact:
            if message.contact.user_id:
                try:
                    index = allowedID.index(int(message.contact.user_id))
                    allowedUsers.pop(index)
                    with open("AllowedUsers.json", "w") as f:
                        json.dump(allowedUsers, f, indent=4, sort_keys=True)
                    bot.send_message(message.chat.id, "User disallowed.")
                except ValueError:
                    bot.send_message(message.chat.id, "Invalid contact.")
            else:
                bot.send_message(message.chat.id, "This contact is not in Telegram.")        
        else:
            bot.send_message(message.chat.id, "That is not what I expected.")

        allowedID = [tid.get("TelegramID") for tid in allowedUsers]        

    @bot.message_handler(commands=["add"])
    def add(message):
        if allowedUsers[allowedID.index(message.from_user.id)]["administrator"]:
            sent = bot.send_message(message.chat.id, "Send me the origin.")
            bot.register_next_step_handler(sent, add_origin)
        else:
            bot.reply_to(message, "You are not an administrator, so you are not allowed to use this command.")

    def add_origin(message):
        global last_origin_msg
        if message.text:
            g = Nominatim(user_agent="TrafficWarnerTelegramBot")
            origin = g.geocode(message.text)
            if origin.address:
                bot.send_message(message.chat.id, origin.address)
                sent = bot.send_message(message.chat.id, "Now send me the destination.")
                bot.register_next_step_handler(sent, add_destination, origin)
                last_origin_msg = message.text
            else:
                bot.send_message(message.chat.id, "Origin not found.")
        else:
            bot.reply_to(message, "That is not what I expected")

    def add_destination(message, origin):
        global last_destination_msg
        if message.text:
            g = Nominatim(user_agent="TrafficWarnerTelegramBot")
            destination = g.geocode(message.text)
            if destination.address:
                bot.send_message(message.chat.id, destination.address)
                last_destination_msg = message.text
                bot.send_message(message.chat.id, "New travel to add:\n{:s} → {:s}".format(last_origin_msg, last_destination_msg),
                 reply_markup=inlineKeyboardAddTravel)
            else:
                bot.send_message(message.chat.id, "Destination not found.")    
        else:
            bot.reply_to(message, "That is not what I expected")    

    @bot.message_handler(func=lambda message: True, content_types=None)    
    def unhandled(message):
        bot.reply_to(message, "I did not understand you, use /help to learn how to use me.")

    @bot.callback_query_handler(func=lambda call: call.data == "confirm_new_travel")
    @bot.callback_query_handler(func=lambda call: call.data == "avoid_highways")
    @bot.callback_query_handler(func=lambda call: call.data == "avoid_ferries")
    @bot.callback_query_handler(func=lambda call: call.data == "avoid_tolls")
    def callback_new_travel(call):
        global avoid_tolls, avoid_ferries, avoid_highways
        global last_destination_msg, last_origin_msg
        global inlineKeyboardButtonTolls, inlineKeyboardButtonHighways, inlineKeyboardButtonFerries, inlineKeyboardButtonConfirm

        g = Nominatim(user_agent="TrafficWarnerTelegramBot")

        avoid = []

        if avoid_tolls:
            avoid.append("tolls")
        if avoid_ferries:
            avoid.append("ferries")
        if avoid_highways:
            avoid.append("highways")

        if call.data == "confirm_new_travel":
            bot.send_chat_action(call.message.chat.id, "typing")
            with open("config.json", "r") as f:
                config = json.load(f)    
            
            for travel in config["directions"]:
                if (g.geocode(last_origin_msg).address == g.geocode(travel["origin"]).address) and (g.geocode(last_destination_msg).address == g.geocode(travel["destination"]).address):
                    bot.answer_callback_query(call.id, text="This travel does already exists.", show_alert=True)
                    return

            new_travel = {"origin" : last_origin_msg, "destination" : last_destination_msg, "avoid" : avoid}
            with open("config.json", "w") as f:
                config["directions"].append(new_travel)
                json.dump(config, f, indent=4, sort_keys=True)
            bot.answer_callback_query(call.id, text="New travel added.", show_alert=True)

            avoid_tolls = False
            avoid_ferries = False
            avoid_highways = False

            inlineKeyboardButtonConfirm = telebot.types.InlineKeyboardButton("Confirm", callback_data="confirm_new_travel")
            inlineKeyboardButtonTolls = telebot.types.InlineKeyboardButton("\U000026AA Avoid Tolls", callback_data="avoid_tolls")
            inlineKeyboardButtonFerries = telebot.types.InlineKeyboardButton("\U000026AA Avoid Ferries", callback_data="avoid_ferries")
            inlineKeyboardButtonHighways = telebot.types.InlineKeyboardButton("\U000026AA Avoid Highways", callback_data="avoid_highways")
            inlineKeyboardAddTravel = telebot.types.InlineKeyboardMarkup(row_width=1)
            inlineKeyboardAddTravel.add(inlineKeyboardButtonTolls, inlineKeyboardButtonFerries, 
              inlineKeyboardButtonHighways, inlineKeyboardButtonConfirm)

        if call.data == "avoid_highways":
            avoid_highways = not avoid_highways

            emoji = "\U000026AA"

            if avoid_highways:
                emoji = "\U0001F518"
                inlineKeyboardButtonHighways = telebot.types.InlineKeyboardButton(emoji + " Avoid Highways", callback_data="avoid_highways")
                inlineKeyboardAddTravel = telebot.types.InlineKeyboardMarkup(row_width=1)
                inlineKeyboardAddTravel.add(inlineKeyboardButtonTolls, inlineKeyboardButtonFerries, 
                 inlineKeyboardButtonHighways, inlineKeyboardButtonConfirm)
            else:
                inlineKeyboardButtonHighways = telebot.types.InlineKeyboardButton(emoji + " Avoid Highways", callback_data="avoid_highways")    
                inlineKeyboardAddTravel = telebot.types.InlineKeyboardMarkup(row_width=1)
                inlineKeyboardAddTravel.add(inlineKeyboardButtonTolls, inlineKeyboardButtonFerries, 
                  inlineKeyboardButtonHighways, inlineKeyboardButtonConfirm)    
            bot.edit_message_text("New travel to add:\n{:s} → {:s}".format(last_origin_msg, last_destination_msg),
             reply_markup=inlineKeyboardAddTravel, message_id=call.message.message_id, chat_id=call.message.chat.id)
            bot.answer_callback_query(call.id)    

        if call.data == "avoid_ferries":
            avoid_ferries = not avoid_ferries

            emoji = "\U000026AA"

            if avoid_ferries:
                emoji = "\U0001F518"
                inlineKeyboardButtonFerries = telebot.types.InlineKeyboardButton(emoji + " Avoid Ferries", callback_data="avoid_ferries")
                inlineKeyboardAddTravel = telebot.types.InlineKeyboardMarkup(row_width=1)
                inlineKeyboardAddTravel.add(inlineKeyboardButtonTolls, inlineKeyboardButtonFerries, 
                 inlineKeyboardButtonHighways, inlineKeyboardButtonConfirm)
            else:
                inlineKeyboardButtonFerries = telebot.types.InlineKeyboardButton(emoji + " Avoid Ferries", callback_data="avoid_ferries")    
                inlineKeyboardAddTravel = telebot.types.InlineKeyboardMarkup(row_width=1)
                inlineKeyboardAddTravel.add(inlineKeyboardButtonTolls, inlineKeyboardButtonFerries, 
                  inlineKeyboardButtonHighways, inlineKeyboardButtonConfirm)    
            bot.edit_message_text("New travel to add:\n{:s} → {:s}".format(last_origin_msg, last_destination_msg),
             reply_markup=inlineKeyboardAddTravel, message_id=call.message.message_id, chat_id=call.message.chat.id)
            bot.answer_callback_query(call.id)

        if call.data == "avoid_tolls":
            avoid_tolls = not avoid_tolls

            emoji = "\U000026AA"

            if avoid_tolls:
                emoji = "\U0001F518"
                inlineKeyboardButtonTolls = telebot.types.InlineKeyboardButton(emoji + " Avoid Tolls", callback_data="avoid_tolls")
                inlineKeyboardAddTravel = telebot.types.InlineKeyboardMarkup(row_width=1)
                inlineKeyboardAddTravel.add(inlineKeyboardButtonTolls, inlineKeyboardButtonFerries, 
                 inlineKeyboardButtonHighways, inlineKeyboardButtonConfirm)
            else:
                inlineKeyboardButtonTolls = telebot.types.InlineKeyboardButton(emoji + " Avoid Tolls", callback_data="avoid_tolls")    
                inlineKeyboardAddTravel = telebot.types.InlineKeyboardMarkup(row_width=1)
                inlineKeyboardAddTravel.add(inlineKeyboardButtonTolls, inlineKeyboardButtonFerries, 
                  inlineKeyboardButtonHighways, inlineKeyboardButtonConfirm)    
            bot.edit_message_text("New travel to add:\n{:s} → {:s}".format(last_origin_msg, last_destination_msg),
             reply_markup=inlineKeyboardAddTravel, message_id=call.message.message_id, chat_id=call.message.chat.id)
            bot.answer_callback_query(call.id)                

    @bot.callback_query_handler(func=lambda call: call.data == "next_travel")
    @bot.callback_query_handler(func=lambda call: call.data == "previous_travel")
    @bot.callback_query_handler(func=lambda call: call.data == "next_route")
    @bot.callback_query_handler(func=lambda call: call.data == "previous_route")
    def callback_show(call):
        global indexTravel
        global indexRoute

        if (call.data == "next_travel") and (indexTravel < len(lastUpdate) - 1):
            indexTravel += 1
            indexRoute = 0
        elif (call.data == "next_travel") and not (indexTravel < len(lastUpdate) - 1):
            indexTravel = 0
            indexRoute = 0
        elif (call.data == "previous_travel") and (indexTravel > 0):
            indexTravel -= 1
            indexRoute = 0
        elif (call.data == "previous_travel") and not (indexTravel > 0):
            indexTravel = len(lastUpdate) - 1
            indexRoute = 0
        elif (call.data == "next_route") and (indexRoute < len(lastUpdate[indexTravel]) - 1):
            indexRoute += 1
        elif (call.data == "next_route") and not (indexRoute < len(lastUpdate[indexTravel]) - 1):
            indexRoute = 0
        elif (call.data == "previous_route") and (indexRoute > 0):
            indexRoute -= 1
        elif (call.data == "previous_route") and not (indexRoute > 0):
            indexRoute = len(lastUpdate[indexTravel]) - 1

        try:    
            bot.edit_message_text(showMessage.format(lastUpdate[indexTravel][indexRoute]["origin"],
             lastUpdate[indexTravel][indexRoute]["original_origin"],
             lastUpdate[indexTravel][indexRoute]["destination"], lastUpdate[indexTravel][indexRoute]["original_destination"], 
             lastUpdate[indexTravel][indexRoute]["summary"], lastUpdate[indexTravel][indexRoute]["distance"],
             lastUpdate[indexTravel][indexRoute]["duration"], TrafficLevels[lastUpdate[indexTravel][indexRoute]["traffic_level"]],
             lastUpdate[indexTravel][indexRoute]["duration_traffic"], lastUpdate[indexTravel][indexRoute]["time"], lastUpdate[indexTravel][indexRoute]["original_origin"],
             lastUpdate[indexTravel][indexRoute]["original_destination"]),
             message_id=call.message.message_id, chat_id=call.message.chat.id, parse_mode="Markdown", reply_markup=inlineKeyboardTravelRoute)
        except telebot.apihelper.ApiException as err:
            if err.result.json()["error_code"] == 400:
                pass
            else:
                raise

        bot.answer_callback_query(call.id, text="Travel info updated\U0001f44d")     
                
    print("Bot started...")
    bot.polling()