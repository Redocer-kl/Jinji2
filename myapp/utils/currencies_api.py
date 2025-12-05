"""Утилиты для получения курсов валют из XML API.

В качестве примера используется формат XML Центрального банка РФ (CBR).
Функция `get_currencies` возвращает список словарей с ключами:
'id', 'num_code', 'char_code', 'name', 'value', 'nominal'.
"""

from typing import List, Dict, Optional
import requests
import xml.etree.ElementTree as ET


DEFAULT_CBR_URL = "https://www.cbr.ru/scripts/XML_daily.asp"


def parse_valute_element(elem: ET.Element) -> Dict[str, object]:
    """Разобрать элемент <Valute> из XML и вернуть словарь полей.

    Параметры
    ---------
    elem : ET.Element
        Элемент Valute из XML.

    Возвращает
    ---------
    dict
        Словарь с ключами: id, num_code, char_code, name, nominal, value.
    """
    vid = elem.attrib.get("ID", "")
    num_code = elem.findtext("NumCode", default="")
    char_code = elem.findtext("CharCode", default="")
    nominal_text = elem.findtext("Nominal", default="1")
    name = elem.findtext("Name", default="")
    value_text = elem.findtext("Value", default="0")

    try:
        nominal = int(nominal_text)
    except (TypeError, ValueError):
        nominal = 1

    # Значение приходит в формате '48,6178' — заменяем запятую
    value_text = value_text.replace(",", ".")
    try:
        value = float(value_text)
    except (TypeError, ValueError):
        value = 0.0

    return {
        "id": vid,
        "num_code": num_code,
        "char_code": char_code,
        "name": name,
        "value": value,
        "nominal": nominal,
    }


def get_currencies(url: Optional[str] = None, timeout: int = 10) -> List[Dict[str, object]]:
    """Получить список валют из XML API.

    Параметры
    ---------
    url : Optional[str]
        URL для загрузки XML. Если None, используется `DEFAULT_CBR_URL`.
    timeout : int
        Таймаут запроса в секундах.

    Возвращает
    ---------
    List[Dict[str, object]]
        Список словарей с данными валют.

    Исключения
    ----------
    requests.RequestException
        При сетевых ошибках.
    ET.ParseError
        При ошибке разбора XML.
    """
    target = url or DEFAULT_CBR_URL
    resp = requests.get(target, timeout=timeout)
    resp.raise_for_status()

    root = ET.fromstring(resp.content)

    currencies = []
    for val in root.findall("Valute"):
        currencies.append(parse_valute_element(val))
    return currencies

