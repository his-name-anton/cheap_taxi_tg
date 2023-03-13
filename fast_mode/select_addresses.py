from aiogram import types, F, Router
from aiogram.filters import and_f, Text, or_f
from aiogram.fsm.context import FSMContext

from data_base.data_base import db
from menu.states import MainStates
from keyboards.keyboards import make_recent_address_kb_for_fm, make_inline_menu_board_by_2_items
from parcsing.api_yandex import get_address_data
from text.fast_mode_text import make_text_for_create_route

router = Router()


@router.message(and_f(F.content_type.in_({'location', 'venue', 'text'})),
                or_f(
                    MainStates.first_address_fm,
                    MainStates.second_address_fm,
                    MainStates.third_address_fm,
                    MainStates.fourth_address_fm
                ))
async def get_new_address(msg: types.Message, state: FSMContext):
    user_data = await state.get_data()
    main_message: types.Message = user_data.get('main_message')
    city = user_data.get('city')
    phone = user_data.get('phone')
    first_name = user_data.get('first_name')
    addresses_list = user_data.get('addresses_list')
    wait_message = await msg.answer('Секундочку, ищу адрес 📍')

    if msg.content_type == 'venue':
        lon = msg.venue.location.longitude
        lat = msg.venue.location.latitude
        address_info_yandex = await get_address_data([lon, lat],
                                                     city,
                                                     first_name,
                                                     phone,
                                                     by='coord'
                                                     )
    elif msg.content_type == 'location':
        lon = msg.location.longitude
        lat = msg.location.latitude
        address_info_yandex = await get_address_data([lon, lat],
                                                     city,
                                                     first_name,
                                                     phone,
                                                     by='coord'
                                                     )
    elif msg.content_type == 'text':
        address_info_yandex = await get_address_data(msg.text,
                                                     city,
                                                     first_name,
                                                     phone)
        lat, lon = address_info_yandex.get('lat'), address_info_yandex.get('lon')
        loc_message = await msg.answer_location(lat, lon)
        await state.update_data(loc_message=loc_message)

    await wait_message.delete()
    text_address = address_info_yandex.get('full_text')

    await state.update_data(address_wait_approved=address_info_yandex,
                            addresses_list=addresses_list)

    await main_message.edit_text(
        make_text_for_create_route(addresses_list, city) + f"\n\nОпределил адрес как: <b>{text_address}</b>\nВерно?",
        reply_markup=make_inline_menu_board_by_2_items({
            'incorrect_new_address': '👎 Нет',
            'correct_new_address': '👍 Да'
        }),
        parse_mode='html'
    )

    await state.update_data(last_message=main_message.text)
    await msg.delete()


@router.callback_query(and_f(or_f(Text(['correct_new_address']),
                                  lambda c: 'recent_address' in c.data),
                             or_f(MainStates.first_address_fm,
                                  MainStates.second_address_fm,
                                  MainStates.third_address_fm,
                                  MainStates.fourth_address_fm)
                             )
                       )
async def correct_new_address(cb: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    addresses_list: list = user_data.get('addresses_list')
    addresses_coords: list = user_data.get('addresses_coords')
    address_wait_approved: dict = user_data.get('address_wait_approved')
    recent_addresses = user_data.get('recent_addresses')
    main_message: types.Message = user_data.get('main_message')
    city = user_data.get('city')

    if cb.data == 'correct_new_address':
        addresses_list.append(address_wait_approved['short_text'])
        addresses_coords.append([address_wait_approved.get('lon'), address_wait_approved.get('lat')])
        db.save_address(cb.from_user.id, address_wait_approved)

    elif 'recent_address' in cb.data:
        recent_addresses = user_data.get('recent_addresses')
        address_values = recent_addresses.get(cb.data)
        addresses_coords.append(address_values[0])
        addresses_list.append(address_values[1])

    can_order = True if len(addresses_list) > 1 else False
    await main_message.edit_text(
        make_text_for_create_route(addresses_list, city),
        reply_markup=make_recent_address_kb_for_fm(recent_addresses,
                                                   can_order=can_order),
        parse_mode='html'
    )

    try:
        loc_message: types.Message = user_data.get('loc_message')
        await loc_message.delete()
    except Exception:
        pass

    state_now = await state.get_state()
    index_new_state = MainStates.state_fm_select_address.index(state_now) + 1
    try:
        await state.set_state(MainStates.state_fm_select_address[index_new_state])
    except:
        pass
    await cb.answer()


@router.callback_query(Text(['incorrect_new_address']))
async def incorrect_new_address(cb: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    main_message = user_data.get('main_message')
    addresses_list = user_data.get('addresses_list')
    recent_addresses = user_data.get('recent_addresses')
    city = user_data.get('city')

    try:
        loc_message: types.Message = user_data.get('loc_message')
        await loc_message.delete()
    except Exception:
        pass

    can_order = True if len(addresses_list) > 1 else False
    await main_message.edit_text(
        make_text_for_create_route(addresses_list, city),
        reply_markup=make_recent_address_kb_for_fm(recent_addresses,
                                                   can_order=can_order),
        parse_mode='html'
    )
    await cb.answer()
