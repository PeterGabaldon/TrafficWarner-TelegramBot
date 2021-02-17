# TrafficWarner Telegram Bot
## ![](https://img.shields.io/badge/python-3.9-blue)

## About

TrafficWarner is a Telegram bot PoC that can track information about travels you want using Google Maps Directions API. Using `\add` the bot will ask you about a source an a destination, after that and after configuring the route options(avoid tolls, avoid ferries, avoid highways) the new Travel is added. `TrafficWarner.py` reads the configured travels and ask Google Maps Directions API to update information about the route(s) of the travel(s). You should run it in a Cronjob, in a terminal loop or something similar. `AlertUsers.py` can be used to alert users if the trip status has changed to a worse one, for example, if a route trip is "green" in Google Maps so the traffic is normal but for some reason changes and now the traffic is heavy the users will be warned about it.

# Usage
```bash
git clone TODO
pip install -r requirements.txt

python TrafficWarnerTelegramBot.py [YOUR_BOT_TOKEN_HERE]
python TrafficWarner.py
python AlertUsers.py [YOUR_BOT_TOKEN_HERE]
```
The last two are optional, run it in a loop or scheduled if you want the traffic status being auto-updateded and/or to alert users aboout changes in traffic status.

## Authorization
You need to contact the [Bot Father](https://t.me/botfather) in order to create a Telegram Bot and receive an API Token. Also you will need to create a projet on **Google Cloud Platform** and create and API Key to access the Google Maps API, create this one [here](https://console.cloud.google.com/google/maps-apis/credentials). After that modify `config.json` to add your **Google Maps API** Key. The `ChatsID.txt` file is used by `AlertUsers.py` to keep track about started chats to notify them when required. 

## Allowed users

Only allowed users can use the bot. Edit `AllowedUsers.json` adding your Telegram ID, you can also specify if an user is an admin or not. To find your Telegram ID you can send a message to the bot and make a GET request to the `getUpdates` endpoint of the Bot REST API getting information about the messages the bot has received on your browser(the bot must be stopped, if not it will process the received message). The endpoint is `https://api.telegram.org/bot[YOUR_BOT_TOKEN_HERE]/getUpdates`. In the returned JSON you will find information about the user that sent the message, including the ID. This is only needed for the first user, after that you can use the bot command `/allowuser` to start allowing a user to communicate.

# Bot commands
```
/start - Starts the bot.
/show - This command will send you a message with actual traffic info. (Updated every 30 minutes). Orignal set names will be shown between parentheses. You can iterate through different routes.
/update - It will trigger an update and it will send you new traffic information. (Only admins)
/allowuser - For admins, this will let a new user use this bot.
/disallowuser - For admins, this will remove an allowed user
/add - Add a new travel to the list. (Admins only)
```

# Demo
[![Demo video](https://github.com/PeterGabaldon/TrafficWarner-TelegramBot/blob/main/thumb.png?raw=true)](https://www.youtube.com/watch?v=UQf8vznHKqs)
