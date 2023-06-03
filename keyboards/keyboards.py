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
    if best_price is not None and (price_now - best_price >= 0):
        board.row(InlineKeyboardButton(text=f'💰Заказать лучшую цену {best_price}₽', callback_data='create_order_taxi'))
    return board.as_markup()


def make_recent_address_kb_for_fm(items: dict[str: str],
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


def make_recent_address_kb_for_sm(items: dict[str: str],
                                  exceptions: list = [],
                                  can_next: bool = False) -> InlineKeyboardBuilder:
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
    if can_next:
        board.add(InlineKeyboardButton(
            text='Выбрать время ⏩',
            callback_data='select_time_sm'
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


def make_kb_for_select_time_sm(page=1):
    from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

    num_hours = 24

    progress = 30

    # create a list of button names with the hour ranges
    button_names = []
    for i in range(num_hours):
        start_hour = i
        end_hour = (i + 1) % num_hours
        button_name = f"{start_hour:02d}:00-{end_hour:02d}:00"
        button_names.append(button_name)
        button_name = f"{start_hour:02d}:{progress:02d}-{end_hour:02d}:{progress:02d}"
        button_names.append(button_name)

    # create a list of InlineKeyboardButton objects
    buttons = [InlineKeyboardButton(text=name, callback_data=f"button_{name}") for i, name in enumerate(button_names)]

    # define the number of buttons to show per page
    buttons_per_page = 15

    # create a list of InlineKeyboardMarkup objects, one for each page
    pages = []
    for i in range(0, len(buttons), buttons_per_page):
        page_buttons = buttons[i:i + buttons_per_page]
        page_rows = [page_buttons[j:j+3] for j in range(0, len(page_buttons), 3)]
        page_keyboard = InlineKeyboardMarkup(row_width=3, inline_keyboard=page_rows)
        pages.append(page_keyboard)

    # define the navigation buttons (arrows)
    prev_button = InlineKeyboardButton(text="<", callback_data="prev_page_for_sm")
    next_button = InlineKeyboardButton(text=">", callback_data="next_page_for_sm")

    # create the first page with navigation buttons and return it
    current_page = page
    keyboard = pages[current_page]
    keyboard.inline_keyboard.append([prev_button, next_button])
    return keyboard
