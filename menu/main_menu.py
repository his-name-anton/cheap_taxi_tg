import logging
# -------------------------------------------
from aiogram import types, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
# -------------------------------------------
from fast_mode.create_route import create_new_trip
from menu.states import MainStates
from keyboards.keyboards import make_inline_menu_board, make_inline_menu_board_by_2_items, make_inline_simple_board
from keyboards.buttons import KeyboardButtons, SettingsButtons
from fast_mode.create_route import FAST_MODE_DICT
from data_base.data_base import db
from slow_mode.create_route_slow_mode import create_slow_mode

logging.basicConfig(level=logging.INFO)
router = Router()


# main menu
async def main_menu(msg: Message):
    await msg.answer('Меню', reply_markup=make_inline_menu_board(KeyboardButtons.MAIN_MENU))


async def back_to_main_menu(cb: CallbackQuery, state: FSMContext):
    await state.set_state(MainStates.main_menu)
    await cb.message.edit_text('Меню', reply_markup=make_inline_menu_board(KeyboardButtons.MAIN_MENU))


# main menu
async def find_price_menu(cb: CallbackQuery, state: FSMContext):
    if FAST_MODE_DICT.get(cb.from_user.id) and FAST_MODE_DICT.get(cb.from_user.id).get('is_fast_mode'):
        await cb.message.edit_text('Вы уже ищете цены. \n'
                                   'Вы можете отменить предыдущий поиск и начать новый',
                                   reply_markup=make_inline_menu_board_by_2_items({
                                        'back_to_main_menu': '⬅ Назад в меню',
                                        'cancel_fast_mode': '⛔Отменить'
                                   })
                                   )
    else:
        await cb.message.edit_text('Выберите как будет строить маршрут',
                                   reply_markup=make_inline_menu_board(KeyboardButtons.FIND_PRICE_MENU))


async def slow_mode_menu(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_text('У вас 0 фоновых режимов. '
                               'Вы можете создать до 2-ух маршрутов и указать для них час поиска цен.'
                               'Например вы можете указать час когда вы едете на работу, '
                               'и указать маршрут от дома до работы. '
                               'Тогда в этот час, в любой момент для вас будет доступна '
                               'возмонжость заказать лучшею цены за посдедние 10 минут',
                               reply_markup=make_inline_menu_board(KeyboardButtons.SLOW_MODE_MENU))


async def settings_menu(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_text('Настройки:',
                               reply_markup=make_inline_menu_board(KeyboardButtons.SETTING_MENU,
                                                                   long_f=True))


async def stats_menu(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_text('Статистика по прошлым поискам')


async def donate_menu(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_text('Поддрержать проект')


# find_price_menu
async def new_trip(cb: CallbackQuery, state: FSMContext):
    await state.set_state(MainStates.created_new_trip)
    await create_new_trip(cb, state)


async def last_trip(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_text('Выберите из прошлых поездок')


# slow mode
async def slow_mode(cb: CallbackQuery, state: FSMContext):
    await state.set_state(MainStates.create_slow_mode)
    await create_slow_mode(cb, state)


# settings_menu
async def change_city(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_text('Текущий город ____ \nИзмените город')


async def notif_threshold_price(cb: CallbackQuery, state: FSMContext):
    price_alert_threshold = db.get_setting_value(cb.from_user.id, 'price_alert_threshold')
    await cb.message.edit_text(f'Текущий порог изменения цены для отправки уведомления: {price_alert_threshold} рублей\n\n'
                               f'Выберите новый порог изменения цены',
                               reply_markup=make_inline_simple_board(
                                   SettingsButtons.price_alert
                               ))


@router.callback_query(lambda c: 'change_price_threshold' in c.data)
async def change_notif_threshold_price(cb: CallbackQuery, state: FSMContext):
    value = SettingsButtons.price_alert.get(cb.data)
    value = int(value.replace('рублей', '').strip())
    db.update_value(f"""
        UPDATE user_settings
        SET value = {value}
        WHERE chat_id = {cb.from_user.id}
        and setting_name = 'price_alert_threshold'
    """)
    await cb.message.edit_text(f'Изменил порог изменения цены для отправки уведомления на {value} рублей',
                               reply_markup=make_inline_simple_board({
                                        'back_to_main_menu': '⬅ Назад в меню',
                                   }))


# stats_menu
async def stats_menu(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_text('Кнопка в разработке',
                               reply_markup=make_inline_menu_board(KeyboardButtons.STATS_MENU))


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



