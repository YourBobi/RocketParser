import json
import re
from .rocketparser import RocketParser, JsonObject
from tqdm import tqdm


class OriencoopList(RocketParser):
    hrefs: list[str] = []
    orien_list: list[JsonObject] = []

    def __init__(self, url: str, header: dict = None):
        super().__init__(url, header=header)
        self.__set_href()
        self.__set_oriencoops()

    def __set_href(self):
        all_a = []
        for item in self.body.find_all("ul", class_="c-list c-accordion"):
            all_a.extend(item.find_all("a"))

        for a in all_a:
            if a.get('href')[0] == "/":
                href = self.url[:20] + a.get('href')
                self.hrefs.append(href)

    def __set_oriencoops(self):
        for i in tqdm(range(len(self.hrefs)), desc=f"Парсинг {self.url}…", ascii=False, ncols=120):
            self.orien_list.append(self.make_ori(self.hrefs[i]))

    def make_ori(self, href: str):
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
        google_map = iframe['src']
        location = re.split('!', google_map)
        return [float(location[5][2:]), float(location[6][2:])]

    def to_list_of_dict(self):
        return [obj.to_dict() for obj in self.orien_list]

    def to_json(self, link: str = "JsonObject.json"):
        with open(link, 'w', encoding="utf-8") as file:
            json.dump(self.to_list_of_dict(), file, indent=2)
