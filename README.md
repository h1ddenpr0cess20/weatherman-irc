# weatherman-irc

An AI weatherman for IRC powered by OpenAI GPT-3.5-turbo and WeatherAPI.  Reports the current weather conditions in the style of a weather man at a news station.

## Setup
```
pip3 install openai irc
```
Fill in your [OpenAI API](https://platform.openai.com/signup) key, [WeatherAPI](https://www.weatherapi.com/my/) key, IRC server, username, and channel

## Use
```
python3 weatherman.py
```

To use, type **!w _location_** or send a private message with location
