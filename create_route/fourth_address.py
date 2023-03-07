from aiogram import types, F, Router
from aiogram.filters import and_f
from aiogram.fsm.context import FSMContext

from geo_data.geo_dadata import get_address_by_coord
from create_route.create_route import CITY, ADDRESSES_LIST
from handlers.states import MainStates
from keyboards.keyboards import FAVORITE_ADDRESS, make_inline_menu_board_by_2_items
from text.fast_mode_text import TextFastMode


router = Router()


# FOURTH ADDRESS
@router.message(and_f(F.content_type.in_({'location', 'venue'}), MainStates.fourth_address))
async def fourth_address_location(msg: types.Message, state: FSMContext):
    if msg.content_type == 'venue':
        lat = msg.venue.location.latitude
        lon = msg.venue.location.longitude
        title_venue = msg.venue.title
    else:
        lon = msg.location.longitude
        lat = msg.location.latitude

    user_data = await state.get_data()
    main_message: types.Message = user_data.get('main_message')
    result = get_address_by_coord(lat, lon)

    if msg.content_type == 'venue':
        fourth_address = f"{result.get('street_with_type')} {result.get('house')} ({title_venue})"
    else:
        fourth_address = f"{result.get('street_with_type')} {result.get('house')}"

    await state.update_data(fourth_address=fourth_address)
    first_address = user_data.get('first_address')
    second_address = user_data.get('second_address')
    third_address = user_data.get('third_address')
    await main_message.edit_text(
        TextFastMode.SELECT_ALL_ADDRESS.format(CITY, first_address, second_address, third_address, fourth_address),
        reply_markup=make_inline_menu_board_by_2_items({
            'cancel_create_trip': '⏪ В меню',
            'run_fast_mode': 'Искать цену ⏩'
        }),
        parse_mode='html'
    )
    await state.update_data(last_message=main_message.text)
    await msg.delete()


@router.callback_query(MainStates.fourth_address)
async def fourth_address(cb: types.CallbackQuery, state: FSMContext):
    fourth_address = ADDRESSES_LIST.get(cb.data)
    if cb.data in ('-1', '-2'):
        fourth_address = FAVORITE_ADDRESS.get(cb.data)[1]
    await state.update_data(fourth_address=fourth_address)
    user_data = await state.get_data()
    first_address = user_data.get('first_address')
    second_address = user_data.get('second_address')
    third_address = user_data.get('third_address')
    await cb.message.edit_text(
        TextFastMode.SELECT_ALL_ADDRESS.format(CITY, first_address, second_address, third_address, fourth_address),
        reply_markup=make_inline_menu_board_by_2_items({
            'cancel_create_trip': '⏪ В меню',
            'run_fast_mode': 'Искать цену ⏩'
        }),
        parse_mode='html'
    )
    await state.update_data(last_message=cb.message.text)
    await cb.answer()