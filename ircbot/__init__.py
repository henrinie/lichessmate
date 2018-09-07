# -*- coding: utf-8 -*-
"""
A simple IRC bot.
This bot uses the SingleServerIRCBot from irc.bot.
The bot enters a channel and monitors messages sent to the channel.
If a message is a lichess game url, the bot will post back information about the game.
Certain commands can be given as private messages to the bot.

The known commands are:
  .reload -- Reload settings.
  .disconnect -- Disconnect the bot. The bot will try to reconnect after 60 seconds.
  .die -- Kill the bot.
"""
import importlib
import time

import irc.bot
import irc.client
import irc.strings


class IRCBot(irc.bot.SingleServerIRCBot):
    """IRC bot based on SingleServerIRCBot."""
    def __init__(self, channel, nickname, server, port=6667, lichess=None, settings=None):
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        # The channel (attempted to) connect to.
        self.channel = channel
        # Reference to the Lichess instance.
        self.lichess = lichess
        # Settings module.
        self.settings = settings

    def send_msg(self, message):
        """Send a message to self.channel."""
        self.connection.privmsg(self.channel, message)

    def on_nicknameinuse(self, c, e):
        "When nickname is in use modify the nickname."
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        c.join(self.channel)

    def on_privmsg(self, c, e):
        """React to private messages."""
        self.do_command(e, e.arguments[0])

    def on_pubmsg(self, c, e):
        """React to public messages to a channel."""
        if len(e.arguments[0]) > 20:
            message = self.lichess.get_gameinfo(e.arguments[0])
            channel = e.target
            if message and channel:
                c.privmsg(channel, message)
                # Make sure we wait 1 second between requests coming from IRC.
                time.sleep(1)
        a = e.arguments[0].split(":", 1)
        if len(a) > 1 and irc.strings.lower(a[0]) == irc.strings.lower(self.connection.get_nickname()):
            self.do_command(e, a[1].strip())
        return

    def do_command(self, e, cmd):
        """Commands the bot listens to."""
        nick = e.source.nick
        c = self.connection

        if cmd == '.disconnect':
            self.disconnect()
        elif cmd == '.die':
            self.die()
        elif cmd == '.reload':
            try:
                importlib.reload(self.settings)
            except ImportError:
                return
            c.notice(nick, 'Settings reloaded.')
        else:
            c.notice(nick, 'Not understood: ' + cmd)