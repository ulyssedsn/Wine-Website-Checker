from requests import Session
from wwc.logic.factory import Factory
from wwc.utils.config import WwcConfig

cfg = WwcConfig()
requests_session = Session()


def find_wine():
    for website in cfg.websites:
        print(f"--------- Checking {website} ---------")
        Factory.instance('web', website, requests_session).search()


find_wine()
