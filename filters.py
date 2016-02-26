import math
from datetime import datetime, timedelta

from requests import ConnectionError
from flask import url_for

import utils

tipTrack = utils.TipTracker()

def endo_colors(num):
  if num < 1:
    return "#BBB"
  elif 2 < num and num < 5:
    return "rgb(188, 227, 163)"
  else:
    return "#6cc644"


def plural(cnt, sing, plural):
  if cnt > 1:
    return plural
  return sing

def link_tags(message):
  return message

def tag_list(msg):
  tags = [i  for i in msg.split() if i.startswith("#")]
  return tags

def conf_img(blk):
  chain_tip = None
  try:
    chain_tip = tipTrack.get_chain_tip()
  except ConnectionError:
    return
  height = chain_tip['height'] - blk['h']
  if height > 5:
    return "/static/img/totalconf.png"
  elif height < 0:
    return "/static/img/0conf.png"
  else:
    return "/static/img/%dconf.png" % height

def unix_nice_date(ts, just_day=False):
  date = datetime.utcfromtimestamp(ts)
  return nice_date(date, just_day)

def nice_date(date, just_day=False):
    fmt = date.strftime("%H:%M  %b %d, %Y")
    fmt = fmt[:-2] + fmt[-2:].lower()
    if just_day:
      fmt = date.strftime("%b %d, %Y")
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
    b = len(bltn['msg']) + 100
    return b

def est_burn(bltn):
    '''
    Estimate the number of satoshis burned to store the bulletin
    '''
    b = est_storage(bltn)
    addrs = b / 20.0
    return int(5460 * math.ceil(addrs))

