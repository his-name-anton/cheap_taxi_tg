class TextFastMode:
    NEED_FIRST_ADDRESS = "Давайте построим маршрут по городу {}.\n" \
                         "Выберите <b>МЕСТО ПОСАДКИM</b> из предложженных или напишите новый адрес\n\n" \
                         "Откуда: \n" \
                         "Куда: \n"

    NEED_SECOND_ADDRESS = "Давайте построим маршрут по городу {}.\n" \
                          "Выберите <b>МЕСТО ПОСАДКИM</b> из предложженных или напишите новый адрес\n\n" \
                          "Откуда: {}\n" \
                          "Куда: \n"

    WAIT_THIRD_ADDRESS = "Маршрут для поиска поездки по городу {}\n\n" \
                         "Откуда: {}\n" \
                         "Куда: {}\n\n" \
                         'Можете добавить ещё адреса в поездку или нажмите "Искать цены"'

    WAIT_FOURTH_ADDRESS = "Маршрут для поиска поездки по городу {}\n\n" \
                          "Откуда: {}\n" \
                          "Остановка: {}\n" \
                          "Куда: {}\n\n" \
                          'Можете добавить ещё адреса в поездку или нажмите "Искать цены"'

    SELECT_ALL_ADDRESS = "Маршрут для поиска поездки по городу {}\n\n" \
                         "Откуда: {}\n" \
                         "Остановка 1: {}\n" \
                         "Остановка 2: {}\n" \
                         "Куда: {}\n\n" \
                         'Маршрут может содержать до 4 адресов. Нажмите кнопку "Искать"'


def make_text_for_running_fast_mode(data: dict) -> str:
    addresses_list = data.get('addresses_list_yandex')
    addresses_list = list(filter(lambda x: x != '', addresses_list))
    city = data.get('city')
    if len(addresses_list) == 2:
        return f"Маршрут для поиска поездки по городу {city}\n\n" \
               f"Откуда: {addresses_list[0]}\n" \
               f"Куда: {addresses_list[1]}\n" \
               f"(Адреса взяты из яндекс)\n"
    elif len(addresses_list) == 3:
        return f"Маршрут для поиска поездки по городу {city}\n\n" \
               f"Откуда: {addresses_list[0]}\n" \
               f"Остановка: {addresses_list[1]}\n" \
               f"Куда: {addresses_list[2]}\n" \
               f"(Адреса взяты из яндекс)\n"
    elif len(addresses_list) == 4:
        return f"Маршрут для поиска поездки по городу {city}\n\n" \
               f"Откуда: {addresses_list[0]}\n" \
               f"Остановка 1: {addresses_list[1]}\n" \
               f"Остановка 2: {addresses_list[2]}\n" \
               f"Куда: {addresses_list[3]}\n" \
               f"(Адреса взяты из яндекс)\n"


def create_price_time_string(price_list: list, time_list: list):
    """Функция создаёт строку из прошлых цен"""
    price_time_string = ''

    if len(price_list) > 10:
        price_list = price_list[-10:]
        time_list = time_list[-10:]

    for i in range(len(price_list)):
        emj = ''
        try:
            prev_price = price_list[i - 1]
            if prev_price > price_list[i]:
                emj = '↘️'
            elif prev_price < price_list[i]:
                emj = '↗️'
            elif prev_price == price_list[i]:
                emj = '↔️'
        except:
            pass
        price_time_string += f'В {time_list[i]} цена {price_list[i]} ' + emj + '\n'
    return price_time_string
