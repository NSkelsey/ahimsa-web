import math
from datetime import datetime

def nice_date(date):
    fmt = date.strftime("%H:%M  %b %d, %Y")
    fmt = fmt[:-2] + fmt[-2:].lower()
    return fmt

def trim_msg(msg):
    if len(msg) > 500:
       pass

def topic_count(bltns):
    '''
    Counts the number of unique topics in the list of bulletins
    '''
    if len(bltns) == 0:
        return 0
    else:
        return len(set([b.topic for b in bltns]))

def nice_size_est(bltn):
    '''
    Returns the length estimate of the message in a nicely formatted string
    '''
    l = est_storage(bltn)
    if l > 499:
        return "{:.1%} KB".format(l / 1000)
    else:
        return "{} B".format(l)


def est_storage(bltn):
    '''
    Estimate the number of bytes needed to store the bulletin
    '''
    b = len(bltn.message) + len(bltn.topic) + 10
    return b

def est_burn(bltn):
    '''
    Estimate the number of satoshis burned to store the bulletin
    '''
    b = est_storage(bltn)
    addrs = b / 20.0
    return int(5460 * math.ceil(addrs))

