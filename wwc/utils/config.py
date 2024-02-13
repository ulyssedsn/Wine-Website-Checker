from json import load
from logging import StreamHandler, DEBUG, Formatter, getLogger
from os import environ
from os.path import join, dirname
from pathlib import Path
from sys import stdout

from dotenv import load_dotenv


class WwcConfig(object):
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(WwcConfig, cls).__new__(cls)
            cls._instance.__initialize()
        return cls._instance

    def __initialize(self):
        """
        Perform initialization of the class with a custom method
        Python calls __init__ every time after a call to __new__.
        """
        load_dotenv()

        self.logger = self._logger()
        self.keywords = self._keywords()
        self.websites = self._websites()
        self._version = self._read_version()
        self.password_gmail = self._password_gmail()

    @staticmethod
    def _logger():
        """
        Hacky logger setup
        """
        handler = StreamHandler(stdout)
        handler.setLevel(DEBUG)
        handler.setFormatter(
            Formatter(fmt=('%(asctime)s %(levelname)-5.5s '
                           '[%(name)s:%(lineno)d] %(message)s'),
                      datefmt='%Y-%m-%d %H:%M:%S'))
        logger = getLogger('wwc')
        logger.setLevel(DEBUG)
        logger.addHandler(handler)
        return logger

    @staticmethod
    def _keywords():
        path = f"{Path(__file__).parent}/../config/keyword.json"
        with open(path, 'r') as file:
            return load(file)

    @staticmethod
    def _websites():
        path = f"{Path(__file__).parent}/../config/supported_websites.json"
        with open(path, 'r') as file:
            return load(file)

    @staticmethod
    def _read_version():
        with open(join(dirname(__file__), '..', '..', 'VERSION'), 'r') as f:
            return f.read().strip()

    @staticmethod
    def _password_gmail():
        return environ.get('PASSWORD_GMAIL')
