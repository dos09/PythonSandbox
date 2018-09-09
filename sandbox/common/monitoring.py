import time

import psutil

from sandbox.common.formatting import format_seconds

def log_time(msg=None):
    def decorator(func): 
        def wrapper(*args, **kwargs):
            start_time = time.time()
            func_res = func(*args, **kwargs)
            print('%s completed for %s' %
                  (msg or func.__name__, 
                   format_seconds(time.time() - start_time)))
            return func_res
        
        return wrapper

    return decorator

def show_mem_usage(psutil_proc=None):
    if psutil_proc is None:
        psutil_proc = psutil.Process()
    
    print('Memory used: %s MB' % 
          round(psutil_proc.memory_info().rss / 1000000, 2))

if __name__ == '__main__':
    @log_time()
    def tralala(a, b='b'):
        print('method started with a = %s, b = %s' % (a, b))
        time.sleep(1.25)
        print('method completed')
        return 'X'
    
    print(tralala('banana'))
