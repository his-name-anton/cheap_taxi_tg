import re
import aiohttp
import os

from pprint import pprint
from typing import List
from dotenv import load_dotenv, find_dotenv
from data_base.data_base import db
from parcsing.get_log_driver import get_new_token, driver, data_headers

load_dotenv(find_dotenv())


cookie = 'yashr=4432544281697807044; i=OBzlwvyxXhkld1jK7UU0YKzLlezSZoDrpB6CVEjMw6aBORbN5sdiqSG40eerOtF9BDkzRlbhOxbGooMoC0l+JQZeLbc=; yandexuid=2683412461697807044; yuidss=2683412461697807044; ymex=2013167045.yrts.1697807045; gdpr=0; _ym_uid=1697807045389510066; _ym_d=1697807045; _ym_isad=1; _ym_visorc=b; spravka=dD0xNjk3ODA3MDUwO2k9ODcuMTAzLjIwOC42MztEPTkyREZCODk4QjJENTQ5NjcxMkNENEZDMjE2MzZEN0M2Njc5NzVFQTM1Mzk5MUQ4Q0ZBODBCMTk1RUY0RDRFODY5QUY2QTREQzQ1NThCNUJBRkNCOUYxQzE4NkVFRTNEMTEyRDRERjQ0RDMyREJFNzQ0MzMxRTg0M0I2MEIwMDQ0QUU2MzU5NTI4RDNBNDIwMkJCMzZGMjczOTJGMTc0NkYwMDM2O3U9MTY5NzgwNzA1MDgyNzUxODI3NjtoPWRmNGZkNWQ4YTQ1OTAyMGNhZDY4NzhjMWMxYjY5OTFi; _yasc=+PWoWHx0ZnXyh6XrapaTez3Oo87Q2K3SeaMGgFNCflIBuCEp7SVNcGDaHUFwZajWzz2tEbxL; Session_id=3:1697807069.5.0.1697807069144:P9BnVw:5b.1.2:1|1904945040.-1.0.3:1697807069|3:10277469.36869.qPmjSz6a2-GpWfe1wDMpZzU8YE4; sessar=1.1183.CiBEQH7LD9k6Dw6mzE2Nj2sS04g40iCopgB1Ex3H6CrfYA.eKEGw-hPxR_xEolmPXjS82BWy0qLNSk7DnWSKJdfUmI; sessionid2=3:1697807069.5.0.1697807069144:P9BnVw:5b.1.2:1|1904945040.-1.0.3:1697807069|3:10277469.36869.fakesign0000000000000000000; yp=2013167069.udn.cDrQkNC90YLQvtC9; L=c1lceEFcWgVOf1N5QnRGBElhcQtfVgYCGklYNA1lCCBBFj1efHs=.1697807069.15501.323060.23d913165e4e3cd838dc855f934a4371; yandex_login=nphne-livrh735; ys=udn.cDrQkNC90YLQvtC9#c_chck.3024575315; bh=Ej8iQ2hyb21pdW0iO3Y9IjExOCIsIkdvb2dsZSBDaHJvbWUiO3Y9IjExOCIsIk5vdD1BP0JyYW5kIjt2PSI5OSIaBSJhcm0iIg8iMTE4LjAuNTk5My44OCIqAj8wOgcibWFjT1MiQggiMTQuMC4wIkoEIjY0IlJaIkNocm9taXVtIjt2PSIxMTguMC41OTkzLjg4IiwiR29vZ2xlIENocm9tZSI7dj0iMTE4LjAuNTk5My44OCIsIk5vdD1BP0JyYW5kIjt2PSI5OS4wLjAuMCIi'
headers = {
    'content-type': 'application/json',
    'referer': 'https://taxi.yandex.ru/',
    'cookie': cookie,
    'user-agent':  data_headers.get('user_agent'),
    'x-taxi': data_headers.get('x_taxi'),
    'x-csrf-token': data_headers.get('csrf_token'),
    'x-request-id': data_headers.get('x_request_id'),
    'x-yataxi-userid': data_headers.get('x_yataxi_userid'),
}


def handle_csrf_token(func):
    async def wrapper(*args, **kwargs):
        response = await func(*args, **kwargs)
        cant_none = kwargs.get('cant_none')
        if not response and not cant_none:
            print(f'error api responce: \n{response}')
            global headers
            new_token = get_new_token(driver)
            headers['x-csrf-token'] = new_token
            db.insert_row('csrf_tokens', (new_token, ))
            print(f"Обновил токен {headers['x-csrf-token']}")
            response = await func(*args, **kwargs)
        return response

    return wrapper


@handle_csrf_token
async def get_price_yandex(route: List[List[float]], cant_none=False) -> str:
    card_id = os.getenv('CARD_YANDEX')
    yataxi_id = data_headers.get('x_yataxi_userid')
    data = {
        "route": route,
        "selected_class": "",
        "format_currency": True,
        "requirements": {"coupon": ""},
        "payment": {"type": "card", "payment_method_id": card_id},
        "id": yataxi_id,
        "summary_version": 2,
        "is_lightweight": False,
        "extended_description": True,
        "supported_markup": "tml-0.1",
        "supports_paid_options": True,
        "tariff_requirements": [
            {"class": "econom", "requirements": {"coupon": ""}},
            {"class": "business", "requirements": {"coupon": ""}},
            {"class": "child_tariff", "requirements": {"coupon": ""}},
        ],
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.post(
                "https://ya-authproxy.taxi.yandex.ru/3.0/routestats", json=data
        ) as response:
            if response.status == 401:
                pprint(await response.json())
                return False
            response_json = await response.json()
            price_value = response_json["service_levels"][0]["details"][0]["price"]
            price_value = int(re.sub(r"\D", "", price_value))
            offer = response_json["offer"]
            return offer, price_value


@handle_csrf_token
async def get_orderid(offer: str,
                      addresses_locs: list[list[float]],
                      city: str,
                      name_person: str,
                      phone_person: str,
                      payment_type: str = "cash") -> str:
    """Функция отправляет пост для создание ордера с нужными настройками

        offer: передаём офер для создание ордера для этого офера
        city: передаём город где случиться поездка
        name_person: имя того кому заказываем такси
        phone_person: номер телефона того, кому заказываем такси
        payment_type: способ оплаты, умолчание = "cash"

    """
    url = 'https://ya-authproxy.taxi.yandex.ru/external/3.0/orderdraft'
    payment_method_id = os.getenv('CARD_YANDEX') if payment_type == "card" else "cash"

    route = []
    for loc in addresses_locs:
        route.append({
            "short_text": "",
            "geopoint": loc,
            "fullname": "",
            "type": "address",
            "city": city,
            "uri": ""
        })

    data = {
        "id": data_headers.get('x_yataxi_userid'),
        "class": [
            "econom"
        ],
        "payment": {
            "type": payment_type,
            "payment_method_id": payment_method_id
        },
        "offer": offer,
        "parks": [

        ],
        "route": route,
        "requirements": {
            "coupon": ""
        },
        "dont_sms": False,
        # "extra_contact_phone": phone_person,
        # "extra_passenger_name": name_person,
        "driverclientchat_enabled": True
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.post(
                url, json=data
        ) as response:
            if response.status == 401:
                return False
            response_json = await response.json()
            pprint(response_json)
            orderid = response_json['orderid']
            return orderid


@handle_csrf_token
async def create_order_yandex(orderid):
    url = 'https://ya-authproxy.taxi.yandex.ru/external/3.0/ordercommit'
    data = {"id": data_headers.get('x_yataxi_userid'),
            "orderid": orderid}

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.post(
                url,
                json=data
        ) as response:
            if response.status == 401:
                return False
            response_json = await response.json()
            pprint(response_json)
            return True


@handle_csrf_token
async def canceled_order_yandex(orderid):
    data = {
        "orderid": orderid,
        "format_currency": True,
        "id": data_headers.get('x_yataxi_userid'),
        "break": "user"
    }
    url = 'https://ya-authproxy.taxi.yandex.ru/3.0/taxiontheway'
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.post(
                url,
                json=data
        ) as response:
            if response.status == 401:
                return False
            response_json = await response.json()
            if response_json.get('status') == 'cancelled':
                return response_json


@handle_csrf_token
async def taxi_on_the_way(orderid) -> dict:
    data = {
        "format_currency": True,
        "orderid": orderid,
        "id": data_headers.get('x_yataxi_userid'),
    }
    url = 'https://ya-authproxy.taxi.yandex.ru/3.0/taxiontheway'
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.post(
                url,
                json=data
        ) as response:
            if response.status == 401:
                return False
            response_json: dict = await response.json()
            data = {
                'final_cost': response_json.get('final_cost'),
                'payment': response_json.get('payment'),
                'status': response_json.get('status'),
                'status_updates': response_json.get('status_updates'),
                'driver': response_json.get('driver')
            }
            print('check taxiway', '--'*20)
            pprint(data)
            return data


@handle_csrf_token
async def get_coord(text: str) -> dict:
    url = 'https://ya-authproxy.taxi.yandex.ru/integration/turboapp/v1/suggest'
    data = {
        "part": text,
        "type": "a",
        "id": data_headers.get('x_yataxi_userid'),
        "state": {
            "accuracy": 0,
        },
        "action": "user_input",
        "sticky": False
    }
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.post(
                url,
                json=data
        ) as response:
            if response.status == 401:
                return False
            response_json = await response.json()
            geo = list(map(float, response_json.get('results')[0].get('pos').split(',')))
            return {
                'statuscode': response.status,
                'lon': geo[0],
                'lat': geo[1],
            }


async def get_address_data(value: str,
                           city: str,
                           name_person: str,
                           phone_person: str,
                           by='text'
                           ) -> dict:
    if by == 'text':
        coord_data = await get_coord(city + ' ' + value)
        lon, lat = coord_data.get('lon'), coord_data.get('lat')
    elif by == 'coord':
        lon, lat = value[0], value[1]
    address_loc = [[lon, lat], [lon, lat]]
    offer, price = await get_price_yandex(address_loc, cant_none=True)
    order_id = await get_orderid(offer,
                                 address_loc,
                                 city,
                                 name_person,
                                 phone_person)
    await create_order_yandex(order_id)
    address_data = await canceled_order_yandex(order_id)
    info_address = address_data.get('request').get('route')[0]
    info_address_dict = {
        'area': info_address.get('area'),
        'city': info_address.get('city'),
        'country': info_address.get('country'),
        'full_text': info_address.get('full_text'),
        'short_text': info_address.get('short_text'),
        'street': info_address.get('street'),
        'house': info_address.get('house'),
        'lon': info_address.get('point')[0],
        'lat': info_address.get('point')[1],
    }
    return info_address_dict
