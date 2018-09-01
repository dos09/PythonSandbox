
def confirm(msg='Proceed? (y/n) '):
    yes = ['1', 'y', 'yes', 'ok']
    no = ['0', 'n', 'no']
    while True:
        ans = input(msg).strip().lower()
        if ans in yes:
            return True
        
        if ans in no:
            return False
        
if __name__ == '__main__':
    print(confirm())
    