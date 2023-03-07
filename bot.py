import asyncio
import logging
import os
from dotenv import load_dotenv, find_dotenv

from aiogram import Bot, Dispatcher

from handlers import main_menu
from create_route import first_address, second_address, third_address, \
    fourth_address, cancel_and_back, create_route
from registrations import reg


logging.basicConfig(level=logging.INFO)

load_dotenv(find_dotenv())
bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher()

bot.delete_webhook(drop_pending_updates=True)


# registrations
dp.include_router(reg.router)

# main menu
dp.include_router(main_menu.router)

# fast mode
dp.include_router(cancel_and_back.router)
dp.include_router(create_route.router)

# create route
dp.include_router(first_address.router)
dp.include_router(second_address.router)
dp.include_router(third_address.router)
dp.include_router(fourth_address.router)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(dp.start_polling(bot))
    except KeyboardInterrupt:
        print(KeyboardInterrupt)