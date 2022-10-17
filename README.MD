# RocketData

1. Созданные json файлы находятся в папке **"./jsons/"**

2. Список используемых библиотек **requirements.txt**

3. Список классов используемых для парсинга сайтов(./parser/): 
   * RocketParser
   * JsonObject
   * OriencoopList
   * SomList
   * NaturaSiberica

## RocketParser

---

### Описание
Это основной класс в котором происходит запрос по переданному
URL. После этого создается объект класса bs4.BeautifulSoup для 
последующего парсинга.

### Пример использования класса
   ```python
from rocketparser import RocketParser
    
url = "https://oriencoop.cl"
header = {'User-Agent': 'Mozilla/5.0'}
parser = RocketParser(url, header=header)
   ```

### Методы класса
    parsing_rss # Метод для создания полей self.footer self.body
    


## JsonObject

---

### Описание
Класс для хранения данных о магазине. Объекты этого класса используются
для записи в json файлы с помощью метода **self.to_dict()**

### Пример использования класса
   ```python
from rocketparser import JsonObject

url = "https://oriencoop.cl"
header = {'User-Agent': 'Mozilla/5.0'}
j_obj = JsonObject(url, header=header)
j_obj.set_name("name")

   ```

### Методы класса
    set_address()       # изменение поля self.address 
    set_latlon()        # изменение поля self.latlon
    set_name()          # изменение поля self.name
    set_phones()        # изменение поля self.phones
    set_working_hours() # изменение поля self.working_hours
    to_dict()          # возвращает объект в формате dict()




## OriencoopList

---

### Описание
Используется для сайта "https://oriencoop.cl/sucursales.htm"

Класс для хранения и записи в json объектов класса JsonObject, 
которые содержат информацию о магазинах oriencoop.


### Пример использования класса
   ```python
from oriencoop import OriencoopList

if __name__ == '__main__':
    url = 'https://oriencoop.cl/sucursales.htm'
    ori = OriencoopList(url)
    
    # Запись в json 
    ori.to_json("Orien.json")  
   ```

### Методы класса

   ```python
    ori.to_list_of_dict()  # Вывод данных в виде списка словарей
ori.to_json("Orien.json")  # Запись в json 

ori.__set_href()  # Поиск и запись ссылок на магазин
ori.__set_shops()  # Запись магазинов в self.shops_list
   ```

### Основные поля
   ```python
    hrefs: list[str] = []              # Список ссылок на магазины
    orien_list: list[JsonObject] = []  # Список объектов JsonObject ("магазин")
   ```


## SomList

---

### Описание
Используется для сайта "https://som1.ru/shops/"

Класс для хранения и записи в json объектов класса JsonObject, 
которые содержат информацию о магазинах som1.


### Пример использования класса
   ```python
from som import SomList

if __name__ == '__main__':
    url = 'https://som1.ru/shops/'
    som = SomList(url)
    
    # Запись в json 
    som.to_json("Som.json")  
   ```

### Методы класса

   ```python
    som.to_list_of_dict()  # Вывод данных в виде списка словарей
som.to_json("Som.json")  # Запись в json 

som.__set_href()  # Поиск и запись ссылок на магазин
som.__set_shops()  # Запись магазинов в self.shops_list
   ```

### Основные поля
   ```python
    hrefs: list[str] = []              # Список ссылок на магазины
    som_list: list[JsonObject] = []  # Список объектов JsonObject ("магазин")
   ```