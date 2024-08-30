from My_token import TOKEN
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram_dialog import setup_dialogs
from aiogram.fsm.storage.memory import MemoryStorage

from dialog import start_handlers, windows

logging.basicConfig(level=logging.INFO)


async def main():
    stor = MemoryStorage()
    bot = Bot(TOKEN)
    dp = Dispatcher(storage=stor)
    dp.include_router(start_handlers.filler_router)
    dp.include_router(windows.filler_dialog)
    setup_dialogs(dp)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


def bot_run():
    asyncio.run(main())


if __name__ == '__main__':
    bot_run()
