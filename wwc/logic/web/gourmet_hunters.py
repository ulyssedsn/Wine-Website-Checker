from wwc.utils.config import WwcConfig

cfg = WwcConfig()


class GourmetHunters:
    def __init__(self, requests_session):
        self._requests_session = requests_session

    def search(self):
        for keyword in cfg.keywords:
            # print(f"Start - looking at: {keyword}")
            payload = f"s={keyword}"
            response = self._requests_session.post(
                self._url_builder(), data=payload, headers='')
            self._result_analyser(keyword, response.json())

    def _url_builder(self):
        pass

    def _result_analyser(self, keyword, search_result):
        pass
