# ===========================================
# @Time    : 2018/5/18 17:12
# @Author  : antony
# @Email   : 502202879@qq.com
# @File    : imformater.py
# @Software: PyCharm Community Edition
# ===========================================

import asyncio
import redis
import time

now = lambda: time.time()

async def sleep1(x):
    time.sleep(x)
    return x**2

async def do_some_work(x):
    print('Waiting: ', x)

    await asyncio.gather(sleep1(x))
    return 'Done after {}s'.format(x)


start = now()

coroutine1 = do_some_work(1)
coroutine2 = do_some_work(2)
coroutine3 = do_some_work(3)

tasks = [
    asyncio.ensure_future(coroutine1),
    asyncio.ensure_future(coroutine2),
    asyncio.ensure_future(coroutine3)
]

loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.wait(tasks))

for task in tasks:
    print('Task ret: ', task.result())

print('TIME: ', now() - start)