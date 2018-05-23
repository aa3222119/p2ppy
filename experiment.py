# ===========================================
# @Time    : 2018/5/19 17:26
# @Author  : antony
# @Email   : 502202879@qq.com
# @File    : experiment.py
# @Software: PyCharm Community Edition
# ===========================================
import asyncio
import time
now = lambda: time.time()
from threading import Thread


def start_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


async def do_some_work(x):
    print('Waiting {}'.format(x))
    await asyncio.sleep(x)
    print('Done after {}s'.format(x))


async def more_work(x):
    print('More work {}'.format(x))
    time.sleep(x)
    print('Finished more work {}'.format(x))


start = now()
new_loop = asyncio.new_event_loop()
t = Thread(target=start_loop, args=(new_loop,))
t.start()
print('TIME: {}'.format(time.time() - start))

asyncio.run_coroutine_threadsafe(more_work(6), new_loop)
asyncio.run_coroutine_threadsafe(more_work(4), new_loop)

dir(asyncio.open_connection)



coroutine1 = udp36.listen_bytimes(1)
coroutine2 = udp37.listen_bytimes(1)


tasks = [
    asyncio.ensure_future(coroutine1),
    asyncio.ensure_future(coroutine2),
]

loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.wait(tasks))

for task in tasks:
    print('Task ret: ', task.result())

print('TIME: ', now() - start)