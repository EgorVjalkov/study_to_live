import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram_dialog import setup_dialogs
from aiogram.fsm.storage.memory import MemoryStorage

from my_bot import my_bot
from dialog import start_handlers, windows

logging.basicConfig(level=logging.INFO)


async def main(bot: Bot):
    stor = MemoryStorage()
    dp = Dispatcher(storage=stor)
    dp.include_router(start_handlers.filler_router)
    dp.include_router(windows.filler_dialog)
    setup_dialogs(dp)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

def test_run():
    my_bot.mode = 'test'
    bot = my_bot.get_bot()
    asyncio.run(main(bot))

def bot_run():
    my_bot.mode = 'work'
    bot = my_bot.get_bot()
    asyncio.run(main(bot))


if __name__ == '__main__':
    test_run()
