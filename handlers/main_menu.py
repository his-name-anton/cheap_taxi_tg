import logging
# -------------------------------------------
from aiogram import types, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
# -------------------------------------------
from create_route.create_route import create_new_trip
from handlers.states import MainStates
from keyboards.keyboards import make_inline_menu_board
from keyboards.buttons import KeyboardButtons


logging.basicConfig(level=logging.INFO)
router = Router()


# main menu
async def main_menu(msg: Message):
    await msg.answer('Меню', reply_markup=make_inline_menu_board(KeyboardButtons.MAIN_MENU))


async def back_to_main_menu(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_text('Меню', reply_markup=make_inline_menu_board(KeyboardButtons.MAIN_MENU))


# main menu
async def find_price_menu(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_text('Выберите как будет строить маршрут',
                               reply_markup=make_inline_menu_board(KeyboardButtons.FIND_PRICE_MENU))


async def settings_menu(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_text('Настройки:',
                               reply_markup=make_inline_menu_board(KeyboardButtons.SETTING_MENU))


async def faq_menu(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_text('Вопрос-ответ')


async def donate_menu(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_text('Поддрержать проект')


# find_price_menu
async def new_trip(cb: CallbackQuery, state: FSMContext):
    await state.set_state(MainStates.created_new_trip)
    await create_new_trip(cb, state)


async def last_trip(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_text('Выберите из прошлых поездок')


# settings_menu
async def change_city(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_text('Текущий город ____ \nИзмените город')


async def change_phone(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_text('Текущий номер _____ \nИзмените номер')


async def notif_threshold_price(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_text('Текущий порог изменения цены для увелрмления __\nИзмените порог цены')


# faq_menu

async def faq_menu(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_text('Кнопка в разработке',
                               reply_markup=make_inline_menu_board(KeyboardButtons.FAQ_MENU))


# donate
async def donate_menu(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_text('Кнопка в разработке',
                               reply_markup=make_inline_menu_board(KeyboardButtons.DONATE_MENU))


ALL_VALUES_DICT = list(
    item
    for d in vars(KeyboardButtons).values()
    if isinstance(d, dict)
    for item in d.values()
)
ALL_CB_NEED = [i[1] for i in ALL_VALUES_DICT if type(i) is tuple]


@router.callback_query(lambda c: c.data in ALL_CB_NEED)
async def process_callback_button(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(MainStates.main_menu)
    ALL_BUTTONS = dict(
        item
        for d in vars(KeyboardButtons).values()
        if isinstance(d, dict)
        for item in d.items()
    )
    data = callback_query.data
    text, func_name = ALL_BUTTONS.get(data)
    func = globals().get(func_name)
    await func(callback_query, state)


@router.message(Command(commands=['menu']))
async def cmd_menu(msg: types.Message):
    await main_menu(msg)



