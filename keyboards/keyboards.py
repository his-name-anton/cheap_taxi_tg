from aiogram.types import InlineKeyboardButton, InlineQueryResultLocation
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

FAVORITE_ADDRESS = {
    '-1': ('🏡 Дом', 'Дружбы 31'),
    '-2': ('🗿 Работа', 'Советский проспект 2/6')
}


def make_inline_simple_board(items: dict[str: str]) -> InlineKeyboardBuilder:
    board = InlineKeyboardBuilder()
    for key, value in items.items():
        board.row(InlineKeyboardButton(
            text=value,
            callback_data=key
        ))
    return board.as_markup()


def make_inline_menu_board_by_2_items(items: dict[str: str]) -> InlineKeyboardBuilder:
    buttons = []
    row = []

    for key, value in items.items():
        row.append(InlineKeyboardButton(
            text=value,
            callback_data=key
        ))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if len(row) == 1:
        buttons.append(row)
    board = InlineKeyboardBuilder(buttons)
    return board.as_markup()


def make_inline_menu_board(items: dict[str: str]) -> InlineKeyboardBuilder:
    buttons = []
    row = []

    for key, value in items.items():
        row.append(InlineKeyboardButton(
            text=value[0],
            callback_data=key
        ))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if len(row) == 1:
        buttons.append(row)
    board = InlineKeyboardBuilder(buttons)
    return board.as_markup()


def make_fast_mode_running_board(best_price: int = None) -> InlineKeyboardBuilder:
    board = InlineKeyboardBuilder()
    board.add(InlineKeyboardButton(text='⛔Отменить', callback_data='cancel_fast_mode'))
    if best_price is not None:
        board.add(InlineKeyboardButton(text=f'🚕Заказать \n{best_price}р', callback_data='create_order_taxi'))
    return board.as_markup()


def make_address_keyboard_menu(items: dict[str: str],
                               exceptions: list = [],
                               can_order: bool = False) -> InlineKeyboardBuilder:
    buttons = [
        [
            InlineKeyboardButton(
                text=FAVORITE_ADDRESS['-1'][0],
                callback_data='-1'
            ),
            InlineKeyboardButton(
                text=FAVORITE_ADDRESS['-2'][0],
                callback_data='-2'
            )
        ]
    ]
    row = []
    for i, (key, value) in enumerate(items.items()):
        if value in exceptions:
            continue
        row.append(InlineKeyboardButton(
            text=value,
            callback_data=key
        ))
        if len(row) == 2:
            buttons.append(row)
            row = []

    if len(row) == 1:
        buttons.append(row)
    try:
        buttons = buttons[:3]
    except:
        pass
    board = InlineKeyboardBuilder(buttons)
    board.row(InlineKeyboardButton(
        text='⏪ В меню',
        callback_data='cancel_create_trip'
    ))
    if can_order:
        board.add(InlineKeyboardButton(
            text='Искать цену ⏩',
            callback_data='run_fast_mode'
        ))
    return board.as_markup()


share_phone_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Поделиться номером", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )