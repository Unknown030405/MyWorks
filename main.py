import os
import time
import asyncio
from datetime import datetime

import aiohttp

import work

COEFF = 1
MACHINE_NAME = "_acer_laptop"


async def start(num, left, right, session):
    print(f"started counting from {left} to {right}")
    try:
        await work.forth(session, left, right, num=num)
        print(f">>> successfully ended counting from {left} to {right}")
        with open(r"logs\logs.txt", "a", encoding="utf-8") as file:
            file.write(
                f"{datetime.now().strftime('%HH:%MM:%SS')} " + f"successfully ended counting from {left} to {right}\n")
        await work.sixth(MACHINE_NAME, num=num)
        with open(r"logs\logs.txt", "a", encoding="utf-8") as file:
            file.write(
                f"{datetime.now().strftime('%HH:%MM:%SS')} " + f"successfully ended {num}th thread\n")
    except Exception as e:
        with open(r"logs\errors.txt", "a") as file:
            file.write(f"{datetime.now().strftime('%HH:%MM:%SS')} in thread {num} " + str(e) +
                       f"Please restart {left}:{right}" + "\n")


async def main():
    session = aiohttp.ClientSession()
    tasks = [
        asyncio.create_task(start(0, 40, 46, session)),
        asyncio.create_task(start(1, 46, 51, session))
    ]
    await asyncio.gather(*tasks)
    await session.close()


if __name__ == '__main__':
    t0 = time.time()
    print(t0)
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
    delta = int((time.time() - t0) / COEFF)
    print(f"{datetime.now().strftime('%HH:%MM:%SS')} It took {delta} min")
