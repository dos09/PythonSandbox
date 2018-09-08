# vv Pympler ##################################################################

# from pympler import tracker
# tr = tracker.SummaryTracker()

# ^^ Pympler ##################################################################

# vv Tracemalloc ##############################################################

# import tracemalloc
#
# tracemalloc.start()
#
# def top10_tracemalloc():
#     snapshot = tracemalloc.take_snapshot()
#     top_stats = snapshot.statistics('lineno')
#
#     print("[ Top 10 ]")
#     for stat in top_stats[:10]:
#         print(stat)

# ^^ Tracemalloc ##############################################################

import gc
import asyncio

import psutil


def get_mem_usage_mb():
    return round(psutil.Process().memory_info().rss / 1000000, 2)


async def coro_x():
    # print('started')
    await asyncio.sleep(0)
    # print('finished')


async def coro_run():
    coros_count = 500000
    coros = [coro_x() for _ in range(coros_count)]
    await asyncio.gather(*coros)

    # top10_tracemalloc() # tracemalloc
    # tr.print_diff() # pympler

    print('Memory used: %s MB (before coro_run exit)' % get_mem_usage_mb())


def run():
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(coro_run())
    finally:
        loop.close()


if __name__ == '__main__':
    run()
    gc.collect()
    print('Memory used: %s MB (before program exit)' % get_mem_usage_mb())
