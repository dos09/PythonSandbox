import psutil
import asyncio
import requests
import time
import collections
import json


def show_mem_usage():
    print(psutil.Process().memory_info().rss // 1000000, 'MB memory used')


def run():
    print('started')
    show_mem_usage()
    input('press enter to continue')
    print('completed')

if __name__ == '__main__':
    run()

"""
MEMORY USAGE:
- no imports (3.9 MB in task manager)
- psutil imported (5.9 MB in task manager, 11 MB from psutil)
- + asyncio (8.6 MB in task manager, 14 MB from psutil)
- + requests (11.8 MB in task manager, 18 MB from psutil)
- + time, collections, json (from the standard lib) (no change in memory usage)

Importing specific methods/classes from module, does not reduce memory usage
"""
