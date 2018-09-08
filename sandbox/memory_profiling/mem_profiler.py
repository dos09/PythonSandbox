import threading

@profile
def banana():
    b = [2] * (10 ** 7)
    return b

@profile
def t1():
    print('t1')
    a = a = [1] * (10 ** 7)

@profile
def run():
    a = [1] * (10 ** 7)
    b = banana()
    threads = [
        threading.Thread(target=t1),
        threading.Thread(target=t1),
    ]
    for t in threads:
        t.start()
    
    for t in threads:
        t.join()

if __name__ == '__main__':
    run()
    