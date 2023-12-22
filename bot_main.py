from My_token import TOKEN
import asyncio
import logging
from aiogram import Bot, Dispatcher

from handlers import new_handlers

logging.basicConfig(level=logging.INFO)


async def main():
    bot = Bot(TOKEN)
    dp = Dispatcher()
    dp.include_router(new_handlers.filler_router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


def bot_run():
    asyncio.run(main())


if __name__ == '__main__':
    bot_run()
