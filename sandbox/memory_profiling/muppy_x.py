from pympler import tracker

def f1():
    a = [1] * (10**7)

if __name__ == '__main__':
    tr = tracker.SummaryTracker()
    f1()
    tr.print_diff()
    input('enter')