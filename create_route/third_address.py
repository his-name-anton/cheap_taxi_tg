from aiogram import types, F, Router
from aiogram.filters import and_f
from aiogram.fsm.context import FSMContext

from geo_data.geo_dadata import get_address_by_coord
from create_route.create_route import CITY, ADDRESSES_LIST, select_only_addresses
from handlers.states import MainStates
from keyboards.keyboards import make_address_keyboard_menu, FAVORITE_ADDRESS
from text.fast_mode_text import TextFastMode

router = Router()


# THIRD ADDRESS
@router.message(and_f(F.content_type.in_({'location', 'venue'}), MainStates.third_address))
async def third_address_location(msg: types.Message, state: FSMContext):
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
        third_address = f"{result.get('street_with_type')} {result.get('house')} ({title_venue})"
    else:
        third_address = f"{result.get('street_with_type')} {result.get('house')}"

    await state.update_data(third_address=third_address)
    first_address = user_data.get('first_address')
    second_address = user_data.get('second_address')
    await main_message.edit_text(
        TextFastMode.WAIT_FOURTH_ADDRESS.format(CITY, first_address, second_address, third_address),
        reply_markup=make_address_keyboard_menu(ADDRESSES_LIST,
                                                select_only_addresses(user_data),
                                                can_order=True),
        parse_mode='html'
    )
    state_now = await state.get_state()
    index_new_state = MainStates.state_list.index(state_now) + 1
    await state.set_state(MainStates.state_list[index_new_state])
    await state.update_data(last_message=main_message.text)
    await msg.delete()


@router.callback_query(MainStates.third_address)
async def third_address(cb: types.CallbackQuery, state: FSMContext):
    third_address = ADDRESSES_LIST.get(cb.data)
    if cb.data in ('-1', '-2'):
        third_address = FAVORITE_ADDRESS.get(cb.data)[1]
    await state.update_data(third_address=third_address)
    user_data = await state.get_data()
    first_address = user_data.get('first_address')
    second_address = user_data.get('second_address')
    await cb.message.edit_text(
        TextFastMode.WAIT_FOURTH_ADDRESS.format(CITY, first_address, second_address, third_address),
        reply_markup=make_address_keyboard_menu(ADDRESSES_LIST,
                                                select_only_addresses(user_data),
                                                can_order=True),
        parse_mode='html'
    )
    state_now = await state.get_state()
    index_new_state = MainStates.state_list.index(state_now) + 1
    await state.set_state(MainStates.state_list[index_new_state])
    await state.update_data(last_message=cb.message.text)
    await cb.answer()