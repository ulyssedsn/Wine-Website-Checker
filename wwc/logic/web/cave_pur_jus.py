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
        self._requests_session = requests_session

    def search(self):
        all_result = []

        for keyword in cfg.keywords:
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

    @staticmethod
    def _result_analyser(keyword, search_result):
        results = []

        if search_result.get('products'):
            for product in search_result.get('products'):
                if product['add_to_cart_url'] and (
                        search(rf'{keyword.lower()}',
                               product['name'].lower())):
                    # print(f"PRODUCT FOUND: {product['name']} |"
                    #       f" link: {product['link']} |"
                    #       f" price: {product['price_amount']} |"
                    #       f" has discount: {product['has_discount']} |"
                    #       f" discount: {product['discount_amount']}")
                    # print(f"add to cart: {product['add_to_cart_url']}")
                    results.append({
                        'name': product['name'],
                        'price': product['price_amount'],
                        'link': product['add_to_cart_url'],
                        'image': product['cover']['bySize']['cart_default_2x']
                    })
                elif (product.get('manufacturer_name') and
                      search(rf'{keyword.lower()}', product.get(
                          'manufacturer_name').lower())):
                    # print(f"PRODUCT FOUND: {product['name']} |"
                    #       f" link: {product['link']} |"
                    #       f" price: {product['price_amount']} |"
                    #       f" has discount: {product['has_discount']} |"
                    #       f" discount: {product['discount_amount']}")
                    results.append({
                        'name': product['name'],
                        'price': product['price_amount'],
                        'link': product['add_to_cart_url'],
                        'image': product['cover']['bySize']['cart_default_2x']
                    })
        return results
