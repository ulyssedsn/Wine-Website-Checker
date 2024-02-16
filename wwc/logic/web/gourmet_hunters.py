from re import search
from datetime import datetime, timedelta
from json import load, dump

from wwc.utils.config import WwcConfig
from unidecode import unidecode
from bs4 import BeautifulSoup

cfg = WwcConfig()


class GourmetHunters:
    GH_DOMAIN = 'https://www.gourmethunters.com'
    GH_SEARCH = '/fr/b_'
    GH_HEARDERS = {
        'authority': 'www.gourmethunters.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,'
                  'image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9,fr;q=0.8',
        'cache-control': 'no-cache',
        'dnt': '1',
        'pragma': 'no-cache',
        'referer': 'https://www.gourmethunters.com/fr',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/120.0.0.0 Safari/537.36',
    }

    def __init__(self, requests_session):
        self._requests_session = requests_session

    def search(self):
        all_result = []
        for keyword in cfg.keywords:
            response = self._requests_session.get(
                self._url_builder(keyword), headers=GourmetHunters.GH_HEARDERS)
            result = self._result_analyser(keyword, response.text)
            if result:
                all_result.append(result)
        return [element for sublist in all_result for element in sublist]

    @staticmethod
    def _url_builder(keyword):
        return GourmetHunters.GH_DOMAIN + GourmetHunters.GH_SEARCH + unidecode(
            keyword.replace(' ', '+')).lower()

    def _result_analyser(self, keyword, search_result):
        results = []
        if (("Désolé, mais votre recherche n'a donné aucun résultat. "
             "Pouvons-nous vous recommander l'un de ces vins ?") in
                search_result):
            return

        soup = BeautifulSoup(search_result, 'html.parser')

        for item in soup.find_all("div",
                                  class_="item_view_product item_can_sold"):
            title_container = item.find("div", class_="title_container").h4.a

            title = title_container.text.strip()
            price = item.find("p", itemprop="price").text.strip()
            href = title_container['href'].strip()
            origin_title = item.find("p", class_="origen").a.text.strip()
            image_tag = item.find(
                "img", class_="img-responsive bottle_img vbottom")[
                'src'].strip()

            if search(rf'{keyword.lower()}', title.lower()):
                if self._store_and_compare({'name': title, 'price': price}):
                    results.append({
                        'name': title,
                        'price': price,
                        'link': f"{GourmetHunters.GH_DOMAIN}{href}",
                        'image': {'url': image_tag},
                        'manufacturer_name': origin_title
                    })
            elif (origin_title and
                  search(rf'{keyword.lower()}', origin_title.lower())):
                if self._store_and_compare({'name': title, 'price': price}):
                    results.append({
                        'name': title,
                        'price': price,
                        'link': f"{GourmetHunters.GH_DOMAIN}{href}",
                        'image': {'url': image_tag},
                        'manufacturer_name': origin_title
                    })
        return results

    def _store_and_compare(self, product):
        with open(cfg.file_product_found, 'r') as f:
            data = load(f)

        if product['name'] in data[self.__class__.__name__].keys():
            return not self._check_time_price(
                data[self.__class__.__name__][product['name']], product)

        data[self.__class__.__name__][product['name']] = {
            'timestamp': str(datetime.now()),
            'price': product['price']
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
            return product_json['price'] == product_found['price']
        return False
