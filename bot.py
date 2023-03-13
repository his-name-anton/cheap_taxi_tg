import asyncio
import logging
import os
from dotenv import load_dotenv, find_dotenv

from aiogram import Bot, Dispatcher

from menu import main_menu
from fast_mode import select_addresses, cancel_and_back, create_route
from slow_mode import select_addresses_slow_mode, create_route_slow_mode
from registrations import reg


logging.basicConfig(level=logging.INFO)

load_dotenv(find_dotenv())
bot = Bot(os.getenv('BOT_TOKEN'))
dp = Dispatcher()

bot.delete_webhook(drop_pending_updates=True)


# registrations
dp.include_router(reg.router)

# main menu
dp.include_router(main_menu.router)

# # fast mode
dp.include_router(cancel_and_back.router)
dp.include_router(create_route.router)
dp.include_router(select_addresses.router)

# slow mode
dp.include_router(create_route_slow_mode.router)
dp.include_router(select_addresses_slow_mode.router)




if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(dp.start_polling(bot))
    except KeyboardInterrupt:
        print(KeyboardInterrupt)