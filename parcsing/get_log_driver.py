import os
import re
import time
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
from selenium import webdriver

URL = 'https://taxi.yandex.ru/?from=gofooter'
PATH_DRIVER = 'parcsing/driver_and_files/chromedriver'

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

    cookie = 'ym_uid=1670490608167719583; _ym_d=1670490609; yashr=1819935411674096423; gdpr=0; my=YwA=; font_loaded=YSv1; skid=1964573971677503570; yandexuid=8943791831670490607; yuidss=8943791831670490607; i=lkoaiiXTfJGECbJ8bzMY+bbFt+WVc6eLmYjRwQcgfyXVV6TW2L1ZJAS7Zxgo+CEkKSlXVwkcgVFzfAUBTanKXMvA3KY=; ymex=1681303309.oyu.5464549601678610412#1993970412.yrts.1678610412#1993970412.yrtsi.1678610412; uxs_uid=98d44320-c19c-11ed-9d8a-113b6a9be453; is_gdpr=0; is_gdpr_b=CJ6rGBDgrAEoAg==; yp=1990954416.multib.1#1694486733.szm.2:1800x1169:1800x987#1994585979.udn.cDrQkNC90YLQvtC9INCb0LDRgNC40L0%3D#1678797709.yu.5464549601678610412; L=YnZnBXVfRXkGflhBBF9nBAZJenUHaFYKD1ktL0xYJ10iDlUjSw==.1679225979.15286.331900.9b0b4907654db2fa64107a4d562696d2; yandex_login=akkayntnomer3; AMP_MKTG_332f8b000f=JTdCJTIycmVmZXJyZXIlMjIlM0ElMjJodHRwcyUzQSUyRiUyRnd3dy5nb29nbGUuY29tJTJGJTIyJTJDJTIycmVmZXJyaW5nX2RvbWFpbiUyMiUzQSUyMnd3dy5nb29nbGUuY29tJTIyJTdE; AMP_332f8b000f=JTdCJTIyb3B0T3V0JTIyJTNBZmFsc2UlMkMlMjJkZXZpY2VJZCUyMiUzQSUyMjkzNzJiODk4LWE2MzQtNGQyMC04MWVkLTVjYzEyMTFhZWU1MCUyMiUyQyUyMmxhc3RFdmVudFRpbWUlMjIlM0ExNjgxMjkzMjU0MjU1JTJDJTIyc2Vzc2lvbklkJTIyJTNBMTY4MTI5MzI1MDgxMyUyQyUyMnVzZXJJZCUyMiUzQSUyMnVuZGVmaW5lZCUyMiU3RA==; yabs-sid=907133491685775127; Session_id=3:1685775536.5.0.1678554937639:P9BnVw:24.1.2:1|323357137.-1.2.3:1678554937|1765907004.-1.2.2:165285.3:1678720222|3:10270787.44336.BeFBbvIcxX03Fp9Q1n5ITOItBCo; sessar=1.99.CiCwdcMPTIXWLKQ5LNhNcfifIWNN3KIp4jQOCouBK22-nA.uuxPNkP0rlVN4H4acP9cSteVFAC1_Xy-6PVHWBBoGK0; sessionid2=3:1685775536.5.0.1678554937639:P9BnVw:24.1.2:1|323357137.-1.2.3:1678554937|1765907004.-1.2.2:165285.3:1678720222|3:10270787.44336.fakesign0000000000000000000; _ym_isad=1; bh=EkEiR29vZ2xlIENocm9tZSI7dj0iMTEzIiwgIkNocm9taXVtIjt2PSIxMTMiLCAiTm90LUEuQnJhbmQiO3Y9IjI0IhoFImFybSIiECIxMTMuMC41NjcyLjEyNiIqAj8wOgcibWFjT1MiQggiMTMuNC4wIkoEIjY0IlJcIkdvb2dsZSBDaHJvbWUiO3Y9IjExMy4wLjU2NzIuMTI2IiwiQ2hyb21pdW0iO3Y9IjExMy4wLjU2NzIuMTI2IiwiTm90LUEuQnJhbmQiO3Y9IjI0LjAuMC4wIiJaAj8w; _yasc=fejZLb0LTO0q5QL0l9hanUfWd4vYzbKDlm/hR9EgWMuM5IxkqU6449bEBnuQoA=='

    for item in cookie.split('; '):
        name, value = item[:item.index('=')], item[item.index('=')+1:]
        cookie_item = {'name': name,
                       'value': value,
                       'domain': '.yandex.ru'}
        driver.add_cookie(cookie_item)
    driver.refresh()
    time.sleep(10)


def get_xtoken(driver: webdriver.Chrome):
    log_entries = driver.get_log("performance")

    log_str = "\n".join([entry['message'] for entry in log_entries])

    match = re.search(r'"X-Csrf-Token":"([^"]+)"', log_str)

    if match:
        csrf_token = match.group(1)
        return csrf_token
    else:
        raise ValueError('X-Csrf-Token header not found')


def get_payment_method_id(driver: webdriver.Chrome):
    pass


def check_all_cards(driver: webdriver.Chrome):
    class_click_payment_method = '_9p-ZM4NmsWGJ3dm_mIK1F'
    class_card = 'xrSY6XawT5_2qYrZ5_e7Y'
    driver.find_element(by='class name', value=class_click_payment_method).click()
    time.sleep(5)
    payment_chooses = driver.find_elements(by='class name', value=class_card)
    payment_chooses_names = [item.text for item in payment_chooses]
    # for item in payment_chooses:

    # time.sleep(1000)


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

    match = re.search('"payment_method_id":"([^"]+)"', log_str)
    if match:
        payment_method_id = match.group(1)
        headers_data['payment_method_id'] = payment_method_id

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
    """Функция создаёт и драйвер и открывет браузер"""

    driver = webdriver.Chrome(PATH_DRIVER, options=chrome_options)
    original_window = driver.current_window_handle
    driver.switch_to.new_window('tab')
    driver.get(URL)
    load_url_and_cookies(driver)
    check_all_cards(driver)
    driver.close()
    driver.switch_to.window(original_window)
    return driver, original_window


driver, original_window = create_driver()


for i in range(1):
    data_headers = get_new_headers_data(driver)