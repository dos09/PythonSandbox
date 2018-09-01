
def format_seconds(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    msg = '%s sec.' % round(s, 2)
    if m:
        msg = '%s min. %s' % (int(m), msg)
    if h:
        msg = '%s h. %s' % (int(h), msg)

    return msg

if __name__ == '__main__':
    sec = 64123.4
    print('%s seconds = %s' % (sec, format_seconds(sec)))