import asyncio
from collections import OrderedDict
from pprint import pprint
import re
# -------------------------------------------
from aiogram import types, Router
from aiogram.filters import Text
from aiogram.fsm.context import FSMContext
# -------------------------------------------
from handlers.states import MainStates
from keyboards.keyboards import make_address_keyboard_menu, make_fast_mode_running_board, \
    make_inline_menu_board_by_2_items
from text.fast_mode_text import TextFastMode, create_price_time_string, make_text_for_running_fast_mode
from parcsing.parc import get_price, open_browser, check_price_repeat, create_order
from data_base.data_base import db

router = Router()


CITY = 'Кемерово'

ADDRESSES_LIST = {
                  '1': 'Новорогожская улица, 3',
                  '2': 'проспект 60-летия Октября, 23к2',
                  '3': '8 марта 1',
                  }

LAST_TRIPS_LIST = {
    '1': ['Дружбы 31а -> Советский проспект 2/6', [1, 2]],
    '2': ['Дружбы 31а -> Советский проспект 2/6', [1, 2]],
}

FAST_MODE_DICT: dict[dict[str: bool | list]] = {}


def select_only_addresses(data: dict, with_id: bool = False) -> list:
    only_addresses = []
    for key, value in data.items():
        if key in ('first_address', 'second_address', 'third_address', 'fourth_address'):
            only_addresses.append(value)
    if not with_id:
        return only_addresses
    else:
        addresses_ids = []
        for name in only_addresses:
            for k, v in ADDRESSES_LIST.items():
                if v == name:
                    addresses_ids.append(v)
        return addresses_ids


async def create_new_trip(cb: types.CallbackQuery, state: FSMContext):
    await cb.message.edit_text(
        TextFastMode.NEED_FIRST_ADDRESS.format(CITY),
        reply_markup=make_address_keyboard_menu(ADDRESSES_LIST),
        parse_mode='html'
    )

    await state.clear()
    city = db.get_user_value(cb.from_user.id, 'city')
    await state.set_state(MainStates.first_address)
    await state.update_data(main_message=cb.message,
                            city=city)
    await cb.answer()


@router.callback_query(Text(['run_fast_mode']))
async def run_fast_mode(cb: types.CallbackQuery, state: FSMContext):
    await state.set_state(MainStates.fast_mode)
    user_data = await state.get_data()
    addresses_id = select_only_addresses(user_data, with_id=True)
    addresses_name = select_only_addresses(user_data)
    new_message = cb.message.text + '\n\nЗапустил поиск цен'
    new_message = new_message.replace('Маршрут может содержать до 4 адресов. Нажмите кнопку "Искать"\n\n', '')
    new_message = new_message.replace('Можете добавить ещё адреса в поездку или нажмите "Искать цены"\n\n', '')
    new_message = new_message.replace('Запустил поиск цен', '')
    await cb.message.edit_text(
        new_message,
        reply_markup=make_fast_mode_running_board()
    )
    cb.answer()

    driver = await open_browser()

    FAST_MODE_DICT[cb.from_user.id] = {
        'message_id_start': cb.message.message_id,
        'driver': driver,
        'is_fast_mode': True,
        'iter': 1,
        'city': user_data.get('city'),
        'addresses_list': addresses_name,
        'addresses_list_yandex': [],
        'addresses_list_yandex_last': [],
        'price_history': [],
        'price_created_history': [],
        'best_price': None,
        'best_price_will_be_active': None,
        'best_tab_id': None,
        'processing_tab': OrderedDict()
    }

    while FAST_MODE_DICT.get(cb.from_user.id).get('is_fast_mode'):
        data = await get_price(FAST_MODE_DICT[cb.from_user.id])

        if data['addresses_list_yandex_last'] != data['addresses_list_yandex']:
            data = await get_price(FAST_MODE_DICT[cb.from_user.id])

        FAST_MODE_DICT[cb.from_user.id] = data

        pprint(FAST_MODE_DICT[cb.from_user.id])

        price_list = FAST_MODE_DICT.get(cb.from_user.id).get('price_history')
        time_list = FAST_MODE_DICT.get(cb.from_user.id).get('price_created_history')

        price_time_string = create_price_time_string(price_list, time_list)

        if not FAST_MODE_DICT.get(cb.from_user.id).get('is_fast_mode'):
            break

        string_best_price = f"\n\nЛучшая цена на момент обновления: {FAST_MODE_DICT[cb.from_user.id].get('best_price')} " \
                            f"активна ещё {FAST_MODE_DICT[cb.from_user.id].get('best_price_will_be_active')} минут"

        new_message = make_text_for_running_fast_mode(FAST_MODE_DICT[cb.from_user.id])

        await cb.message.edit_text(
            new_message + f'\n\n{price_time_string}' + string_best_price,
            reply_markup=make_fast_mode_running_board(FAST_MODE_DICT[cb.from_user.id].get('best_price'))
        )

        try:
            if price_list[-2] - price_list[-1] > 30:
                await cb.message.answer('Цена снизалась!')
            elif price_list[-1] - price_list[-2] > 30:
                await cb.message.answer('Цена выросла!')
        except:
            pass

        await asyncio.sleep(60)


@router.callback_query(Text(['create_order_taxi']))
async def create_order_taxi(cb: types.CallbackQuery, state: FSMContext):
    await state.set_state(MainStates.main_menu)
    FAST_MODE_DICT[cb.from_user.id]['is_fast_mode'] = False
    driver = FAST_MODE_DICT.get(cb.from_user.id).get('driver')
    best_price = FAST_MODE_DICT.get(cb.from_user.id).get('best_price')
    best_tab_id = FAST_MODE_DICT.get(cb.from_user.id).get('best_tab_id')
    await cb.message.edit_reply_markup(reply_markup=None)
    repeat_check_price_result = await check_price_repeat(driver, best_tab_id)
    print(repeat_check_price_result, best_price)
    if repeat_check_price_result == best_price:
        await create_order(driver)
        await state.set_state(MainStates.created_order)

        msg = await cb.message.answer(f'Заказал такси за {repeat_check_price_result} руб.\nПодробности в приложение яндекс такси'
                                f'\nОтменить заказ можно в течение 30 секунд',
                                reply_markup=make_inline_menu_board_by_2_items({
                                    'cancellation_order': '❌ Отменить вызов такси'
                                }))
        await cb.answer()
        FAST_MODE_DICT[cb.from_user.id]['sec_for_cancel_order'] = 30
        while FAST_MODE_DICT[cb.from_user.id]['sec_for_cancel_order'] > 0:
            await msg.edit_reply_markup(reply_markup=make_inline_menu_board_by_2_items({
                                    'cancellation_order': f"❌ Отменить вызов такси {FAST_MODE_DICT[cb.from_user.id]['sec_for_cancel_order']}"
                                }))
            FAST_MODE_DICT[cb.from_user.id]['sec_for_cancel_order'] -= 1
            await asyncio.sleep(1)

        await msg.edit_reply_markup(reply_markup=None)
    else:
        await cb.message.answer(f'Цена изменилась((( Мне дика жаль(((')
        await cb.answer()


