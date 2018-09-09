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

import objgraph

import gc
import asyncio

import psutil

def print_dict(d):
    if isinstance(d, dict):
        for k, v in d.items():
            print(k,v)

def get_mem_usage_mb():
    return round(psutil.Process().memory_info().rss / 1000000, 2)


async def coro_x():
    # print('started')
    await asyncio.sleep(0)
    # print('finished')


async def coro_run():
    objgraph.show_growth(limit=5)
    
    coros_count = 1000#00
    coros = [coro_x() for _ in range(coros_count)]
    await asyncio.gather(*coros)
    
    print('----------------')
    objgraph.show_growth()
    
    show_refs_from_module()
    
    print('Memory used: %s MB (before coro_run exit)' % get_mem_usage_mb())

def show_backref_from_coro():
    import random
    objgraph.show_chain(
        objgraph.find_backref_chain(
            random.choice(objgraph.by_type('coroutine')),
            objgraph.is_proper_module),
        filename='chain-to-leaked.png')

    
def show_refs_from_module():
    import sys
    current_module = sys.modules[__name__]
    print(current_module)
    objgraph.show_refs([current_module], 
                       filename='references-from-main.png',
                       too_many=100,
                       refcounts=True)

def run():
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(coro_run())
    finally:
        print('Memory used: %s MB (before closing the event loop)' % 
              get_mem_usage_mb())
        loop.close()

def print_locals_globals():
    print('--- locals and globals ---')
    print('--- locals ---')
    print_dict(locals())
    print('--- globals ---')
    print_dict(globals())

if __name__ == '__main__':
    run()
    gc.collect()
    print('Memory used: %s MB (before program exit)' % get_mem_usage_mb())
