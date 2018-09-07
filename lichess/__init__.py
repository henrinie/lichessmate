# -*- coding: utf-8 -*-
import re
import json
import random
import time

from urllib.request import urlopen, Request
from urllib.error import URLError

from app import settings
from app import print_error

LICHESS_API_URL = 'https://lichess.org/api/'


class ApiRequest(object):
    """
    Objects instantiated by the :class:`ApiRequest <ApiRequest>` are to be
    used to send requests to lichess api. Creating only one instance is preferred
    to avoid sending requests too fast.
    """
    def send(self, path):
        """Send request to path on the API.

        :param path: A relative path added to lichess.org/api/
        :return: API response, json loaded into dict.
        """
        req = Request(LICHESS_API_URL + path, headers={'Accept': 'application/json'})
        try:
            with urlopen(req) as response:
                response_data = response.read()
        except URLError:
            raise URLError
        if response.status == 429:
            print_error('Response 429 - waiting 61 seconds.')
            # Wait a full minute before resuming API usage as lichess suggests.
            time.sleep(61)
            return
        return json.loads(response_data)


class LichessBot(object):
    """
    A bot that is used to communicate with the lichess API.
    Monitors if a player in the settings.PLAYERS list is playing.
    Can get data of a game based on a valid lichess game url.

    """
    def __init__(self):
        self.players_on_delay = dict()
        self.last_check = time.time() - settings.GET_PLAYING_DELAY
        self.request = ApiRequest()

    def get_playing(self, bot):
        """
        Check for players playing currently. Send one randomly selected players info to the bot.

        :param bot: The bot instance to which the message is relayed to.
        """
        self.update_player_delay()
        # Set the time interval (in seconds) that has to be passed from last time we checked.
        if time.time() - self.last_check > settings.GET_PLAYING_DELAY:
            print('Delay: ' + str(settings.GET_PLAYING_DELAY) + ' Last_check: ' +
                  str(time.ctime(self.last_check)) + ' time: ' + str(time.ctime()))
            path = '{}{}'.format('users/status?ids=', ','.join(settings.PLAYERS))
            # Get data from api using the request the ApiRequest object.
            data = self.request.send(path)
            if data is None:
                return
            playing = list()
            for player in data:
                # Player is playing and is not in the player delay list
                if player.get('playing') and player.get('id') not in self.players_on_delay.keys():
                    playing.append(player.get('id'))
            try:
                # Pick random player from the list.
                random_player_id = random.choice(playing)
            except IndexError:  # If list is empty.
                return
            user_path = 'user/{}'.format(random_player_id)
            # Fetch user data
            user = self.request.send(user_path)

            # Build a lichesstv url for the user
            tv_url = '{}{}'.format(user.get('url', ''), '/tv')
            # Get game id for the game the user is playing in.
            gameid = self.parse_gameid(user.get('playing'))

            # Fetch game data as a string.
            if gameid:
                gamedata = self.get_game(gameid, with_opening=False)
            else:
                return
            # Construct message the send to the channel by appending gameinfo with users lichesstv url.
            message = 'LIVE: {} @ {}'.format(gamedata, tv_url)
            try:
                # Relay a message to the chatbot.
                bot.send_msg(message)
            except:
                return
            print(message)
            # Set the time playing users was checked last time
            self.last_check = time.time()
            # Set a delay for the player whose gameinfo was posted to the chatbot.
            self.players_on_delay[random_player_id] = self.last_check
            print('Delay: {}'.format(settings.GET_PLAYING_DELAY))
        return

    @staticmethod
    def parse_gameid(msg):
        """
        Parse the gameid from a valid lichess gameurl.

        :param msg: Message to parse the gameid from.
        :return: Parsed gameid or None.
        """
        url_match = re.match('^https://([a-zA-Z]{2}\.)?lichess.org/(?P<id>\w+)/?(?:[#\w]*)$', msg)
        if url_match and url_match.group('id'):
            return url_match.group('id')
        return None

    def get_gameinfo(self, msg, with_opening=True):
        """
        Return game info as a string if the message contains a valid lichess gameurl.

        :param msg: Message to parse.
        :param with_opening: Whether to get opening data for the game.
        :return: A string to send as a message parsed from the gamedata, or nothing.

        """
        game = self.get_game(self.parse_gameid(msg))
        if game:
            message = self.parse_gamedata_to_str(game, with_opening)
            return message
        return

    def get_game(self, gameid, with_opening=True):
        """
        Fetch data for a game based on a gameid.

        :param gameid: Lichess gameId.
        :param with_opening: Whether to get opening data for the game.
        :return: API data of a game, json loaded into dict.
        """
        if gameid:
            path = 'game/{}?with_opening={}'.format(gameid, '1' if with_opening else '0')
            try:
                return self.request.send(path)
            except URLError:
                print_error('Unable to get gamedata: ' + path)
        return

    def parse_gamedata_to_str(self, game, with_opening=False):
        """
        Parse game data from a dict to a string.

        :param game: API data of a lichess game. Json loaded into a dict.
        :param with_opening: Whether to get opening data for the game.
        :return: String in the form of 'player1(rating) vs. player2(rating) [time+increment]'.
        """
        white = game.get('players', {}).get('white', {})
        black = game.get('players', {}).get('black', {})
        result = '{white_user}({white_rating}) vs. {black_user}({black_rating}) [{game_time}] {opening}'.format(
            white_user=white.get('userId') or white.get('name', ''),
            white_rating=white.get('rating', ''),
            black_user=black.get('userId') or black.get('name', ''),
            black_rating=black.get('rating', ''),
            game_time=self.calculate_gametime(game.get('clock', {})),
            opening=game.get('opening', {}).get('name', '') if with_opening else ''
        )
        return result

    @staticmethod
    def calculate_gametime(clock):
        """
        Return gametime(minutes)+increment(seconds) type of representation of gametime.
        E.g. '1+0' (1 minute of time with 0 second increments per move),
        or '15+15' (15 minutes of time with 15 seconds increments per move).

        :param clock: API data of a games clock. Json loaded into a dict.
        :return: Time formatted as gametime+increment (minutes+seconds).
        """
        clock_initial = clock.get('initial', '0')
        if clock_initial and int(clock_initial) > 59:
            clock_initial = str(int(int(clock_initial) / 60))
        increment = clock.get('increment', '0')
        game_time = '{}+{}'.format(clock_initial, increment)
        return game_time

    def update_player_delay(self):
        """
        Remove a player from players_on_delay if the GET_PLAYER_DELAY time has passed.
        """
        for key, value in self.players_on_delay.copy().items():
            # If settings.GET_PLAYER_DELAY amount of time has passed
            if time.time() - value > settings.GET_PLAYER_DELAY:
                # Remove the key (player) form the dictionary
                self.players_on_delay.pop(key)
