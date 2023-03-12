import asyncio
import logging
import os
from dotenv import load_dotenv, find_dotenv

from aiogram import Bot, Dispatcher

from handlers import main_menu
from create_route import select_addresses, cancel_and_back, create_route
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

# # create route
dp.include_router(select_addresses.router)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(dp.start_polling(bot))
    except KeyboardInterrupt:
        print(KeyboardInterrupt)