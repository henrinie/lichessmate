"""Unit tests for lichess module."""
import unittest
import json

import lichess


class LichessTests(unittest.TestCase):
    def setUp(self):
        self.bot = lichess.LichessBot()

    def test_parse_gameid(self):
        """Test parsing a gameid from url."""
        # Should not be valid
        msg = ''  # empty string
        self.assertIsNone(self.bot.parse_gameid(msg))
        msg = 'non-url text'
        self.assertIsNone(self.bot.parse_gameid(msg))
        msg = 'non-url text over 20 characters long'
        self.assertIsNone(self.bot.parse_gameid(msg))
        msg = 'https://fakelichess.org/mpTZiTC9'
        self.assertIsNone(self.bot.parse_gameid(msg))

        # Should be valid
        msg = 'https://lichess.org/mpTZiTC9'
        parsed_msg = self.bot.parse_gameid(msg)
        gameid = 'mpTZiTC9'
        self.assertEqual(parsed_msg, gameid)
        msg = 'https://lichess.org/mpTZiTC9/black'
        parsed_msg = self.bot.parse_gameid(msg)
        self.assertEqual(parsed_msg, gameid)
        msg = 'https://de.lichess.org/mpTZiTC9'
        parsed_msg = self.bot.parse_gameid(msg)
        self.assertEqual(parsed_msg, gameid)
        msg = 'https://de.lichess.org/mpTZiTC9/white'
        parsed_msg = self.bot.parse_gameid(msg)
        self.assertEqual(parsed_msg, gameid)

    def test_parse_gamedata_to_str(self):
        """Verify that parsing to str works as intended."""
        data = '{}'
        mock = json.loads(data)
        parsed = self.bot.parse_gamedata_to_str(mock, with_opening=False)
        self.assertEqual(parsed, '() vs. () [0+0] ')

        data = '''{"id":"mpTZiTC9","rated":true,"variant":"standard","speed":"bullet","perf":"bullet",
        "createdAt":1536315709992,"lastMoveAt":1536315837328,"turns":97,"color":"black","status":"mate",
        "clock":{"initial":60,"increment":0,"totalTime":60},"players":{"white":{"userId":"piscean64",
        "rating":2461,"ratingDiff":14},"black":{"userId":"off_white","rating":2529,"ratingDiff":-13}},
        "opening":{"eco":"A13","name":"English Opening: Agincourt Defense","ply":3},
        "winner":"white","url":"https://lichess.org/mpTZiTC9/black"}'''
        mock = json.loads(data)
        parsed_opening = self.bot.parse_gamedata_to_str(mock, with_opening=True)
        self.assertEqual(parsed_opening, 'piscean64(2461) vs. off_white(2529) [1+0] English Opening: Agincourt Defense')
        parsed = self.bot.parse_gamedata_to_str(mock, with_opening=False)
        self.assertEqual(parsed, 'piscean64(2461) vs. off_white(2529) [1+0] ')

    def test_calculate_gametime(self):
        """Verify that gametime calculator works as intended."""
        clock = {"initial": 0, "increment": 0, "totalTime": 0}
        self.assertEqual(self.bot.calculate_gametime(clock), '0+0')
        clock = {"initial": 60, "increment": 0, "totalTime": 60}
        self.assertEqual(self.bot.calculate_gametime(clock), '1+0')
        clock = {"initial": 300, "increment": 5, "totalTime": 500}
        self.assertEqual(self.bot.calculate_gametime(clock), '5+5')
        clock = {"initial": 900, "increment": 15, "totalTime": 1500}
        self.assertEqual(self.bot.calculate_gametime(clock), '15+15')

    def test_update_player_delay(self):
        """Test that updating delay for a player works."""
        from settings import GET_PLAYER_DELAY
        delay = GET_PLAYER_DELAY
        players = self.bot.players_on_delay
        last_check = self.bot.last_check
        players.update({'username': last_check})
        self.bot.update_player_delay()
        self.assertIn('username', players.keys())

        last_check -= delay
        players.update({'username': last_check})
        self.bot.update_player_delay()
        self.assertNotIn('username', players.keys())
