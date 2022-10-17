import json
import re
from .rocketparser import RocketParser, JsonObject
from tqdm import tqdm


class OriencoopList(RocketParser):
    hrefs: list[str] = []               # Ссылки на страницы
    shops_list: list[JsonObject] = []   # List of JsonObject with shop info

    def __init__(self, url: str, header: dict = None):
        super().__init__(url, header=header)
        self.__set_href()
        self.__set_shops()

    def __set_href(self):
        """
        Запись ссылок на магазины в self.shops_href
        :return: None
        """
        all_a = []
        for item in self.body.find_all("ul", class_="c-list c-accordion"):
            all_a.extend(item.find_all("a"))

        for a in all_a:
            if a.get('href')[0] == "/":
                href = self.url[:20] + a.get('href')
                self.hrefs.append(href)

    def __set_shops(self):
        """
        Запись объектов shops в self.shops.list
        :return: None
        """
        for i in tqdm(range(len(self.hrefs)), desc=f"Парсинг {self.url}…", ascii=False, ncols=120):
            self.shops_list.append(self.make_shop(self.hrefs[i]))

    def make_shop(self, href: str):
        """
        Создание объекта JsonObject и парсинг в него информации
        :param href: Ссылка на магазин
        :return: shop = JsonObject()
        """
        shop = JsonObject(href)
        div = shop.body.find("div", attrs={'class': 's-dato'})
        span = div.find_all("span")
        div_phone = shop.footer.find("div", attrs={'class': 'b-call shadow'})
        iframe_location = shop.body.find("div", class_="s-mapa").find("iframe")
        address = span[0].get_text(strip=True)
        name = div.h3.get_text(strip=True)
        phones = [phone.get('href')[4:] for phone in div_phone.find_all('a')
                  if phone.get('href')[5].isdigit()]
        working_hours = self.__find_time(span)
        latlon = self.__find_latlon(iframe_location)

        shop.set_address(address)
        shop.set_latlon(latlon)
        shop.set_name(name)
        shop.set_phones(phones)
        shop.set_working_hours(working_hours)

        return shop

    def __find_time(self, span):
        """
        Find time in span
        :param span: bs4 object
        :return: correct list of times
        """
        time = re.findall(r"[-+]?\d*\.?\d+|\d+",
                          span[3].get_text(strip=True) + span[4].get_text(strip=True))
        time = [hour.replace('.', ':') for hour in time]
        if len(time) == 5:
            working_hours = [f"mon-thu {time[0]} - {time[1]} {time[2]}-{time[3]}",
                             f"fri {time[0]} - {time[1]} {time[2]}-{time[3]}"]
        else:
            working_hours = [f"mon-thu {time[0]} - {time[1]}",
                             f"fri {time[0]} - {time[1]}"]
        return working_hours

    def __find_latlon(self, iframe):
        """
        Find latlon in span
        :param iframe:
        :return: correct list of latlon
        """

        google_map = iframe['src']
        location = re.split('!', google_map)
        return [float(location[5][2:]), float(location[6][2:])]

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
