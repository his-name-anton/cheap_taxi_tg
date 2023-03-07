import datetime

from aiogram import types, Router
from aiogram.filters import Text
from aiogram.fsm.context import FSMContext

from create_route.create_route import FAST_MODE_DICT
from handlers.states import MainStates
from keyboards.buttons import KeyboardButtons
from keyboards.keyboards import make_inline_menu_board
from parcsing.parc import cancellation_when_searching, close_driver

router = Router()


@router.callback_query(Text(['cancel_fast_mode']))
async def cancel_fast_mode(cb: types.CallbackQuery, state: FSMContext):
    await state.set_state(MainStates.main_menu)
    driver = FAST_MODE_DICT.get(cb.from_user.id).get('driver')
    await close_driver(driver)
    await state.clear()
    FAST_MODE_DICT[cb.from_user.id]['is_fast_mode'] = False
    await cb.message.edit_reply_markup(reply_markup=None)
    await cb.message.edit_text(
        cb.message.text + f"\n\nЗавершил поиск в {datetime.datetime.now().strftime('%H:%M')}"
    )
    await cb.answer()


@router.callback_query(Text(['cancellation_order']))
async def cancellation_order(cb: types.CallbackQuery, state: FSMContext):
    driver = FAST_MODE_DICT.get(cb.from_user.id).get('driver')
    await cb.answer()
    FAST_MODE_DICT[cb.from_user.id]['sec_for_cancel_order'] = 0
    await cb.message.edit_reply_markup(reply_markup=None)
    await cancellation_when_searching(driver)
    await state.set_state(MainStates.main_menu)
    await cb.message.answer('Отменил заказ такси')


@router.callback_query(Text(['cancel_create_trip']))
async def back_to_main_menu(cb: types.CallbackQuery, state: FSMContext):
    await cb.message.edit_text('Меню', reply_markup=make_inline_menu_board(KeyboardButtons.MAIN_MENU))