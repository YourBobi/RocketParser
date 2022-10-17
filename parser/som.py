import json
import re
from tqdm import tqdm
from .rocketparser import RocketParser, JsonObject


class SomList(RocketParser):
    hrefs: list[str] = []              # Ссылки на страницы
    shops_list: list[JsonObject] = []  # List of JsonObject with shop info

    def __init__(self, url: str, header: dict = None):
        super().__init__(url, header=header)
        self.home_url = url
        self.__set_shops()
        self.__set_city_list()

    def __set_shops(self):
        """
        Запись ссылок на магазины в self.shops_href
        :return: None
        """
        divs = self.body.find("div", attrs={'class': 'col-xs-12 col-sm-6 citys-box'}).find_all("div", class_='col-sm-12')
        city_divs = []

        for i in tqdm(range(len(divs)), desc=f"Запись url {self.url}……", ascii=False, ncols=120):
            city_id = divs[i].input.get('id')
            self.get_div_of_l(city_id, city_divs)

        # ls = div_id.find_all("div", class_='col-sm-12')
        # with ProcessPoolExecutor() as e:
        #     for i in range(len(ls)):
        #         city_id = ls[i].input.get('id')
        #         e.submit(self.get_div_of_l, city_id)

        for el in city_divs:
            self.hrefs.append(self.url[:15] + el.find("a").get("href"))

    def get_div_of_l(self, city_id, city_divs):
        """
        Запрос с cookie который добавляет найденные divs в city_divs
        :param city_id: id города
        :param city_divs: list
        :return: None
        """
        ck = {'BITRIX_SM_CITY_ID': f'{city_id}'}
        shop = RocketParser(self.url, cookies=ck)
        city_divs.extend(shop.body.find_all("div", class_="shops-col shops-button"))

    def __set_city_list(self):
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
        :return: shop = JsonObject()
        """
        shop = JsonObject(href)
        latlon = self.__find_latlon(shop.body)
        name = shop.body.find("h1").get_text(strip=True)
        ad_ph_w = shop.body.find("table", class_='shop-info-table').find_all("td")

        address = ad_ph_w[2].get_text(strip=True)
        phones = self.__find_phones(ad_ph_w[5].get_text(strip=True))
        working_hours = self.__find_working_hours(ad_ph_w[8].get_text(strip=True))

        shop.set_address(address)
        shop.set_latlon(latlon)
        shop.set_name(name)
        shop.set_phones(phones)
        shop.set_working_hours(working_hours)

        return shop

    def __find_latlon(self, body):
        location = body.find("script", text=re.compile("showShopsMap")).get_text(strip=True)
        return re.findall(r"[-+]?\d*\.?\d+|\d+", location)

    def __find_phones(self, string):
        phones = ''.join([x for x in string if x.isdigit() or x == ',' or x.isalpha()])
        return re.findall(r"\d+", phones)

    def __find_working_hours(self, string):
        hours = re.findall(r"\d+", string)
        return [f"пн – вс {hours[0]}:{hours[1]} – {hours[2]}:{hours[3]}"] if len(hours) > 3 else []

    def to_list_of_dict(self):
        return [obj.to_dict() for obj in self.shops_list]

    def to_json(self, link: str = "JsonObject.json"):
        with open(link, 'w', encoding="utf-8") as file:
            json.dump(self.to_list_of_dict(), file, indent=2)
