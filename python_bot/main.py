import asyncio
import logging
import os


from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

import config
from handlers import router
def secrets_update():
    secrets = {
    "BOT_TOKEN": os.environ.get("BOT_TOKEN"),
    "CON_URL": os.environ.get("CON_URL")
    }
    config.BOT_TOKEN=secrets["BOT_TOKEN"]
    config.CON_URL=secrets["CON_URL"]


async def main():
    bot = Bot(token=config.BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())