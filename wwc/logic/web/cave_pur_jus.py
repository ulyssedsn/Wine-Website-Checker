from re import search

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

    def __init__(self, requests_session):
        self.requests_session = requests_session

    def search(self, keywords):
        for keyword in keywords:
            # print(f"Start - looking at: {keyword}")
            payload = f"s={keyword}"
            response = self.requests_session.post(
                self._url_builder(), data=payload, headers=self.CPJ_HEADERS)
            self._result_analyser(keyword, response.json())

    def _url_builder(self):
        return self.CPJ_DOMAIN + self.CPJ_SEARCH

    def _result_analyser(self, keyword, search_result):
        if search_result.get('products'):
            for product in search_result.get('products'):
                if search(rf'{keyword.lower()}', product['name'].lower()):
                    print(f"PRODUCT FOUND: {product['name']} |"
                          f" link: {product['link']} |"
                          f" price: {product['price_amount']} |"
                          f" has discount: {product['has_discount']} |"
                          f" discount: {product['discount_amount']}")
                    print(f"add to cart: {product['add_to_cart_url']}")
