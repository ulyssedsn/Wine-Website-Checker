from re import search
from wwc.utils.config import WwcConfig

cfg = WwcConfig()


class MesBourgognesBeaune:
    MBB_DOMAIN = 'https://mesbourgognesbeaune.com'
    MBB_SEARCH = '/en/search'
    MBB_HEADERS = {
        'authority': 'mesbourgognesbeaune.com',
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'en-US,en;q=0.9,fr;q=0.8',
        'cache-control': 'no-cache',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'dnt': '1',
        'origin': 'https://mesbourgognesbeaune.com',
        'pragma': 'no-cache',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/120.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }

    def __init__(self, requests_session):
        self._requests_session = requests_session

    def search(self):
        for keyword in cfg.keywords:
            # print(f"Start - looking at: {keyword}")
            payload = f"s={keyword}"
            response = self._requests_session.post(
                self._url_builder(), data=payload, headers=self.MBB_HEADERS)
            self._result_analyser(keyword, response.json())

    def _url_builder(self):
        return self.MBB_DOMAIN + self.MBB_SEARCH

    @staticmethod
    def _result_analyser(keyword, search_result):
        if search_result.get('products'):
            for product in search_result.get('products'):
                if product['add_to_cart_url'] and (search(rf'{keyword.lower()}', product['name'].lower()) or
                        search(rf'{keyword.lower()}', product.get('manufacturer_name').lower())):
                    print(f"PRODUCT FOUND: {product['name']} |"
                          f" link: {product['link']} |"
                          f" price: {product['price_amount']} |"
                          f" has discount: {product['has_discount']} |"
                          f" discount: {product['discount_amount']}")
                    print(f"add to cart: {product['add_to_cart_url']}")
