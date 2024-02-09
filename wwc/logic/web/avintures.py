from wwc.utils.config import WwcConfig
from urllib.parse import quote
from re import search

cfg = WwcConfig()

"https://www.avintures.fr/fr/module/leoproductsearch/productsearch?q=arbois&timestamp=1707483561391&ajaxSearch=1&id_lang=1&leoproductsearch_static_token=4b929f82862a52568f90db02682134f5"


class Avintures:
    A_DOMAIN = 'https://www.avintures.fr'
    A_SEARCH = '/fr/module/leoproductsearch/productsearch'
    A_HEADERS = {
        'authority': 'www.avintures.fr',
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'en-US,en;q=0.9,fr;q=0.8',
        'cache-control': 'no-cache',
        'dnt': '1',
        'pragma': 'no-cache',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }

    def __init__(self, requests_session):
        self._requests_session = requests_session

    def search(self):
        for keyword in cfg.keywords:
            # print(f"Start - looking at: {keyword}")
            payload = f"s={keyword}"

            response = self._requests_session.get(
                self._url_builder(keyword),
                headers=self.A_HEADERS)
            self._result_analyser(keyword, response.json())

    def _url_builder(self, keyword):
        query = (f"q={quote(keyword)}&timestamp=1707483561391&ajaxSearch=1"
                 f"&id_lang=1&leoproductsearch_static_token"
                 f"=4b929f82862a52568f90db02682134f5")
        return f"{self.A_DOMAIN}{self.A_SEARCH}?{query}"

    @staticmethod
    def _result_analyser(keyword, search_result):
        if search_result.get('products'):
            for product in search_result.get('products'):
                if product['add_to_cart_url'] and (
                        search(rf'{keyword.lower()}',
                               product['name'].lower()) or
                        search(rf'{keyword.lower()}',
                               product.get('manufacturer_name').lower())):

                    print(f"PRODUCT FOUND for {keyword}: {product['name']} |"
                          f" link: {product['link']} |"
                          f" price: {product['price_amount']} |"
                          f" has discount: {product['has_discount']} |"
                          f" discount: {product['discount_amount']}")
                    print(f"add to cart: {product['add_to_cart_url']}")
