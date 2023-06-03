import asyncio
from pprint import pprint

# -------------------------------------------
from aiogram import types, Router
from aiogram.filters import Text
from aiogram.fsm.context import FSMContext

from data_base.data_base import db
# -------------------------------------------
from menu.states import MainStates
from keyboards.keyboards import make_recent_address_kb_for_fm, make_fast_mode_running_board, \
    make_inline_menu_board_by_2_items
from parcsing.api_yandex import get_price_yandex, get_orderid, create_order_yandex, taxi_on_the_way
from text.fast_mode_text import create_price_time_string, make_text_for_create_route, make_text_for_running_fast_mode

router = Router()

FAST_MODE_DICT: dict[dict[str: bool | list]] = {}


async def create_new_trip(cb: types.CallbackQuery, state: FSMContext):
    await state.clear()
    city = db.get_user_value(cb.from_user.id, 'city')
    first_name = db.get_user_value(cb.from_user.id, 'first_name')
    phone = str(db.get_user_value(cb.from_user.id, 'phone'))
    recent_addresses = db.get_recent_addresses(cb.from_user.id)
    addresses_list = []
    addresses_coords = []
    await state.set_state(MainStates.first_address_fm)
    await state.update_data(main_message=cb.message,
                            recent_addresses=recent_addresses,
                            city=city,
                            addresses_list=addresses_list,
                            addresses_coords=addresses_coords,
                            first_name=first_name,
                            phone=phone)

    await cb.message.edit_text(
        make_text_for_create_route(addresses_list, city),
        reply_markup=make_recent_address_kb_for_fm(recent_addresses),
        parse_mode='html'
    )
    await cb.answer()


@router.callback_query(Text(['run_fast_mode']))
async def run_fast_mode(cb: types.CallbackQuery, state: FSMContext):
    await state.set_state(MainStates.fast_mode)
    user_data = await state.get_data()
    remove_msg_alert_price_list = []
    await state.update_data(remove_msg_alert_price_list=remove_msg_alert_price_list)
    addresses_list = user_data.get('addresses_list')
    addresses_list_for_db = addresses_list + [None] * (4 - len(addresses_list))
    new_message = cb.message.text
    new_message = new_message.replace("Если вам нужно указать еще какие-то адреса в маршруте, то введите их сейчас. "\
                                        "Если же вы готовы продолжить, то нажмите кнопку 'Искать цены', и я начну поиск цен.", '')
    new_message = new_message.replace('Маршрут может содержать до 4 адресов. Теперь нажми кнопку "Искать цены"\n', '')
    await cb.message.edit_text(
        new_message,
        reply_markup=make_fast_mode_running_board()
    )
    cb.answer()

    # Создаём сессию в базе
    db.insert_row('session_fast_mode', tuple([cb.from_user.id] + addresses_list_for_db))

    FAST_MODE_DICT[cb.from_user.id] = {
        'iter': 1,
        'is_fast_mode': True,
        cb.message.message_id: True,
        'message_id_start': cb.message.message_id,
        'city': user_data.get('city'),
        'first_name': user_data.get('first_name'),
        'phone': user_data.get('phone'),
        'best_offer': None,
        'best_price': None,
        'best_price_will_be_active': None,
        'orderid': None,
        'session_id': db.get_last_session_id(cb.from_user.id),
        'addresses_coords': user_data.get('addresses_coords'),
        'price_alert_threshold': db.get_setting_value(cb.from_user.id, 'price_alert_threshold'),
        'msg_session': cb.message,
        'order_successfully_created': None
    }

    while FAST_MODE_DICT.get(cb.from_user.id) and FAST_MODE_DICT.get(cb.from_user.id).get(cb.message.message_id):

        offer, price = await get_price_yandex(FAST_MODE_DICT[cb.from_user.id].get('addresses_coords'))
        db.insert_row('offers_taxi',
                      (cb.from_user.id,
                       FAST_MODE_DICT[cb.from_user.id].get('session_id'),
                       offer,
                       price)
                      )

        FAST_MODE_DICT[cb.from_user.id]['best_price'], FAST_MODE_DICT[cb.from_user.id]['best_offer'], \
            FAST_MODE_DICT[cb.from_user.id]['best_price_will_be_active'] = db.get_best_price(
            FAST_MODE_DICT[cb.from_user.id].get('session_id'))

        price_list, time_list = db.get_price_history(chat_id=cb.from_user.id,
                                                     session_id=FAST_MODE_DICT[cb.from_user.id].get('session_id'))

        price_time_string = create_price_time_string(price_list, time_list)

        if not FAST_MODE_DICT.get(cb.from_user.id) and FAST_MODE_DICT.get(cb.from_user.id).get(cb.message.message_id):
            break

        string_best_price = f"\nЛучшая цена на момент обновления: {FAST_MODE_DICT[cb.from_user.id].get('best_price')}₽ " \
                            f"активна ещё {FAST_MODE_DICT[cb.from_user.id].get('best_price_will_be_active')} минут"

        await cb.message.edit_text(
            make_text_for_running_fast_mode(addresses_list, price_time_string, string_best_price),
            reply_markup=make_fast_mode_running_board(FAST_MODE_DICT[cb.from_user.id].get('best_price'),
                                                      price_list[-1],
                                                      FAST_MODE_DICT[cb.from_user.id].get('addresses_coords')
                                                      ),
            parse_mode='html'
        )

        try:
            if price_list[-2] - price_list[-1] > FAST_MODE_DICT[cb.from_user.id]['price_alert_threshold']:
                remove_msg_alert_price = await cb.message.answer('Цена снизалась!')
            elif price_list[-1] - price_list[-2] > FAST_MODE_DICT[cb.from_user.id]['price_alert_threshold']:
                remove_msg_alert_price = await cb.message.answer(f"Цена выросла! \n"
                                                                 f"Но я сохранил для вас цену {FAST_MODE_DICT[cb.from_user.id].get('best_price')}₽")
            user_data = await state.get_data()
            user_data['remove_msg_alert_price_list'].append(remove_msg_alert_price)
            await state.update_data(remove_msg_alert_price_list=user_data['remove_msg_alert_price_list'])
        except:
            pass

        await asyncio.sleep(60)


@router.callback_query(Text(['create_order_taxi']))
async def create_order_taxi(cb: types.CallbackQuery, state: FSMContext):
    # вот это хуёва, нельзя довать создавать новый заказ, пока не завершён или не отменён текущий
    await state.set_state(MainStates.main_menu)

    # данные
    FAST_MODE_DICT[cb.from_user.id][cb.message.message_id] = False
    best_price = FAST_MODE_DICT.get(cb.from_user.id).get('best_price')
    best_offer = FAST_MODE_DICT.get(cb.from_user.id).get('best_offer')
    addresses_coords = FAST_MODE_DICT.get(cb.from_user.id).get('addresses_coords')
    city = FAST_MODE_DICT.get(cb.from_user.id).get('city')
    name_person = FAST_MODE_DICT.get(cb.from_user.id).get('first_name')
    phone_person = FAST_MODE_DICT.get(cb.from_user.id).get('phone')
    payment_type = 'card' if cb.from_user.id == 1069177650 else 'cash'
    payment_type = 'cash'

    # удаляем клаву. чтобы не кликал больше
    await cb.message.edit_reply_markup(reply_markup=None)

    # получаем ордерID который потом будем комитить для создания заказа
    orderid = await get_orderid(best_offer,
                                addresses_coords,
                                city,
                                name_person,
                                phone_person,
                                payment_type)
    FAST_MODE_DICT[cb.from_user.id]['orderid'] = orderid

    # коммитим заказ
    await create_order_yandex(orderid)

    # проверяем статус заказа, если упал в нужные статусы, то ставим флаг успеха
    for i in range(5):
        await asyncio.sleep(.5)
        data_order: dict = await taxi_on_the_way(FAST_MODE_DICT[cb.from_user.id]['orderid'])
        if data_order.get('status') in ('search', 'driving'):
            FAST_MODE_DICT[cb.from_user.id]['order_successfully_created'] = True
            break

    # если заказ не создан, то пишем
    if not FAST_MODE_DICT[cb.from_user.id]['order_successfully_created']:
        await cb.message.answer('Ошибка при создание заказа. Попробуйте ещё раз')

    # успешный заказ
    else:
        # логируем сессию
        db.set_result_session_fast_mode(FAST_MODE_DICT[cb.from_user.id]['session_id'],
                                        'created_order_taxi',
                                        FAST_MODE_DICT[cb.from_user.id]['best_offer'])

        await state.set_state(MainStates.created_order)
        # отвечаем и даём клаву для отмены
        msg = await cb.message.answer(f'Заказал такси за {best_price} руб.\nПодробности в приложение яндекс такси'
                                      f'\nОтменить заказ можно в течение 30 секунд',
                                      reply_markup=make_inline_menu_board_by_2_items({
                                          'cancellation_order': '❌ Отменить вызов такси'
                                      }))
        await cb.answer()

        # таймер для клавы на отмену заказа
        FAST_MODE_DICT[cb.from_user.id]['sec_for_cancel_order'] = 30
        while FAST_MODE_DICT.get(cb.from_user.id) and FAST_MODE_DICT[cb.from_user.id]['sec_for_cancel_order'] > 0:
            await msg.edit_reply_markup(reply_markup=make_inline_menu_board_by_2_items({
                'cancellation_order': f"❌ Отменить вызов такси {FAST_MODE_DICT[cb.from_user.id]['sec_for_cancel_order']}"
            }))
            FAST_MODE_DICT[cb.from_user.id]['sec_for_cancel_order'] -= 1
            await taxi_on_the_way(FAST_MODE_DICT[cb.from_user.id]['orderid'])
            await asyncio.sleep(1)

        try:
            await msg.edit_reply_markup(reply_markup=None)
        except Exception:
            pass
