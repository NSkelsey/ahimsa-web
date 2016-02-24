from datetime import timedelta, datetime

import requests
from flask import abort

from config import API_URL

class TipTracker(object):
  """Tracks the current chain tip by issuing get for api status everytime 
  the local cache becomes stale.
  """

  def __init__(self):
    # Local variables not to be exported
    self.last_req = datetime(1990, 1, 1)
    self.poll_period = timedelta(seconds=60)
    self.chain_tip = self.init_chain_tip()

  def get_poll_period(self):
    return self.poll_period 

  def set_poll_period(self, seconds):
    self.poll_period = timedelta(seconds=seconds)

  def init_chain_tip(self):
    stat = self.make_status_req() 
    last_req = datetime.now()
    self.chain_tip = stat['blkTip']
    return self.chain_tip

  def get_chain_tip(self):
    now = datetime.now()
    diff = now - self.last_req
    if diff > self.poll_period:
      self.last_req = now
      self.chain_tip = self.make_status_req()['blkTip']
    return self.chain_tip

  def make_status_req(self):
    resp = requests.get(API_URL+"/status")
    if resp.status_code == 200: 
      stat = resp.json()
      return stat
    else:
      raise APIError(resp, url, 'renewing status req')

# make_api_req should only be called within a flask route. 
# It short circuits a functions execution if there is an error.
def make_api_req(path):
    try:
      resp = requests.get(API_URL + path)
      if not resp.status_code == 200:
          abort(resp.status_code)
      return resp.json()
    except requests.ConnectionError:
      abort(500)
