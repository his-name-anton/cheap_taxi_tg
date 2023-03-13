from aiogram.fsm.state import StatesGroup, State


class MainStates(StatesGroup):

    start_reg = State()
    registrations_city = State()
    registrations_phone = State()
    main_menu = State()
    created_new_trip = State()
    favorite_addresses = State()
    first_address_fm = State()
    second_address_fm = State()
    third_address_fm = State()
    fourth_address_fm = State()
    fast_mode = State()
    created_order = State()

    # slow mode
    create_slow_mode = State()
    first_address_sm = State()
    second_address_sm = State()
    third_address_sm = State()
    fourth_address_sm = State()
    select_time_sm = State()

    state_fm_select_address = [
        first_address_fm,
        second_address_fm,
        third_address_fm,
        fourth_address_fm
    ]

    state_sm_select_address = [
        first_address_sm,
        second_address_sm,
        third_address_sm,
        fourth_address_sm
    ]

