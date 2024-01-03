import asyncio


async def time_awaiting(func, args, time_await: int):
    await asyncio.sleep(time_await)
    await func(*args)




