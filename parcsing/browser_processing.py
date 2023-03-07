from collections import OrderedDict
from datetime import datetime

from selenium import webdriver

MINUTE_LIVE_SESSION = 10


def close_tab(driver: webdriver.Chrome, tab_id):
    driver.switch_to.window(tab_id)
    driver.close()


def act_browser(driver: webdriver.Chrome, tabs: OrderedDict) -> OrderedDict:
    """Функция записывает новые цены и управляет закрытием и определением не нужных сессий"""

    str_format = '%Y-%m-%d %H:%M:%S'
    now = datetime.now()

    # Проверка на срок жизни сессии
    actual_tabs = OrderedDict()
    for key, value in tabs.items():
        if (now - datetime.strptime(key, str_format)).total_seconds() > 60 * MINUTE_LIVE_SESSION:
            print(
                f"Закрываем вкладку {value.get('tab')} созданную в {key} с ценой {value.get('price')} причина ИСТЕКЛО ВРЕМЯ СЕССИИ")
            close_tab(driver, value.get('tab'))
        else:
            actual_tabs[key] = value
    tabs = actual_tabs

    # Сортируем словарь по возврастанию цены и дате создания сессии
    sorted_prices = sorted(tabs.items(),
                           key=lambda x: (x[1]['price'], -datetime.timestamp(datetime.strptime(x[0], str_format))))
    tabs = OrderedDict(sorted_prices)

    # # оставляем 3 первых сессий
    # actual_tabs = OrderedDict()
    # for i, (key, value) in enumerate(tabs.items()):
    #     if i > 2:
    #         print(
    #             f"Закрываем вкладку для {value.get('tab')} созданную в {key} с ценой {value.get('price')} причина НЕ АКТУАЛЬНО ХРАНИТЬ")
    #         close_tab(driver, value.get('tab'))
    #     else:
    #         actual_tabs[key] = value
    # tabs = actual_tabs

    return tabs
