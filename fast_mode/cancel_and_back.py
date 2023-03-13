import datetime
from pprint import pprint

from aiogram import types, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Text
from aiogram.fsm.context import FSMContext

from fast_mode.create_route import FAST_MODE_DICT
from menu.states import MainStates
from keyboards.buttons import KeyboardButtons
from keyboards.keyboards import make_inline_menu_board
from parcsing.api_yandex import canceled_order_yandex
from data_base.data_base import db


router = Router()


@router.callback_query(Text(['cancel_fast_mode']))
async def cancel_fast_mode(cb: types.CallbackQuery, state: FSMContext):
    await state.set_state(MainStates.main_menu)
    await state.clear()
    msg_session: types.Message = FAST_MODE_DICT[cb.from_user.id]['msg_session']
    db.set_result_session_fast_mode(FAST_MODE_DICT[cb.from_user.id]['session_id'],
                                    'cancel_fast_mode')
    await cb.message.edit_reply_markup(reply_markup=None)
    await cb.message.edit_text(
        cb.message.text + f"\n\nЗавершил поиск в {datetime.datetime.now().strftime('%H:%M')}"
    )

    try:
        await msg_session.edit_reply_markup(reply_markup=None)
        await msg_session.edit_text(
            msg_session.text + f"\n\nЗавершил поиск в {datetime.datetime.now().strftime('%H:%M')}"
        )
    except TelegramBadRequest:
        pass

    FAST_MODE_DICT[cb.from_user.id] = {}
    await cb.answer()


@router.callback_query(Text(['cancellation_order']))
async def cancellation_order(cb: types.CallbackQuery, state: FSMContext):
    orderid = FAST_MODE_DICT[cb.from_user.id]['orderid']
    if await canceled_order_yandex(orderid):
        FAST_MODE_DICT[cb.from_user.id]['sec_for_cancel_order'] = 0
        await cb.message.edit_text(cb.message.text + '\n\n Отменил заказ такси ❌')
        db.set_result_session_fast_mode(FAST_MODE_DICT[cb.from_user.id]['session_id'],
                                        'cancellation_order',
                                        FAST_MODE_DICT[cb.from_user.id]['best_offer'])
        await state.set_state(MainStates.main_menu)
    else:
        await cb.message.answer('Ошибка при отмене заказа')
    FAST_MODE_DICT[cb.from_user.id] = {}
    await cb.answer()


@router.callback_query(Text(['cancel_create_trip']))
async def back_to_main_menu(cb: types.CallbackQuery, state: FSMContext):
    await cb.message.edit_text('Меню', reply_markup=make_inline_menu_board(KeyboardButtons.MAIN_MENU))