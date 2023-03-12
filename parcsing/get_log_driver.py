import datetime
import re
import time
from csv import DictReader
from pprint import pprint

from selenium import webdriver

URL = 'https://taxi.yandex.ru/?from=gofooter'
PATH_DRIVER = 'parcsing/driver_and_files/chromedriver/chromedriver'
PATH_COOKIES_FILE = 'parcsing/driver_and_files/cookies_taxi.csv'

chrome_options = webdriver.ChromeOptions()
chrome_options.set_capability(
                        "goog:loggingPrefs", {"performance": "ALL", "browser": "ALL"}
                    )
# chrome_options.add_argument(f"--proxy-server='direct://'")  # отключает прокси-сервер
chrome_options.add_argument(
    f"--proxy-bypass-list=*")  # настраивает список сайтов, для которых не нужно использовать прокси-сервер
chrome_options.add_argument(f"--headless")
chrome_options.add_argument(f"--disable-gpu")  # отключает использование GPU для рендеринга страницы.
chrome_options.add_argument('--blink-settings=imagesEnabled=false')
chrome_options.add_argument('--disable-javascript')
chrome_options.add_argument(f"--disable-extensions")  # отключаем расширения
chrome_options.add_argument(f"--start-maximized")  # запускает браузер в режиме максимального размера окна.
chrome_options.add_argument(
    f"--disable-dev-shm-usage")  # отключает использование /dev/shm для обмена данными между процессами браузера.
chrome_options.add_argument(f"--no-sandbox")  # запускает браузер без использования песочницы (sandbox)


def load_url_and_cookies(driver: webdriver.Chrome):
    """Функция загружает страницу и подставляет куки"""

    def get_cookies_values(file):
        with open(file) as f:
            dict_reader = DictReader(f)
            list_of_dict = list(dict_reader)
        return list_of_dict

    cookies = get_cookies_values(PATH_COOKIES_FILE)
    for i in cookies:
        driver.add_cookie(i)
    driver.refresh()
    time.sleep(3)


def get_xtoken(driver: webdriver.Chrome):
    log_entries = driver.get_log("performance")

    log_str = "\n".join([entry['message'] for entry in log_entries])

    match = re.search(r'"X-Csrf-Token":"([^"]+)"', log_str)

    if match:
        csrf_token = match.group(1)
        return csrf_token
    else:
        raise ValueError('X-Csrf-Token header not found')


def get_data_headers(driver: webdriver.Chrome):
    log_entries = driver.get_log("performance")
    headers_data = {
        'cookie': None,
        'csrf_token': None,
        'x_request_id': None,
        'x_yataxi_userid': None,
        'user_agent': None,
        'x_taxi': None
    }
    log_str = "\n".join([entry['message'] for entry in log_entries])


    m_cookie = re.search(r'"Cookie":"([^"]*yandex_login=akkayntnomer3;[^"]*)"', log_str)
    if m_cookie:
        cookie = m_cookie.group(1)
        headers_data['cookie'] = cookie

    match = re.search(r'"X-Csrf-Token":"([^"]+)"', log_str)
    if match:
        csrf_token = match.group(1)
        headers_data['csrf_token'] = csrf_token

    match = re.search(r'"X-Request-Id":"([^"]+)"', log_str)
    if match:
        x_request_id = match.group(1)
        headers_data['x_request_id'] = x_request_id

    match = re.search(r'"X-YaTaxi-UserId":"([^"]+)"', log_str)
    if match:
        x_yataxi_userid = match.group(1)
        headers_data['x_yataxi_userid'] = x_yataxi_userid

    match = re.search(r'"X-Taxi":"([^"]+)"', log_str)
    if match:
        x_taxi = match.group(1)
        headers_data['x_taxi'] = x_taxi

    match = re.search(r'"User-Agent":"([^"]+)"', log_str)
    if match:
        user_agent = match.group(1)
        headers_data['user_agent'] = user_agent

    return headers_data


def get_new_token(driver: webdriver.Chrome):
    """Функция создаёт новую вкладку и переключается на неё фокусе драйвера"""
    driver.switch_to.new_window('tab')
    driver.get(URL)
    time.sleep(3)
    token = get_xtoken(driver)
    driver.close()
    driver.switch_to.window(original_window)
    return token


def get_new_headers_data(driver: webdriver.Chrome):
    """Функция создаёт новую вкладку и переключается на неё фокусе драйвера"""
    driver.switch_to.new_window('tab')
    driver.get(URL)
    time.sleep(3)
    data_headers = get_data_headers(driver)
    driver.close()
    driver.switch_to.window(original_window)
    return data_headers


def create_driver():
    driver = webdriver.Chrome(PATH_DRIVER, options=chrome_options)
    original_window = driver.current_window_handle
    driver.switch_to.new_window('tab')
    driver.get(URL)
    load_url_and_cookies(driver)
    driver.close()
    driver.switch_to.window(original_window)
    return driver, original_window


driver, original_window = create_driver()


for i in range(2):
    data_headers = get_new_headers_data(driver)
pprint(data_headers)
