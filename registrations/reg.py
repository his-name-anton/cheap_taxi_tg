from aiogram import Router, types, F
from aiogram.filters import Command, Text, and_f
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile, ReplyKeyboardRemove

from handlers.main_menu import main_menu
from data_base.data_base import db
from handlers.states import MainStates
from geo_data.geo_dadata import get_info_address, get_address_by_coord
from keyboards.keyboards import make_inline_menu_board_by_2_items, share_phone_keyboard
from text.registrations_text import TextRegistrations

router = Router()


async def registration(msg: types.Message, state: FSMContext):
    await state.set_state(MainStates.registrations_city)
    main_message = await msg.answer(
        TextRegistrations.REGISTRATIONS.format(msg.from_user.first_name.capitalize())
    )
    await state.update_data(main_message=main_message)


@router.message(MainStates.registrations_city)
async def check_city(msg: types.Message, state: FSMContext):
    """Функция находит город в дадате по координатам или по тексту"""
    if msg.content_type == 'location':
        lat, lon = msg.location.latitude, msg.location.longitude
        result = get_address_by_coord(lat, lon)
        city = result.get('city')

    if msg.content_type == 'venue':
        lat, lon = msg.venue.location.latitude, msg.venue.location.longitude
        result = get_address_by_coord(lat, lon)
        city = result.get('city')

    if msg.content_type == 'text':
        all_data = get_info_address(msg.text)
        city = all_data.get('full_address')

    user_data = await state.get_data()
    main_message: types.Message = user_data.get('main_message')

    if city:
        await state.update_data(city_with_type=city)
        await main_message.edit_text(f'Я определ город как: {city}\n\n'
                                     f'Всё верно?',
                                     reply_markup=make_inline_menu_board_by_2_items({
                                         'incorrect_city': '👎 Нет',
                                         'correct_city': '👍 Да',
                                     }))
    else:
        await main_message.edit_text(TextRegistrations.CITY_NOT_RECOGNIZED,
                                     reply_markup=None)
    await msg.delete()


@router.callback_query(Text(['incorrect_city']))
async def incorrect_city(cb: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    main_message: types.Message = user_data.get('main_message')
    await main_message.edit_text(TextRegistrations.INCORRECT_CITY)


@router.callback_query(Text(['correct_city']))
async def correct_city(cb: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    main_message: types.Message = user_data.get('main_message')
    city_with_type = user_data.get('city_with_type')
    db.update_value(f"UPDATE users SET city = '{city_with_type}' WHERE chat_id = {cb.from_user.id}")
    await main_message.edit_text(f'Отлично {cb.from_user.first_name.capitalize()}!\n'
                                 f'Сохранил город: {city_with_type}\n\n',
                                 reply_markup=None)
    await wait_phone(cb.message, state)


async def wait_phone(msg: types.Message, state: FSMContext):
    gif = FSInputFile('img/how_check_yandex_phone.gif')
    await state.set_state(MainStates.registrations_phone)
    await msg.answer_animation(gif,
                               caption=TextRegistrations.WAIT_PHONE,
                               reply_markup=share_phone_keyboard)


@router.message(and_f(and_f(F.content_type.in_({'contact'}), MainStates.registrations_phone)))
async def get_phone(msg: types.Message, state: FSMContext):
    phone_number = msg.contact.phone_number
    phone_number = int(phone_number.replace('+', ''))
    db.update_value(f"UPDATE users SET phone = {phone_number} WHERE chat_id = {msg.from_user.id}")

    await msg.answer(TextRegistrations.GET_PHONE,
                     reply_markup=ReplyKeyboardRemove())
    await state.set_state(MainStates.main_menu)
    await main_menu(msg)


@router.message(Command(commands=['start']))
async def cmd_start(msg: types.Message, state: FSMContext):
    if db.get_user_value(msg.chat.id, 'phone'):
        await main_menu(msg)
    elif db.get_user_value(msg.chat.id, 'city'):
        await wait_phone(msg, state)
    elif db.get_user(msg.chat.id):
        await registration(msg, state)
    else:
        db.insert_row('users', (msg.from_user.id,
                                msg.from_user.first_name,
                                msg.from_user.last_name,
                                msg.from_user.username))
        await state.set_state(MainStates.start_reg)
        await registration(msg, state)
