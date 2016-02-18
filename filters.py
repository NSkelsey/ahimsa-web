import math
from datetime import datetime, timedelta

from flask import url_for

from config import BLK_DAY_STRF

def link_tags(message):
  return message

def conf_img(blk):
  return "/static/img/totalconf.png"

def unix_nice_date(ts):
  date = datetime.utcfromtimestamp(ts)
  return nice_date(date)

def nice_date(date):
    fmt = date.strftime("%H:%M  %b %d, %Y")
    fmt = fmt[:-2] + fmt[-2:].lower()
    return fmt

def todays_blocks(_):
    today = datetime.now().date()
    return url_for('blocks_by_day', day_str=today.strftime(BLK_DAY_STRF), blks='w/bltns')

def trim_msg(msg):
    if len(msg) > 500:
       pass

import hashlib

def rgb_color(address):
  m = hashlib.sha1()  
  m.update(address)
  d = m.digest()
  r = ord(d[0])
  g = ord(d[1])
  b = ord(d[2])

  return "rgb(%d, %d, %d)" % (r, g, b)

def topic_count(bltns):
    '''
    Counts the number of unique topics in the list of bulletins
    '''
    if len(bltns) == 0:
        return 0
    return 0
    #else:
    #    return len(set([b.topic for b in bltns]))

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
    b = len(bltn.message) + 100
    return b

def est_burn(bltn):
    '''
    Estimate the number of satoshis burned to store the bulletin
    '''
    b = est_storage(bltn)
    addrs = b / 20.0
    return int(5460 * math.ceil(addrs))


class DayBrowser():
    '''
    An object that spits out a html that lets us browse the blockchain by day
    '''

    def __init__(self, day, start, show_all):
        '''
        We have three pointers to relevant days which gives us the link configuration
        '''
        self.today = datetime.now().date()
        self.day = day
        self.start = start.date()
        self.show_all = show_all

    def self_link(self, show_all=False):
        '''
        Returns a url to view the current day with all blocks displayed or not
        '''
        if show_all:
            return url_for('blocks_by_day', 
                           day_str=self.day.strftime(BLK_DAY_STRF),
                           blks='all')
        else:
            return url_for('blocks_by_day',
                           day_str=self.day.strftime(BLK_DAY_STRF),
                           blks='w/bltns')

    def _gen_lnk(self):
        '''
        Generates the function used to generate date links
        '''
        lnk = lambda date: url_for('blocks_by_day', day_str=date.strftime(BLK_DAY_STRF))
        if self.show_all:
            lnk = lambda date: url_for('blocks_by_day', 
                                       day_str=date.strftime(BLK_DAY_STRF),
                                       blks='all')
        return lnk


    def render_link(self, day, label):
        a = '<a href="{}">{}</a>'
        ah = '<a href="{}" class="active">{}</a>'
     
        lnk = self._gen_lnk()

        l = ""
        if self.day == day:
            l = ah.format(lnk(day), label)
        else: 
            l = a.format(lnk(day), label)
        return l


    def links(self):
        '''
        Deterimines the number of links needed and how to lay them out for maximimum
        ease in browsing.
        '''
        
        gap = timedelta(days=2)
        a = '<a href="{}">{}</a>'
        ah = '<a href="{}" class="active">{}</a>'
     
        lnk = self._gen_lnk()

        # nice date formatting
        nd = lambda date: date.strftime('%b %d, %Y')
        back = lambda date: date - timedelta(days=1)
        forward = lambda date: date + timedelta(days=1)

        next_btn = '<a href="{}"><span class="glyphicon glyphicon-chevron-right"></span></a>'
        back_btn = '<a href="{}"><span class="glyphicon glyphicon-chevron-left"></span></a>'

        skip_now = '<a href="{}"><span class="glyphicon glyphicon-forward"></span></a>'\
                .format(lnk(self.today))
        skip_gen = '<a href="{}"><span class="glyphicon glyphicon-backward"></span></a>'\
                .format(lnk(self.start))

        links = []

        if (self.day - self.start) < gap:
            # day is within gap distance of the genesis block
            days = [
                 self.start,
                 forward(self.start),
                 forward(forward(self.start)),
            ]
            idx = days.index(self.day)
            links = [
                self.render_link(days[0], nd(days[0])),
                self.render_link(days[1], nd(days[1])),
                a.format(lnk(days[2]), nd(days[2])),
                next_btn.format(lnk(days[idx+1])),
                skip_now,
            ]

        elif (self.today - self.day) < gap:
            # day is within gap of today
            days = [
                back(back(self.today)),
                back(self.today),
                self.today,
            ]
            idx = days.index(self.day)
            links = [
                skip_gen,
                back_btn.format(lnk(days[idx-1])),
                a.format(lnk(days[0]), nd(days[0])),
                self.render_link(days[1], "Yesterday"),
                self.render_link(days[2], "Today"),
            ]

        else:
            # day is somewhere in the middle
            days = [
                back(self.day),
                self.day,
                forward(self.day),
            ]
            links = [
                skip_gen,
                back_btn.format(lnk(days[0])),
                a.format(lnk(days[0]), nd(days[0])),
                ah.format(lnk(days[1]), nd(days[1])),
                a.format(lnk(days[2]), nd(days[2])),
                next_btn.format(lnk(days[2])),
                skip_now,
            ]

        return '\n'.join(links)

