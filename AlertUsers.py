#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2019 Pedro Gabaldón

if __name__ == "__main__":
    import sys
    import json

    import telebot

    try:
        bot = telebot.TeleBot(sys.argv[1])
    except IndexError:
        sys.exit("Usage: %s TOKEN" % sys.argv[0])

    showMessage = "Travel:\n*{:s}* ({:s}) → *{:s}* ({:s}):\n\n"\
        "Via: *{:s}*. {:.2f} km in {:.2f} minutes. Traffic status: *{:s}*, {:.2f} minutes.\n\nLast update at: {:s}\n\n"\
        "See more [here](https://www.google.es/maps/dir/?api=1&origin={:s}&destination={:s})."

    TrafficLevels = ["Normal", "Bit slow", "Slow", "Heavy"]    

    with open("ChatsID.txt", "r") as f:
        chats = f.readlines()

    with open("last_update.json", "r") as f:
        update = json.load(f)

    for travel in update:
        for route in travel:
            if route["traffic_level"] > 0:
                for chatID in chats:
                    try:
                        bot.send_message(chatID, "Travel with slower traffic than normal:")
                        bot.send_message(chatID, showMessage.format(route["origin"], route["original_origin"],
                         route["destination"], route["original_destination"], route["summary"], route["distance"], 
                         route["duration"], TrafficLevels[route["traffic_level"]], route["duration_traffic"], route["time"],
                         route["original_origin"], route["original_destination"]), parse_mode="Markdown")
                    except:
                        pass