from bs4 import BeautifulSoup
import bs4
import requests

HEADERS = requests.utils.default_headers()
HEADERS.update({'User-Agent': 'Mozilla/5.0', })


class RocketParser:
    body: bs4.element.Tag
    footer: bs4.element.Tag

    def __init__(self, url: str, *, header: dict = HEADERS, page_source: str = None, cookies: dict = None):

        self.url = url
        self.header = header if header else HEADERS
        self.page_source = page_source
        self.cookies = cookies if cookies else {}
        self.parsing_rss()

    def parsing_rss(self):
        try:
            if not self.page_source:
                self.page_source = requests.get(self.url, headers=self.header, cookies=self.cookies).text
            soup = BeautifulSoup(self.page_source, 'lxml')
        except requests.exceptions.ConnectionError:
            raise requests.exceptions.ConnectionError("Connection error")
        except Exception as e:
            raise e

        self.body = soup.body
        self.footer = soup.footer


class JsonObject(RocketParser):
    address: str
    latlon: list[float]
    name: str
    phones: list[str]
    working_hours: list[str]

    def __init__(self, url: str, header: dict = None, source: str = None, cookies: dict = None):
        super().__init__(url, header=header, page_source=source, cookies=cookies)

    def set_address(self, address: str):
        self.address = address

    def set_latlon(self, latlon: list):
        self.latlon = latlon

    def set_name(self, name: str):
        self.name = name

    def set_phones(self, phones: list):
        self.phones = phones

    def set_working_hours(self, working_hours: list):
        self.working_hours = working_hours

    def to_dict(self):
        return {"address": self.address,
                "latlon": self.latlon,
                "name": self.name,
                "phones": self.phones,
                "working_hours": self.working_hours}
