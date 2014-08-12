from datetime import datetime

def nice_date(date):
    fmt = date.strftime("%H:%M  %b %d, %Y")
    fmt = fmt[:-2] + fmt[-2:].lower()
    return fmt

def trim_msg(msg):
    if len(msg) > 500:
       pass

def topic_count(bltns):
    """Counts the number of unique topics in the list of bulletins"""

    if len(bltns) == 0:
        return 0
    else:
        return len(set([b.topic for b in bltns]))

def length_est(msg):
    '''
    Returns the length estimate of the message in a nicely formatted string
    '''
    l = len(msg)
    if l > 499:
        return "{:.1%} KB".format(l / 1000)
    else:
        return "{} B".format(l)


