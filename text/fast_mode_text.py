
def make_text_for_create_route(address_list: list, city: str) -> str:
    if len(address_list) == 0:
        return f"Давай вместе построим маршрут по городу {city}. \n" \
               f"Чтобы начать, выберите <b>МЕСТО ПОСАДКИ</b> из списка " \
               f"предложенных адресов или напишите новый адрес вручную. " \
               f"Если вам удобнее, можете прислать мне геолокацию нужного " \
               f"места через Telegram, и я найду его для вас.\n\n"\
               "Откуда: \n" \
               "Куда: \n"

    if len(address_list) == 1:
        return "Отлично! Теперь введи <b>МЕСТО НАЗНАЧЕНИЯ</b>, " \
               "куда ты хочешь поехать.\n\n"\
               f"Откуда: <b><b>{address_list[0]}</b></b>\n" \
               "Куда: \n"

    if len(address_list) == 2:
        return f"Отлично, мы готовы начать поиск подходящей поездки по городу {city}! " \
               f"Ниже указаны пункты маршрута:\n\n"\
                f"Откуда: <b>{address_list[0]}</b>\n"\
                f"Куда: <b>{address_list[1]}</b>\n\n"\
                "Если вам нужно указать еще какие-то адреса в маршруте, то введите их сейчас. "\
                "Если же вы готовы продолжить, то нажмите кнопку 'Искать цены', и я начну поиск цен."

    if len(address_list) == 3:
        return f"Отлично, мы готовы начать поиск подходящей поездки по городу {city}! " \
               f"Ниже указаны пункты маршрута:\n\n"\
                f"Откуда: <b>{address_list[0]}</b>\n"\
                f"Остановка 1: <b>{address_list[1]}</b>\n"\
                f"Куда: <b>{address_list[2]}</b>\n\n"\
                "Если вам нужно указать еще какие-то адреса в маршруте, то введите их сейчас. "\
                "Если же вы готовы продолжить, то нажмите кнопку 'Искать цены', и я начну поиск цен."

    if len(address_list) == 4:
        return f"Отлично, мы готовы начать поиск подходящей поездки по городу {city}! " \
               f"Ниже указаны пункты маршрута:\n\n"\
                 f"Откуда: <b>{address_list[0]}</b>\n" \
                 f"Остановка 1: <b>{address_list[1]}</b>\n" \
                 f"Остановка 2: <b>{address_list[2]}</b>\n" \
                 f"Куда: <b>{address_list[3]}</b>\n\n" \
                 'Маршрут может содержать до 4 адресов. Теперь нажми кнопку "Искать цены"'


def make_text_for_running_fast_mode(address_list: list, price_history, best_price) -> str:

    top = f"Каждую минуту я проверяю для тебя цены по маршруту:\n"

    if len(address_list) == 2:
        route = f"Откуда: <b>{address_list[0]}</b>\n"\
                f"Куда: <b>{address_list[1]}</b>\n\n"\

    if len(address_list) == 3:
        route = f"Откуда: <b>{address_list[0]}</b>\n"\
                f"Остановка 1: <b>{address_list[1]}</b>\n"\
                f"Куда: <b>{address_list[2]}</b>\n\n"

    if len(address_list) == 4:
        route = f"Откуда: <b>{address_list[0]}</b>\n" \
                 f"Остановка 1: <b>{address_list[1]}</b>\n" \
                 f"Остановка 2: <b>{address_list[2]}</b>\n" \
                 f"Куда: <b>{address_list[3]}</b>\n\n"

    info = "Я сохраняю возможность оформить заказ на любую цену, которая была полученая за посдедние 10 минут. " \
               'То есть если ты видишь здесь "лучшую цену" 200 рублей, а в "Яндекс такси" стоимость уже 300 рублей по тому же маршруту, ' \
               'то я всё ещё могу оформить для тебя такси за 200 рублей! Для этого нажми "Заказать"\n\n'

    return top + route + info + price_history + best_price


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
        price_time_string += f'В {time_list[i]} цена {price_list[i]}₽ ' + emj + '\n'
    return price_time_string
