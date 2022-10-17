from parser.oriencoop import OriencoopList
from parser.naturasiberica import NaturaSiberica
from parser.som import SomList


if __name__ == '__main__':
    url = 'https://oriencoop.cl/sucursales.htm'
    url1 = 'https://som1.ru/shops/'
    url2 = 'https://naturasiberica.ru/our-shops/'

    # Создание объектов
    ori = OriencoopList(url)
    som = SomList(url1)
    nat = NaturaSiberica(url2)

    # Создание файлов и запись данных
    ori.to_json("./jsons/Orien.json")
    som.to_json("./jsons/Som.json")
    nat.to_json("./jsons/Natura.json")



