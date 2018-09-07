lichessmate documentation
=========================

:Date: |today|
:Version: |release|

Python chatbot for monitoring lichess.org.

.. toctree::
    :maxdepth: 2
    :caption: Contents:

    lichess
    ircbot

Features
--------
* Monitors the activity of a list of players on lichess.
* Shows information of lichess games when a valid url is posted.
* Can connect to IRC

Requirements
------------
* Python 3.6
* `Pipenv`_
* Python package `irc`_ and its dependencies

.. _Pipenv: https://docs.pipenv.org/
.. _irc: https://pypi.org/project/irc/

Usage
-----

Install dependencies:

.. code-block:: bash

    $ pipenv install

After that configure settings.py.

Then run the application:

.. code-block:: bash

    $ python3 app.py

Documentation
-------------
Build the documentation locally by running:

.. code-block:: bash

    $ pipenv run docs/make html

View the freshly built html documentation at
``docs/html``

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
