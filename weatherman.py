#AI weather man for IRC
#Dustin Whyte 
#September 2023

import irc.bot
from openai import OpenAI
import requests
import textwrap
import time

class WeatherBot(irc.bot.SingleServerIRCBot):
    def __init__(self, channel, nickname, server, password=None, port=6667):
        # Initialize the bot
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        self.channel = channel
        self.password = password

    def on_welcome(self, connection, event):
        #if nick has a password
        if self.password != None:
          connection.privmsg("NickServ", f"IDENTIFY {self.password}")
          #wait for identify to finish
          time.sleep(5)
        # Join the channel when the bot is connected to the server
        connection.join(self.channel)

    def on_privmsg(self, connection, event):
        # Handle private messages
        nick = event.source.nick
        message = event.arguments[0]
        
        #get the weather
        weather = self.get_weather(message)
        #generate AI report, generates a longer report than in channel
        report = self.respond(f"report this weather. \n{weather}")
        lines = self.chop(report)
        for line in lines:
            connection.privmsg(nick, line)
            time.sleep(1)

    def on_pubmsg(self, connection, event):
        # Handle messages in the channel
        nick = event.source.nick
        message = event.arguments[0]

        # get weather report
        if message.startswith("!w "):
            #get location from the message
            location = message.strip("!w")
            location = location.strip()
            #get weather report
            weather = self.get_weather(location)
            #generate the AI weather report, omitting less important details
            report = self.respond(f"report this weather in one paragraph, you can skip barometric pressure, visibility, UV index and other less important details. \n{weather}")
            lines = self.chop(report)
            #send lines to channel
            for line in lines:
                connection.privmsg(self.channel, line)
                time.sleep(1)    

    # get the weather from weather api
    def get_weather(self, location):
        url = f"http://api.weatherapi.com/v1/current.json?key={weather_key}&q={location}&aqi=no"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data
        
        #improve this with other error codes later
        else:
            return "ignore previous sentence.  DO NOT attempt to report the weather.  tell the user there was a problem with the location they provided."

    # AI response   
    def respond(self, message):
        personality = "assume the personality of a weatherman with a name you make up and roleplay as them.  [fahrenheit should come before celsius, mph before kph]"
        response = openai.chat.completions.create(model='gpt-3.5-turbo-1106',
                                                temperature=1,
                                                messages=({"role": "system", "content": personality},
                                                            {"role": "user", "content": message}))
        response_text = response.choices[0].message.content
        return response_text.strip()
    
    # split message for irc message length limit of 512 characters
    def chop(self, message):
        #separate each line of the response
        lines = message.splitlines()
        newlines = []  # Initialize an empty list to store wrapped lines

        #check the length of the line, break it up if above limit
        for line in lines:
            if len(line) > 420:
                wrapped_lines = textwrap.wrap(line,
                                            width=420,
                                            drop_whitespace=False,
                                            replace_whitespace=False,
                                            fix_sentence_endings=True,
                                            break_long_words=False)
                newlines.extend(wrapped_lines)  # Extend the list with wrapped lines
            else:
                newlines.append(line)  # Add the original line to the list

        return newlines  # Return the list of wrapped lines

if __name__ == "__main__":
    #openai
    api_key = "API_KEY"
    openai = OpenAI(api_key=api_key)
    #weather api
    weather_key = 'API_KEY'
    
    # Set your bot's configuration here
    channel = "#CHANNEL"
    nickname = "NICKNAME"
    server = "irc.SERVER.TLD"
    #optional password for channels that require registration
    #password = "password"

    try:
        bot = WeatherBot(channel, nickname, server, password)
    except:
        bot = WeatherBot(channel, nickname, server)
    bot.start()