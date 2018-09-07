# lichessmate #

[![Build Status](https://travis-ci.org/henrinie/lichessmate.svg?branch=master)](https://travis-ci.org/henrinie/lichessmate)

Python chatbot for monitoring lichess.org.

## Features ##

* Monitors the activity of a list of players on lichess.
* Shows information of lichess games when a valid url is posted.
* Can connect to IRC

## Requirements ##

* Python 3.6
* [Pipenv](https://docs.pipenv.org/)
* Python package [irc](https://pypi.org/project/irc/)

## Usage ##

`$ pipenv install`
Configure settings.py
`$ python3 app.py`

## Documentation ##

Build the documentation locally by running `$ pipenv run docs/make html`
View the freshly built html documentation at `docs/html`
