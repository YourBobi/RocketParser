import json
import re
import time

import geocoder

from .rocketparser import RocketParser, JsonObject
from selenium.webdriver import Chrome
from selenium.common import TimeoutException
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from deep_translator import GoogleTranslator
from tqdm import tqdm


# Драйвер для полной загрузки страницы
driver_exe = ChromeDriverManager().install()
options = Options()
options.add_argument("--headless")


class NaturaSiberica(RocketParser):
    hrefs: list[str] = []              # Ссылки на страницы
    shops_list: list[JsonObject] = []  # List of JsonObject with shop info

    def __init__(self, url: str, header: dict = None):
        super().__init__(url, header=header)
        self.home_url = url
        self.__set_href()

        self.driver = Chrome(driver_exe, options=options)
        self.__set_natura()
        self.driver.close()

    def __set_href(self):
        """
        Запись ссылок на магазины в self.shops_href
        :return: None
        """
        all_a = []
        for item in self.body.find_all("ul", class_="card-list"):
            all_a.extend(item.find_all("a"))

        for a in all_a:
            href = self.home_url[:-11] + a.get('href')
            self.hrefs.append(href)

    def __set_natura(self):
        """
        Запись объектов shops в self.shops.list
        :return: None
        """
        for i in tqdm(range(len(self.hrefs)), desc=f"Парсинг {self.url}……", ascii=False, ncols=120):
            self.shops_list.append(self.make_shop(self.hrefs[i]))

    def make_shop(self, href: str):
        """
        Создание объекта JsonObject и парсинг в него информации
        :param href: Ссылка на магазин
        :return: shop = JsonObject()"""
        self.driver.get(href)
        shop = self.load_natura(href, 0.5)
        address = shop.body.find("span", class_="select2-selection__rendered").get_text(strip=True)
        latlon = self.__find_latlon(address)
        name = "Natura Siberica"
        phones = self.__find_phones(shop)
        working_hours = self.__find_time(shop)

        shop.set_address(address)
        shop.set_latlon(latlon)
        shop.set_name(name)
        shop.set_phones(phones)
        shop.set_working_hours(working_hours)

        return shop

    def __find_latlon(self, address: str):
        address = GoogleTranslator(source='auto', target='en').translate(address)
        location = geocoder.arcgis(address)
        return location.latlng

    def __find_time(self, shop: JsonObject):
        """
        Find time in shop object
        :param span: bs4 object
        :return: correct list of times
        """
        hours_string = shop.body.find("div", id="schedule1").get_text(strip=True)
        hours = re.findall(r"\d+", hours_string)
        if len(hours) > 3:
            return [f"пн-вс {hours[0]}:{hours[1]}-{hours[2]}:{hours[3]}"]
        return []

    def __find_phones(self, shop: JsonObject):
        """
        Find phones in shop object
        :param span: bs4 object
        :return: correct list of phones
        """
        phones = []

        for p in shop.body.find_all("p", id="shop-phone-by-city"):
            phone = re.findall(r'\d+', p.get_text(strip=True))
            phone = '7' + ''.join(phone)[1:]
            phones.append(phone)

        return phones

    def load_natura(self, href: str, timeout: float):
        """
        Прогружает страницу пока не появятся данные
        :param href: ссылка на shop
        :param timeout: стартовое время загрузки
        :return: shop object
        """
        time.sleep(timeout)

        natura = JsonObject(href, source=self.driver.page_source)
        address = natura.body.find("span", class_="select2-selection__rendered")

        if not address.get_text(strip=True):
            self.load_natura(href, timeout + 0.5)
        elif timeout == 5:
            raise TimeoutException
        return natura

    def to_list_of_dict(self):
        """
        List of dict
        :return: Oriencoop object in list of dict format
        """
        return [obj.to_dict() for obj in self.shops_list]

    def to_json(self, link: str = "JsonObject.json"):
        """
        Save data in json format
        :param link: link of save file
        :return: None
        """
        with open(link, 'w', encoding="utf-8") as file:
            json.dump(self.to_list_of_dict(), file, indent=2)
