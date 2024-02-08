from requests import Session
from wwc.logic.factory import Factory
from wwc.utils.config import WwcConfig

cfg = WwcConfig()
requests_session = Session()


def find_wine():
    for website in cfg.websites:
        Factory.instance('web', website, requests_session)


find_wine()
