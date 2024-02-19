from datetime import datetime, timedelta
from json import load, dump

from wwc.utils.config import WwcConfig
from urllib.parse import quote
from re import search

cfg = WwcConfig()


class VilaViniteca:
    VV_DOMAIN = 'https://www.vilaviniteca.es'
    VV_SEARCH = '/es/searchautocomplete/ajax/suggest/'
    VV_HEADERS = {
  'authority': 'www.vilaviniteca.es',
  'accept': 'application/json, text/javascript, */*; q=0.01',
  'accept-language': 'en-US,en;q=0.9,fr;q=0.8',
  'cache-control': 'no-cache',
  'dnt': '1',
  'pragma': 'no-cache',
  'referer': 'https://www.vilaviniteca.es/es/catalogsearch/result/?q=arbois',
  'sec-ch-ua': '"Chromium";v="121", "Not A(Brand";v="99"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"macOS"',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'same-origin',
  'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 '
                'Safari/537.36',
  'x-requested-with': 'XMLHttpRequest'
}

    def __init__(self, requests_session):
        self._requests_session = requests_session

    def search(self):
        all_result = []
        for keyword in cfg.keywords:
            response = self._requests_session.get(
                self._url_builder(keyword),
                headers=self.VV_HEADERS)
            result = self._result_analyser(keyword, response.json())
            if result:
                all_result.append(result)
        return [element for sublist in all_result for element in sublist]

    def _url_builder(self, keyword):
        query = (f"q={quote(keyword)}")
        return f"{self.VV_DOMAIN}{self.VV_SEARCH}?{query}"

    def _result_analyser(self, keyword, search_result):
        results = []
        if search_result.get('indexes'):
            for product in search_result.get('indexes')[0]['items']:
                if (search(rf'{keyword.lower()}',
                               product['name'].lower())):
                    if self._store_and_compare(product):
                        results.append({
                            'name': product['name'],
                            'price': 'Not Found',
                            'link': product['url'],
                            'image': {'url': product['image']},
                            'manufacturer_name': ''})
        return results

    def _store_and_compare(self, product):
        with open(cfg.file_product_found, 'r') as f:
            data = load(f)
        if product['name'] in data[self.__class__.__name__].keys():
            return not self._check_time_price(
                data[self.__class__.__name__][product['name']], product)

        data[self.__class__.__name__][product['name']] = {
            "timestamp": str(datetime.now()),
            "price": product.get('price_amount')
        }

        with open(cfg.file_product_found, 'w') as f:
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
