from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from json import load, dump

from wwc.utils.config import WwcConfig

cfg = WwcConfig()


class LesZinzinsDuVin:
    LZDV_DOMAIN = 'https://www.leszinzinsduvin.com/'
    LZDV_HEADERS = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,'
                  '*/*;q=0.8',
        'Sec-Fetch-Site': 'none',
        'Accept-Encoding': 'gzip, deflate, br',
        'Sec-Fetch-Mode': 'navigate',
        'Host': 'www.leszinzinsduvin.com',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                      'AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 '
                      'Safari/605.1.15',
        'Accept-Language': 'en-GB,en;q=0.9',
        'Sec-Fetch-Dest': 'document',
        'Connection': 'keep-alive'
    }

    def __init__(self, requests_session, user):
        self._requests_session = requests_session
        self._user_keywords = user['keywords']
        self._user_results = user['results']

    def search(self):
        response = self._requests_session.get(
            LesZinzinsDuVin.LZDV_DOMAIN,
            headers=LesZinzinsDuVin.LZDV_HEADERS
        )
        return self._filter_new_wines(response.text)

    def _filter_new_wines(self, html_page):
        soup = BeautifulSoup(html_page, 'html.parser')
        wines = []

        for wine_div in soup.find_all("div", class_="displayVin"):
            appellation_vin = wine_div.find("h6",
                                            class_="appelation_vin").text.strip()
            nom_domaine = wine_div.find("p", class_="nom_domaine").text.strip()
            prix = wine_div.find("p", class_="prix").text.strip()

            if wine_div.find("div", class_="novelties__blockImg").img:
                photo_vin_src = \
                    (LesZinzinsDuVin.LZDV_DOMAIN +
                     wine_div.find("div", class_="novelties__blockImg").img[
                         'src'])
            else:
                photo_vin_src = 'https://www.leszinzinsduvin.com/ressources/vins/vin_'
            data_url = wine_div.find("div", class_="novelties__card -list")[
                'data-url']

            if self._store_and_compare(
                    {'name': appellation_vin, 'price': prix}):
                wines.append({
                    "name": appellation_vin,
                    "manufacturer_name": nom_domaine,
                    "price": prix,
                    "image": {'url': photo_vin_src},
                    "link": LesZinzinsDuVin.LZDV_DOMAIN + data_url
                })
        return wines

    def _store_and_compare(self, product):
        with open(self._user_results, 'r') as f:
            data = load(f)

        if product['name'] in data[self.__class__.__name__].keys():
            return not self._check_time_price(
                data[self.__class__.__name__][product['name']], product)

        data[self.__class__.__name__][product['name']] = {
            'timestamp': str(datetime.now()),
            'price': product['price']
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
            return product_json['price'] == product_found['price']
        return False
