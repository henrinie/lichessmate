# -*- coding: utf-8 -*-
"""
Running this file will run the application.
Remember to configure settings in settings.py before running the app.

Usage:
    $ python3 app.py
"""
import sys
import time
import _thread

from datetime import datetime
import irc.client
from jaraco.stream import buffer

from ircbot import IRCBot
import lichess
import settings
try:
    from settings import SERVER, PORT, CHANNEL, NICKNAME
except ImportError as e:
    print('Unable to import required settings: {}'.format(e), file=sys.stderr)
    sys.exit()


def print_error(msg):
    """Prints current datetime and the message msg."""
    print('{now} * {msg}'.format(now=str(datetime.now()), msg=msg), file=sys.stderr)


def run_lichess(instance, bot):
    """

    :param instance: The instance to run.
    :param bot:
    :return:
    """
    while True:
        # This sets the wait time for checking lichess (in seconds).
        time.sleep(settings.GET_PLAYING_DELAY)
        instance.get_playing(bot)


def main():
    server = settings.SERVER
    port = settings.PORT
    channel = settings.CHANNEL
    nickname = settings.NICKNAME

    lichessmate = lichess.LichessBot()

    # LenientDecodingBuffer attempts UTF-8 but falls back to latin-1 to avoid UnicodeDecoreError in all cases.
    irc.client.ServerConnection.buffer_class = buffer.LenientDecodingLineBuffer
    ircbot = IRCBot(channel, nickname, server, port, lichessmate, settings)

    try:
        # Start a new thread for running Lichess, send the ircbot instance to it.
        _thread.start_new_thread(run_lichess, (lichessmate, ircbot))
    except _thread.error:
        print_error('Error: Unable to start thread.')

    ircbot.start()


if __name__ == '__main__':
    main()
