import vedomost_filler as vfill

from My_token import TOKEN
import asyncio
import logging
from aiogram import Bot, Dispatcher

import bot_handlers

logging.basicConfig(level=logging.INFO)


async def main():
    bot = Bot(TOKEN)
    dp = Dispatcher()
    dp.include_router(bot_handlers.router)
    dp.include_router(bot_handlers.router2)
    dp.include_router(bot_handlers.router3)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


month = 'oct23'
path_to_vedomost = f'months/{month}/{month}.xlsx'
username_dict = {'Jegor': 'Egr', 'Валерия': 'Lera'}

if __name__ == '__main__':
    filler = vfill.VedomostFiller(month)
    filler.refresh_vedomost()
    prices = filler.vedomost.prices
    cell = vfill.Cell(prices)
    asyncio.run(main())
else:
    filler = vfill.VedomostFiller(month)
    filler.refresh_vedomost()
    cell = vfill.Cell(filler.vedomost.prices)
