from aiogram import types, Router
from aiogram.filters import Text, and_f
from aiogram.fsm.context import FSMContext

from data_base.data_base import db
from menu.states import MainStates
from keyboards.keyboards import make_recent_address_kb_for_fm, make_kb_for_select_time_sm, \
    make_inline_menu_board_by_2_items
from text.slow_mode_text import make_text_for_create_route_slow_mode

router = Router()

SLOW_MODE_DICT: dict[dict[str: bool | list]] = {}


async def create_slow_mode(cb: types.CallbackQuery, state: FSMContext):
    await state.clear()
    city = db.get_user_value(cb.from_user.id, 'city')
    first_name = db.get_user_value(cb.from_user.id, 'first_name')
    phone = str(db.get_user_value(cb.from_user.id, 'phone'))
    recent_addresses = db.get_recent_addresses(cb.from_user.id)
    addresses_list = []
    addresses_coords = []
    await state.set_state(MainStates.first_address_sm)
    await state.update_data(main_message=cb.message,
                            recent_addresses=recent_addresses,
                            city=city,
                            addresses_list=addresses_list,
                            addresses_coords=addresses_coords,
                            first_name=first_name,
                            phone=phone)

    await cb.message.edit_text(
        make_text_for_create_route_slow_mode(addresses_list, city),
        reply_markup=make_recent_address_kb_for_fm(recent_addresses),
        parse_mode='html'
    )
    await cb.answer()


@router.callback_query(Text(['select_time_sm']))
async def select_time_sm(cb: types.CallbackQuery, state: FSMContext):
    page = 1
    await state.update_data(page=page)
    await state.set_state(MainStates.select_time_sm)
    await cb.message.edit_text(
        'Выбери часовой промежуток, когда мне анализировать и сохранять время',
        reply_markup=make_kb_for_select_time_sm(page=1),
        parse_mode='html'
    )


@router.callback_query(and_f(lambda c: c.data in ('prev_page_for_sm', 'next_page_for_sm'),
                             MainStates.select_time_sm))
async def pagination_time_list_sm(cb: types.CallbackQuery, state: FSMContext):
    PAGES = 4
    user_data = await state.get_data()
    page = user_data.get('page')
    if cb.data == 'next_page_for_sm':
        page = (page + 1) % PAGES
    elif cb.data == 'prev_page_for_sm':
        page = (page - 1) % PAGES
    await cb.message.edit_reply_markup(reply_markup=make_kb_for_select_time_sm(page))
    await state.update_data(page=page)


@router.callback_query(and_f(lambda c: 'button_' in c.data,
                             MainStates.select_time_sm))
async def create_sm_session(cb: types.CallbackQuery, state: FSMContext):
    times = cb.data.replace('button_', '').split('-')
    time_start, time_end = times
    user_data = await state.get_data()
    addresses_list = user_data.get('addresses_list')
    addresses_list_for_db = addresses_list + [None] * (4 - len(addresses_list))
    city = user_data.get('city')

    # создаём сессия slow mode в базе
    db.insert_row('session_slow_mode', tuple([cb.from_user.id] + times + addresses_list_for_db))
    SLOW_MODE_DICT[cb.from_user.id] = {
        'best_offer': None,
        'best_price': None,
        'best_price_will_be_active': None,
        'orderid': None,
        'session_id': db.get_last_session_id(cb.from_user.id,
                                             table='session_slow_mode'),
        'addresses_coords': user_data.get('addresses_coords'),
        'msg_session': cb.message,
        'order_successfully_created': None
    }

    await cb.message.edit_text(
        make_text_for_create_route_slow_mode(addresses_list,
                                             city,
                                             time_start,
                                             time_end),
        reply_markup=make_inline_menu_board_by_2_items({
                      'back_to_main_menu': '⬅ Назад в меню'
                                      }),
        parse_mode='html'
    )

    await state.set_state(MainStates.main_menu)
    await cb.answer()