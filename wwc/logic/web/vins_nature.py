from re import search
from datetime import datetime, timedelta
from json import load, dump

from wwc.utils.config import WwcConfig

cfg = WwcConfig()


class VinsNature:
    VN_DOMAIN = 'https://www.vinsnature.fr'
    VN_SEARCH = '/recherche'
    VN_HEADERS = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'DNT': '1',
        'Origin': 'https://www.vinsnature.fr',
        'Pragma': 'no-cache',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/121.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Chromium";v="121", "Not A(Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"'
    }

    def __init__(self, requests_session, user):
        self._requests_session = requests_session
        self._user_keywords = user['keywords']
        self._user_results = user['results']

    def search(self):
        all_result = []

        for keyword in self._user_keywords:
            payload = f"s={keyword}&resultsPerPage=30"
            response = self._requests_session.post(
                self._url_builder(), data=payload, headers=self.VN_HEADERS)
            result = self._result_analyser(keyword, response.json())
            if result:
                all_result.append(result)
        return [element for sublist in all_result for element in sublist]

    def _url_builder(self):
        return self.VN_DOMAIN + self.VN_SEARCH

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
                                'cart_default'],
                            'manufacturer_name': product.get(
                                'manufacturer_name')
                        })
                elif (product['add_to_cart_url'] and
                       (product.get('manufacturer_name') and
                      search(rf'{keyword.lower()}', product.get(
                          'manufacturer_name').lower()))):
                    if self._store_and_compare(product):
                        results.append({
                            'name': product['name'],
                            'price': product['price_amount'],
                            'link': product['add_to_cart_url'],
                            'image': product['cover']['bySize'][
                                'cart_default'],
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
