import datetime
import math
import re
from csv import DictReader
import asyncio
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.common.exceptions import NoSuchWindowException
from selenium.webdriver.chrome.options import Options
from parcsing.browser_processing import act_browser

URL = 'https://taxi.yandex.ru/?from=gofooter'
PATH_DRIVER = 'parcsing/driver_and_files/chromedriver/chromedriver'
PATH_COOKIES_FILE = 'parcsing/driver_and_files/cookies_taxi.csv'
MINUTE_LIVE_SESSION = 10


def get_cookies_values(file):
    with open(file) as f:
        dict_reader = DictReader(f)
        list_of_dict = list(dict_reader)
    return list_of_dict


async def open_browser() -> webdriver.Chrome:
    """Функция создаёт экзепляр драйвера в headless режиме"""

    chrome_options = Options()
    chrome_options.add_argument(f"--proxy-server='direct://'")  # отключает прокси-сервер
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
    driver = webdriver.Chrome(PATH_DRIVER, options=chrome_options)

    return driver


async def load_url_and_cookies(driver: webdriver.Chrome):
    """Функция загружает страницу и подставляет куки"""
    driver.get(URL)
    cookies = get_cookies_values(PATH_COOKIES_FILE)
    for i in cookies:
        driver.add_cookie(i)
    await asyncio.sleep(1)
    driver.refresh()


async def create_order(driver: webdriver.Chrome):
    """Функция жмёт кнопку "заказать такси" """
    await asyncio.sleep(1)
    try:
        driver.find_element(by='class name', value='_31iarc8gLE6KEn039H0091').click()
        return True
    except Exception as ex:
        return False


async def cancellation_when_searching(driver: webdriver.Chrome):
    """Функция отменяет заказ"""
    await asyncio.sleep(1)
    try:
        # жмём кнопку отмены
        driver.find_element(by='class name', value='_6qY_pEVU5SmwbH8hxhUBe').click()
        await asyncio.sleep(1)

        # поддверждаем отмену
        button_no, button_yes = driver.find_elements(by='class name', value='_1DoxiAXzNPfOjm16d1vEO4')
        button_yes.click()
        await asyncio.sleep(1)

        # кнопка Понятно
        driver.find_element(by='class name', value='_1DoxiAXzNPfOjm16d1vEO4').click()
        await asyncio.sleep(1)

        driver.close()
        return True
    except Exception as ex:
        return False


async def close_driver(driver: webdriver.Chrome):
    """Функция закрывает браузер"""

    await asyncio.sleep(.1)
    driver.quit()


def get_inputted(driver: webdriver.Chrome, num_address: int):
    """Фунция забирает что подствлено в строку КУДА"""
    input_destination = driver.find_elements(
        by="class name", value="Textarea-Control")[num_address - 1].text
    return input_destination


async def set_first_address(address, driver: webdriver.Chrome):
    """Функция подставляет нужное значение в поле ОТКУДА"""
    input_address = driver.find_element(by="class name", value="Textarea-Control")
    input_address.send_keys(Keys.SHIFT, Keys.ARROW_UP)
    input_address.send_keys(Keys.DELETE)
    input_address.send_keys(address)
    await asyncio.sleep(2)
    input_address.send_keys(Keys.ARROW_DOWN)
    input_address.send_keys(Keys.ENTER)


async def set_second_address(address, driver: webdriver.Chrome):
    """Функция подставляет нужное значение в поле КУДА"""
    input_address = driver.find_elements(
        by="class name", value="Textarea-Control")[1]
    input_address.send_keys(Keys.SHIFT, Keys.ARROW_UP)
    input_address.send_keys(Keys.DELETE)
    input_address.send_keys(address)
    await asyncio.sleep(2)
    input_address.send_keys(Keys.ARROW_DOWN)
    input_address.send_keys(Keys.ENTER)


async def set_third_address(address: str, driver: webdriver.Chrome):
    """Функция подставляет нужное значение в поле третьего адреса"""
    driver.find_element(by='class name', value='_28m66s3CajkMUAQEfHpCe4').click()
    await asyncio.sleep(2)
    input_address = driver.find_elements(by='class name', value='Textarea-Control')[2]
    input_address.send_keys(address)
    await asyncio.sleep(2)
    input_address.send_keys(Keys.ARROW_DOWN)
    input_address.send_keys(Keys.ENTER)


async def set_fourth_address(address: str, driver: webdriver.Chrome):
    """Функция подставляет нужное значение в поле четвёртого адреса"""
    driver.find_element(by='class name', value='_28m66s3CajkMUAQEfHpCe4').click()
    await asyncio.sleep(2)
    input_address = driver.find_elements(by='class name', value='Textarea-Control')[3]
    input_address.send_keys(address)
    await asyncio.sleep(2)
    input_address.send_keys(Keys.ARROW_DOWN)
    input_address.send_keys(Keys.ENTER)


async def check_price(driver: webdriver.Chrome) -> int:
    """Функция возвращает цену за поездку"""
    await asyncio.sleep(3)
    price = driver.find_element(
        by="class name", value="_3vzsP0WCBDtNC4hYe70Pt_").text
    price = int(price.replace('₽', '').strip())
    return price


async def check_price_repeat(driver: webdriver.Chrome, tab_id) -> int:
    """Функция переключает драйвер на переданную вкладку и возращает цену"""
    await asyncio.sleep(1)
    driver.switch_to.window(tab_id)
    return await check_price(driver)


async def select_button_created_trip(driver: webdriver.Chrome):
    """Если уже есть поиск заказа или происходит поездка на аккаунте,
    то эта функция выберет "создать новую поездку" """
    await asyncio.sleep(3)
    try:
        add_new_trip = driver.find_element(by='class name', value='_3yyQwcte9DdeZQAF_DCPSJ')
        add_new_trip.click()
        return True
    except Exception as ex:
        return False


async def close_last_complete_trip(driver: webdriver.Chrome):
    """Если на странице есть инфа о прошлой завершённой поездке, то её нужно закрыть"""
    await asyncio.sleep(.2)
    try:
        close_last_trip_info = driver.find_element(by='class name', value='_1IMY-OXziGWwEZO8fPxJVU')
        if close_last_trip_info.text == 'Закрыть':
            close_last_trip_info.click()
    except Exception as ex:
        return False


async def create_new_tab(driver: webdriver.Chrome):
    """Функция создаёт новую вкладку и переключается на неё фокусе драйвера"""
    await asyncio.sleep(1)
    driver.execute_script("window.open('');")
    new_tab_id = driver.window_handles[-1]
    driver.switch_to.window(new_tab_id)
    return new_tab_id


def remove_text_in_parentheses(text):
    pattern = r'\([^()]*\)'
    return re.sub(pattern, '', text)


async def get_price(data: dict) -> dict:
    addresses_list: list = data.get('addresses_list')
    city = data.get('city')
    addresses_list = list(map(remove_text_in_parentheses, addresses_list))
    addresses_list = [city + ' ' + address for address in addresses_list]
    driver: webdriver.Chrome = data.get('driver')

    try:
        tab = await create_new_tab(driver)
    except NoSuchWindowException:
        original_tab_id = driver.window_handles[0]
        driver.switch_to.window(original_tab_id)
        tab = await create_new_tab(driver)

    await load_url_and_cookies(driver)

    first_address = addresses_list[0]
    second_address = addresses_list[1]
    try:
        third_address = addresses_list[2]
    except:
        third_address = None
    try:
        fourth_address = addresses_list[3]
    except:
        fourth_address = None

    await select_button_created_trip(driver)
    await close_last_complete_trip(driver)
    await set_first_address(first_address, driver)
    await set_second_address(second_address, driver)
    if third_address:
        await set_third_address(third_address, driver)
    if fourth_address:
        await set_fourth_address(fourth_address, driver)
    price = await check_price(driver)

    data_new = {
        'tab': tab,
        'price': price,
        'first_address_inputted': get_inputted(driver, 1),
        'second_address_inputted': get_inputted(driver, 2),
        'third_address_inputted': get_inputted(driver, 3),
        'fourth_address_inputted': get_inputted(driver, 4)
    }
    if data['iter'] == 1:
        data['addresses_list_yandex'] = [get_inputted(driver, 1),
                                         get_inputted(driver, 2),
                                         get_inputted(driver, 3),
                                         get_inputted(driver, 4)]

    data['addresses_list_yandex_last'] = [get_inputted(driver, 1),
                                          get_inputted(driver, 2),
                                          get_inputted(driver, 3),
                                          get_inputted(driver, 4)]

    data['processing_tab'].update(
        {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'): data_new}
    )

    data['price_history'].append(price)
    data['price_created_history'].append(datetime.datetime.now().strftime('%H:%M'))

    new_tabs_data = act_browser(driver, data['processing_tab'])
    data['processing_tab'] = new_tabs_data
    best_values = next(iter(data['processing_tab'].values()))
    data['best_price'] = best_values.get('price')
    data['best_tab_id'] = best_values.get('tab')
    best_time = next(iter(data['processing_tab'].keys()))
    data['best_price_will_be_active'] = math.ceil(
        (MINUTE_LIVE_SESSION * 60 - (datetime.datetime.now() - datetime.datetime.strptime(best_time,
                                                                                          '%Y-%m-%d %H:%M:%S')).total_seconds()) / 60)
    data['iter'] += 1

    return data
