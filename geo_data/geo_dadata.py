import os
from dotenv import load_dotenv, find_dotenv
from dadata import Dadata

load_dotenv(find_dotenv())

dadata = Dadata(os.getenv('TOKEN_DADATA'), os.getenv('SECRET_DADATA'))


def get_address_by_coord(lat: float, lon: float) -> dict[str: str]:
    all_data = dadata.geolocate(name="address", lat=lat, lon=lon)
    first_el = all_data[0]
    res_d = {
        'value': first_el.get('value'),
        'region': first_el.get('data').get('region'),
        'city': first_el.get('data').get('city'),
        'street_with_type': first_el.get('data').get('street_with_type'),
        'house': first_el.get('data').get('house'),
    }
    return res_d


def get_info_address(address):
    add_data = dadata.clean("address", address)
    result = {
        'region': add_data.get('region_with_type'),
        'city': add_data.get('city_with_type'),
        'street': add_data.get('street_with_type'),
        'house': add_data.get('house'),
        'full_address': add_data.get('result'),
        'timezone': add_data.get('timezone'),
        'geo_lat': add_data.get('geo_lat'),
        'geo_lon': add_data.get('geo_lon'),
        'postal_code': add_data.get('postal_code'),
    }
    return result



