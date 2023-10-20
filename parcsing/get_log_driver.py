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
# chrome_options.add_argument(f"--headless")
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

    cookie = 'yashr=4432544281697807044; i=OBzlwvyxXhkld1jK7UU0YKzLlezSZoDrpB6CVEjMw6aBORbN5sdiqSG40eerOtF9BDkzRlbhOxbGooMoC0l+JQZeLbc=; yandexuid=2683412461697807044; yuidss=2683412461697807044; ymex=2013167045.yrts.1697807045; gdpr=0; _ym_uid=1697807045389510066; _ym_d=1697807045; _ym_isad=1; _ym_visorc=b; spravka=dD0xNjk3ODA3MDUwO2k9ODcuMTAzLjIwOC42MztEPTkyREZCODk4QjJENTQ5NjcxMkNENEZDMjE2MzZEN0M2Njc5NzVFQTM1Mzk5MUQ4Q0ZBODBCMTk1RUY0RDRFODY5QUY2QTREQzQ1NThCNUJBRkNCOUYxQzE4NkVFRTNEMTEyRDRERjQ0RDMyREJFNzQ0MzMxRTg0M0I2MEIwMDQ0QUU2MzU5NTI4RDNBNDIwMkJCMzZGMjczOTJGMTc0NkYwMDM2O3U9MTY5NzgwNzA1MDgyNzUxODI3NjtoPWRmNGZkNWQ4YTQ1OTAyMGNhZDY4NzhjMWMxYjY5OTFi; _yasc=+PWoWHx0ZnXyh6XrapaTez3Oo87Q2K3SeaMGgFNCflIBuCEp7SVNcGDaHUFwZajWzz2tEbxL; Session_id=3:1697807069.5.0.1697807069144:P9BnVw:5b.1.2:1|1904945040.-1.0.3:1697807069|3:10277469.36869.qPmjSz6a2-GpWfe1wDMpZzU8YE4; sessar=1.1183.CiBEQH7LD9k6Dw6mzE2Nj2sS04g40iCopgB1Ex3H6CrfYA.eKEGw-hPxR_xEolmPXjS82BWy0qLNSk7DnWSKJdfUmI; sessionid2=3:1697807069.5.0.1697807069144:P9BnVw:5b.1.2:1|1904945040.-1.0.3:1697807069|3:10277469.36869.fakesign0000000000000000000; yp=2013167069.udn.cDrQkNC90YLQvtC9; L=c1lceEFcWgVOf1N5QnRGBElhcQtfVgYCGklYNA1lCCBBFj1efHs=.1697807069.15501.323060.23d913165e4e3cd838dc855f934a4371; yandex_login=nphne-livrh735; ys=udn.cDrQkNC90YLQvtC9#c_chck.3024575315; bh=Ej8iQ2hyb21pdW0iO3Y9IjExOCIsIkdvb2dsZSBDaHJvbWUiO3Y9IjExOCIsIk5vdD1BP0JyYW5kIjt2PSI5OSIaBSJhcm0iIg8iMTE4LjAuNTk5My44OCIqAj8wOgcibWFjT1MiQggiMTQuMC4wIkoEIjY0IlJaIkNocm9taXVtIjt2PSIxMTguMC41OTkzLjg4IiwiR29vZ2xlIENocm9tZSI7dj0iMTE4LjAuNTk5My44OCIsIk5vdD1BP0JyYW5kIjt2PSI5OS4wLjAuMCIi'

    for item in cookie.split('; '):
        name, value = item[:item.index('=')], item[item.index('=')+1:]
        cookie_item = {'name': name,
                       'value': value,
                       'domain': '.yandex.ru'}
        driver.add_cookie(cookie_item)
    driver.refresh()
    time.sleep(5)


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
    print(data_headers)