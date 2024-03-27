import configparser

from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from json import load, dump

from requests import Session

from wwc.utils.config import WwcConfig

cfg = WwcConfig()


class LesZinzinsDuVin:
    LZDV_DOMAIN = 'https://www.leszinzinsduvin.com/vins.php'
    LZDV_HEADERS = {
        'authority': 'www.leszinzinsduvin.com',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9,fr;q=0.8',
        'cache-control': 'no-cache',
        'content-type': 'application/x-www-form-urlencoded',
        'dnt': '1',
        'origin': 'https://www.leszinzinsduvin.com',
        'pragma': 'no-cache',
        'referer': 'https://www.leszinzinsduvin.com/vins.php',
        'sec-ch-ua': '"Not(A:Brand";v="24", "Chromium";v="122"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }

    def __init__(self, requests_session, user):
        self._requests_session = requests_session
        self._user_keywords = user['keywords']
        self._user_results = user['results']

    def search(self):
        wines = []
        index = 0
        while True:
            payload = f'xajax=recherche&xajaxr=1711110398872&xajaxargs%5B%5D=%3Cxjxquery%3E%3Cq%3Eregion%3D%26prix%3D%26cepage%3D%26couleur%3D%3C%2Fq%3E%3C%2Fxjxquery%3E&xajaxargs%5B%5D={index}'
            response = self._requests_session.post(
                LesZinzinsDuVin.LZDV_DOMAIN,
                data=payload,
                headers=LesZinzinsDuVin.LZDV_HEADERS
            )
            response.raise_for_status()
            if len(response.text) < 500:
                return wines
            wines = wines + self._filter_new_wines(response.text)
            index += 1


    def _filter_new_wines(self, html_page):
        soup = BeautifulSoup(html_page, "xml")
        html_content = soup.find('cmd', attrs={'t': 'liste_vins'}).text
        soup_html = BeautifulSoup(html_content, "html.parser")


        wines = []
        for wine_card in soup_html.find_all("div", class_="novelties__card -list"):
            appelation_vin = wine_card.find("h6", class_="appelation_vin").get_text(strip=True) if wine_card.find(
                "h6", class_="appelation_vin") else "N/A"
            nom_domaine = wine_card.find("p", class_="nom_domaine").get_text(strip=True) if wine_card.find(
                "p",class_="nom_domaine") else "N/A"
            bouche_vin = wine_card.find("p", class_="bouche_vin").get_text(strip=True) if wine_card.find(
                "p", class_="bouche_vin") else "N/A"
            prix = wine_card.find("p", class_="prix").get_text(strip=True) if wine_card.find(
                "p", class_="prix") else "N/A"
            photo_vin = wine_card.find("img", class_="photo_vin")["src"].strip() if wine_card.find(
                "img", class_="photo_vin") else "N/A"
            data_url = wine_card["data-url"].strip() if "data-url" in wine_card.attrs else "N/A"

            if self._store_and_compare(
                    {'name': appelation_vin, 'price': prix}):
                wines.append({
                    "name": appelation_vin,
                    "manufacturer_name": nom_domaine,
                    "price": prix,
                    "image": {'url': "https://www.leszinzinsduvin.com/" + photo_vin},
                    "link": "https://www.leszinzinsduvin.com/" + data_url
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
