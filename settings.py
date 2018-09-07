# -*- coding: utf-8 -*-
"""
Settings module for lichessmate.
Make sure you fill in every setting correctly.
"""
# Server address (e.g. 'irc.server.org')
SERVER = 'irc.quakenet.org'
# Port number (as an inteher! e.g. 6667)
PORT = 6667
# Channel (e.g. '#mychannel')
CHANNEL = '#chesstest'
# Nickname of the bot
NICKNAME = 'dasdasbas'
# A list of lichess usernames to monitor. E.g. ['lichess_username1', 'lichess_username2',]
PLAYERS = ['cocostarc', 'TheNoobyOne']
# 3600 seconds = 1h, 1800s=30min, 900s=15min, 300s=5min
# The delay between requests for checking if any user in PLAYERS is currently playing.
GET_PLAYING_DELAY = 300  # Delay in seconds
# How long to wait until posting info again about a user whose info was posted.
GET_PLAYER_DELAY = 3600  # Delay in seconds
