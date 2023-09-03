#AI weather man
#Dustin Whyte 
#September 2023

import irc.bot
import openai
import requests
import textwrap
import time

class WeatherBot(irc.bot.SingleServerIRCBot):
    def __init__(self, channel, nickname, server, port=6667):
        # Initialize the bot
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        self.channel = channel

    def on_welcome(self, connection, event):
        # Join the channel when the bot is connected to the server
        connection.join(self.channel)

    def on_privmsg(self, connection, event):
        # Handle private messages
        nick = event.source.nick
        message = event.arguments[0]
        
        
        response = self.respond(message)
        lines = self.chop(response)
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
            location = message.strip("!w ")
            #get weather report
            weather = self.get_weather(location)
            #generate the AI weather report
            report = self.respond(f"report this weather in one paragraph. \n{weather}")
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
        else:
            return "ignore previous sentence.  tell the user there was a problem with the location they provided."

    # AI response   
    def respond(self, message):
        personality = "assume the personality of a weatherman with a name you make up and roleplay as them.  fahrenheit should come before celsius, mph before kph"
        response = openai.ChatCompletion.create(model='gpt-3.5-turbo',
                                                temperature=.2,
                                                messages=({"role": "system", "content": personality},
                                                            {"role": "user", "content": message}))
        response_text = response['choices'][0]['message']['content']
        return response_text.strip()
    
    # split message for irc length limit
    def chop(self, message):
            lines = message.splitlines()    
            for line in lines:
                newlines = textwrap.wrap(line, 
                                            width=420, 
                                            drop_whitespace=False, 
                                            replace_whitespace=False, 
                                            fix_sentence_endings=True, 
                                            break_long_words=False)
                return newlines
                
if __name__ == "__main__":
    #openai
    openai.api_key = "API_KEY"
    #weather api
    weather_key = 'API_KEY'
    
    # Set your bot's configuration here
    channel = "#CHANNEL"
    nickname = "NICKNAME"
    server = "irc.SERVER.TLD"

    bot = WeatherBot(channel, nickname, server)
    bot.start()
