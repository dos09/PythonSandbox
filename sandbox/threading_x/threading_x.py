import objgraph
import time
import random
import threading

from sandbox.common.monitoring import show_mem_usage

LIMIT = 5


def print_msg(msg):
    tid = threading.get_ident()
    for _ in range(LIMIT):
        print('(%s) %s' % (tid, msg))
        time.sleep(random.uniform(0.2, 0.9))


def run():
    threads = [
        threading.Thread(target=print_msg, args=('X',)),
        threading.Thread(target=print_msg, args=('Y',))
    ]
    for t in threads:
        t.start()

    for t in threads:
        t.join()

if __name__ == '__main__':
    show_mem_usage()
    objgraph.show_growth()
    run()
    print('run done')
    show_mem_usage()
    a = [1]
    objgraph.show_growth()
    
