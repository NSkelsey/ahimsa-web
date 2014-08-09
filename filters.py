from datetime import datetime

def nice_date(date):
    fmt = date.strftime("%b %d %Y")
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
