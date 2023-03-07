from pprint import pprint

from aiogram import types, F, Router
from aiogram.filters import and_f, Text
from aiogram.fsm.context import FSMContext

from geo_data.geo_dadata import get_address_by_coord, get_info_address
from create_route.create_route import CITY, ADDRESSES_LIST, select_only_addresses
from handlers.states import MainStates
from keyboards.keyboards import make_address_keyboard_menu, FAVORITE_ADDRESS, make_inline_menu_board_by_2_items
from text.fast_mode_text import TextFastMode
from data_base.data_base import db

router = Router()


# FIRST ADDRESS
@router.message(and_f(F.content_type.in_({'location', 'venue'}), MainStates.first_address))
async def first_address_location(msg: types.Message, state: FSMContext):
    if msg.content_type == 'venue':
        address = msg.venue.address
        title_venue = msg.venue.title
        first_address = f"{address} ({title_venue})"
    else:
        lon = msg.location.longitude
        lat = msg.location.latitude
        result = get_address_by_coord(lat, lon)
        first_address = f"{result.get('street_with_type')} {result.get('house')}"

    user_data = await state.get_data()
    main_message: types.Message = user_data.get('main_message')
    await state.update_data(first_address=first_address)
    await main_message.edit_text(
        TextFastMode.NEED_SECOND_ADDRESS.format(CITY, first_address),
        reply_markup=make_address_keyboard_menu(ADDRESSES_LIST, select_only_addresses(user_data)),
        parse_mode='html'
    )
    state_now = await state.get_state()
    index_new_state = MainStates.state_list.index(state_now) + 1
    await state.set_state(MainStates.state_list[index_new_state])
    await state.update_data(last_message=main_message.text)
    await msg.delete()


@router.message(and_f(F.content_type.in_({'text'}), MainStates.first_address))
async def first_address_text(msg: types.Message, state: FSMContext):
    user_data = await state.get_data()
    city = user_data.get('city')
    add_data = get_info_address(city + ' ' + msg.text)
    await state.update_data(add_data=add_data)
    await msg.delete()
    await check_text_address(msg, state)


@router.callback_query(and_f(Text(['correct']), MainStates.first_address))
async def check_text_address(cb: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    main_message: types.Message = user_data.get('main_message')
    city = user_data.get('add_data').get('city')
    first_address = user_data.get('street_house')
    address_data = user_data.get('add_data')
    db.save_address(cb.from_user.id, address_data)
    await state.update_data(first_address=first_address)
    await main_message.edit_text(TextFastMode.NEED_SECOND_ADDRESS.format(city, first_address),
                                 reply_markup=make_address_keyboard_menu(ADDRESSES_LIST, select_only_addresses(user_data)),
                                 parse_mode='html'
                                 )
    state_now = await state.get_state()
    index_new_state = MainStates.state_list.index(state_now) + 1
    await state.set_state(MainStates.state_list[index_new_state])
    await cb.answer()


@router.callback_query(and_f(Text(['incorrect']), MainStates.first_address))
async def check_text_address(cb: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    main_message: types.Message = user_data.get('main_message')
    city = user_data.get('add_data').get('city')
    await main_message.edit_text(TextFastMode.NEED_FIRST_ADDRESS.format(city) + '\n\nДавайте тогда попробуем ещё раз',
                                 reply_markup=make_address_keyboard_menu(ADDRESSES_LIST, select_only_addresses(user_data)),
                                 parse_mode='html'
                                 )
    await cb.answer()


async def check_text_address(msg: types.Message, state: FSMContext):
    user_data = await state.get_data()
    main_message: types.Message = user_data.get('main_message')
    full_address = user_data.get('add_data').get('full_address')
    city = user_data.get('add_data').get('city')
    street_house = user_data.get('add_data').get('street') + ' ' + user_data.get('add_data').get('house')
    await state.update_data(full_address=full_address,
                            street_house=street_house)
    await main_message.edit_text(TextFastMode.NEED_FIRST_ADDRESS.format(city) +
                                 f'\n\nОпределил адрес как: {full_address}\nВерно?',
                                 reply_markup=make_inline_menu_board_by_2_items({
                                     'incorrect': 'Нет',
                                     'correct': 'Да'
                                 }),
                                 parse_mode='html')


@router.callback_query(MainStates.first_address)
async def first_address_cb(cb: types.CallbackQuery, state: FSMContext):
    first_address = ADDRESSES_LIST.get(cb.data)
    if cb.data in ('-1', '-2'):
        first_address = FAVORITE_ADDRESS.get(cb.data)[1]
    await state.update_data(first_address=first_address)
    user_data = await state.get_data()
    await cb.message.edit_text(
        TextFastMode.NEED_SECOND_ADDRESS.format(CITY, first_address),
        reply_markup=make_address_keyboard_menu(ADDRESSES_LIST, select_only_addresses(user_data)),
        parse_mode='html'
    )
    state_now = await state.get_state()
    index_new_state = MainStates.state_list.index(state_now) + 1
    await state.set_state(MainStates.state_list[index_new_state])
    await state.update_data(last_message=cb.message.text)
    await cb.answer()
