import asyncio
import os
from dotenv import load_dotenv
import logging

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

import routers.start
import routers.auth
import routers.stats
import routers.forwards

from database.db import init_db

load_dotenv()
TOKEN = os.environ.get("BOT_TOKEN")

dp = Dispatcher()
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

async def main():
    await init_db()

    dp.include_routers(
        routers.start.router,
        routers.auth.router,
        routers.stats.router,
        routers.forwards.router
    )

    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())