from re import search
from datetime import datetime, timedelta
from json import load, dump

from wwc.utils.config import WwcConfig

cfg = WwcConfig()


class CavePurJus:
    CPJ_DOMAIN = 'https://www.cavepurjus.com'
    CPJ_SEARCH = '/fr/recherche'
    CPJ_HEADERS = {
        'authority': 'www.cavepurjus.com',
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'en-US,en;q=0.9,fr;q=0.8',
        'cache-control': 'no-cache',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'dnt': '1',
        'origin': 'https://www.cavepurjus.com',
        'pragma': 'no-cache',
        'referer': 'https://www.cavepurjus.com/fr/',
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'x-requested-with': 'XMLHttpRequest'
    }

    def __init__(self, requests_session, user):
        self._requests_session = requests_session
        self._user_keywords = user['keywords']
        self._user_results = user['results']


    def search(self):
        all_result = []

        for keyword in self._user_keywords:
            # print(f"Start - looking at: {keyword}")
            payload = f"s={keyword}"
            response = self._requests_session.post(
                self._url_builder(), data=payload, headers=self.CPJ_HEADERS)
            result = self._result_analyser(keyword, response.json())
            if result:
                all_result.append(result)
        return [element for sublist in all_result for element in sublist]

    def _url_builder(self):
        return self.CPJ_DOMAIN + self.CPJ_SEARCH

    def _result_analyser(self, keyword, search_result):
        results = []

        if search_result.get('products'):
            for product in search_result.get('products'):
                if product['add_to_cart_url'] and (
                        search(rf'{keyword.lower()}',
                               product['name'].lower())):
                    if self._store_and_compare(product):
                        results.append({
                            'name': product['name'],
                            'price': product['price_amount'],
                            'link': product['add_to_cart_url'],
                            'image': product['cover']['bySize'][
                                'cart_default_2x'],
                            'manufacturer_name': product.get(
                                'manufacturer_name')
                        })
                elif (product.get('manufacturer_name') and
                      search(rf'{keyword.lower()}', product.get(
                          'manufacturer_name').lower())):
                    if self._store_and_compare(product):
                        results.append({
                            'name': product['name'],
                            'price': product['price_amount'],
                            'link': product['add_to_cart_url'],
                            'image': product['cover']['bySize'][
                                'cart_default_2x'],
                            'manufacturer_name': product.get(
                                'manufacturer_name')
                        })
        return results

    def _store_and_compare(self, product):
        with open(self._user_results, 'r') as f:
            data = load(f)
        if product['name'] in data[self.__class__.__name__].keys():
            return not self._check_time_price(
                data[self.__class__.__name__][product['name']], product)

        data[self.__class__.__name__][product['name']] = {
            "timestamp": str(datetime.now()),
            "price": product['price_amount']
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
            return product_json['price'] == product_found['price_amount']
        return False
