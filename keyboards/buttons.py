class KeyboardButtons:
    CMD_MENU = {
        'main_menu': 'Меню'
    }
    MAIN_MENU = {
        'find_price_menu': ('Найти цены', 'find_price_menu'),
        'slow_mode_menu': ('Фоновая проверка цен', 'slow_mode_menu'),
        'settings_menu': ('Настройки', 'settings_menu'),
        'stats_menu': ('Статистика', 'stats_menu'),
        'donate_menu': ('Донат', 'donate_menu'),
    }

    FIND_PRICE_MENU = {
        'new_trip': ('Новый маршрут', 'new_trip'),
        'last_trips': ('Выбрат из прошлых', 'last_trips'),
        'back_to_main_menu': ('⬅ Назад в меню', 'back_to_main_menu')
    }

    SLOW_MODE_MENU = {
        'back_to_main_menu': ('⬅ Назад в меню', 'back_to_main_menu'),
        'slow_mode': ('📌Создать маршрут', 'slow_mode')
    }

    SETTING_MENU = {
        'change_city': ('Город для поиска', 'change_city'),
        'notif_threshold_price': ('Изменение цены для уведомления', 'notif_threshold_price'),
        'back_to_main_menu': ('⬅ Назад в меню', 'back_to_main_menu')
    }

    STATS_MENU = {
        'back_to_main_menu': ('⬅ Назад в меню', 'back_to_main_menu')
    }

    DONATE_MENU = {
        'back_to_main_menu': ('⬅ Назад в меню', 'back_to_main_menu')
    }


class SettingsButtons:
    price_alert = {
        'change_price_threshold_10': '10 рублей',
        'change_price_threshold_20': '20 рублей',
        'change_price_threshold_30': '30 рублей',
        'change_price_threshold_40': '40 рублей',
        'change_price_threshold_50': '50 рублей',
        'change_price_threshold_100': '100 рублей',
        'back_to_main_menu': '⬅ Назад в меню'
    }
