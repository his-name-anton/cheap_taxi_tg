from aiogram.types import InlineKeyboardButton
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


def make_inline_menu_board(items: dict[str: str], long_f=False) -> InlineKeyboardBuilder:
    if long_f:
        board = InlineKeyboardBuilder()
        for key, value in items.items():
            board.row(InlineKeyboardButton(
                text=value[0],
                callback_data=key
            ))
    else:
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


def make_fast_mode_running_board(best_price: int = None,
                                 price_now=None,
                                 route_yandex=None) -> InlineKeyboardBuilder:
    board = InlineKeyboardBuilder()
    board.row(InlineKeyboardButton(text='⛔Отменить поиск', callback_data='cancel_fast_mode'))
    if route_yandex:
        start = route_yandex[0]
        end = route_yandex[-1]
        url = f"https://3.redirect.appmetrica.yandex.com/route?start-lat={start[1]}&start-lon={start[0]}&end-lat={end[1]}&end-lon={end[0]}&ref=cab_hound&appmetrica_tracking_id=1178268795219780156"
        board.row(InlineKeyboardButton(text=f'🚕Заказать в Яндекс {price_now}₽', url=url))
    if best_price is not None and (price_now - best_price > 5):
        board.row(InlineKeyboardButton(text=f'💰Заказать лучшую цену {best_price}₽', callback_data='create_order_taxi'))
    return board.as_markup()


def make_address_keyboard_menu(items: dict[str: str],
                               exceptions: list = [],
                               can_order: bool = False) -> InlineKeyboardBuilder:
    board = InlineKeyboardBuilder()
    for i, (key, value) in enumerate(items.items()):
        if value in exceptions:
            continue
        if i > 4:
            break
        board.row(InlineKeyboardButton(
            text=value[1],
            callback_data=key
        ))
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

share_geo_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Поделиться геолокацией", request_location=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )