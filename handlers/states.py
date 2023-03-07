from aiogram.fsm.state import StatesGroup, State


class MainStates(StatesGroup):

    start_reg = State()
    registrations_city = State()
    registrations_phone = State()
    main_menu = State()
    created_new_trip = State()
    favorite_addresses = State()
    first_address = State()
    second_address = State()
    third_address = State()
    fourth_address = State()
    fast_mode = State()
    created_order = State()

    state_list = [
        first_address,
        second_address,
        third_address,
        fourth_address
    ]