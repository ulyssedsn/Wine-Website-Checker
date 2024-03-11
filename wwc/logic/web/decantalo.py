from datetime import datetime, timedelta
from json import load, dump

from wwc.utils.config import WwcConfig
from urllib.parse import quote
from re import search

cfg = WwcConfig()


class Decantalo:
    D_DOMAIN = 'https://eu1-search.doofinder.com/'
    D_SEARCH = '5/search'
    D_HEADERS = {
        'authority': 'eu1-search.doofinder.com',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9,fr;q=0.8',
        'cache-control': 'no-cache',
        'dnt': '1',
        'origin': 'https://www.decantalo.com',
        'pragma': 'no-cache',
        'referer': 'https://www.decantalo.com/',
        'sec-ch-ua': '"Chromium";v="121", "Not A(Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/121.0.0.0 Safari/537.36'
    }

    def __init__(self, requests_session, user):
        self._requests_session = requests_session
        self._user_keywords = user['keywords']
        self._user_results = user['results']


    def search(self):
        all_result = []
        for keyword in self._user_keywords:
            response = self._requests_session.get(
                self._url_builder(keyword),
                headers=self.D_HEADERS)
            result = self._result_analyser(keyword, response.json())
            if result:
                all_result.append(result)
        return [element for sublist in all_result for element in sublist]

    def _url_builder(self, keyword):
        query = (f"page=1&rpp=30&transformer=&type=product&query"
                 f"={quote(keyword)}&hashid=e4235f546eaafb09260bb678e9b49e2c")
        return f"{self.D_DOMAIN}{self.D_SEARCH}?{query}"

    def _result_analyser(self, keyword, search_result):
        results = []
        if search_result.get('results'):
            for product in search_result.get('results'):
                if product['availability'] == 'in stock' and (
                        search(rf'{keyword.lower()}',
                               product['title'].lower()) or
                        search(rf'{keyword.lower()}',
                               product.get('brand').lower())):
                    if self._store_and_compare(product):
                        results.append({
                            'name': product['title'],
                            'price': 'Not Found',
                            'link': f"https://www.decantalo.com/es/en/{product['link']}",
                            'image': {'url': product['image_link']},
                            'manufacturer_name': product['brand']})
        return results

    def _store_and_compare(self, product):
        with open(self._user_results, 'r') as f:
            data = load(f)
        if product['title'] in data[self.__class__.__name__].keys():
            return not self._check_time_price(
                data[self.__class__.__name__][product['title']], product)

        data[self.__class__.__name__][product['title']] = {
            "timestamp": str(datetime.now()),
            "price": ''
        }

        with open(self._user_results, 'w') as f:
            dump(data, f, indent=4)
        return True

    @staticmethod
    def _check_time_price(product_json, product_found):
        now = datetime.now()
        if now - datetime.strptime(
                product_json['timestamp'],
                '%Y-%m-%d %H:%M:%S.%f') > timedelta(
            seconds=cfg.expiration_time):
            return product_json['price'] == ''
        return False
