from datetime import datetime

def nice_date(date):
    fmt = date.strftime("%b %d %Y")
    return fmt


def trim_msg(msg):
    if len(msg) > 500:
       pass
