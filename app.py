import calendar
import inspect
import urllib
from datetime import date, datetime
from glob import glob
import requests

from flask import Flask, render_template, abort, url_for, redirect
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.assets import Environment, Bundle, ManageAssets
from flask.ext.script import Manager
from werkzeug.contrib.fixers import ProxyFix
from markdown2 import Markdown
from sqlalchemy import func, desc, and_, distinct
from sqlalchemy.orm import joinedload

import config, models, filters, side_thread
from config import BLK_DAY_STRF, API_URL
from models import BlockHead, Bulletin, db_session
from filters import DayBrowser
from utils import make_api_req


app = Flask(__name__)
app.config.from_object(config)
app.wsgi_app = ProxyFix(app.wsgi_app)


# Flask-Assets
assets = Environment(app)

less = Bundle('css/app.less', depends="css/*.less", 
              filters='less', output='gen/css_all.css')
assets.register('css', less)

# Flask-Scripts
manager = Manager(app)
manager.add_command("assets", ManageAssets(assets))

# Add all functions in filter.py to the jinja env.
for name, obj in inspect.getmembers(filters):
    if inspect.isfunction(obj):
        app.jinja_env.filters[name] = obj

# Find the day of the first block was created
GENESIS_BLK = BlockHead.query.order_by(BlockHead.height).first()

#
# Routes
#

@app.route('/')
def home():
    return render_template('home.html', unconfd_bltns=[], confd_bltns=[])

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/bulletin/<string:txid>')
def bulletin(txid):
    bltn = make_api_req("/bltn/%s" % txid)
    return render_template('bulletin.html', bltn=bltn)

#
# Ways to browse
#

@app.route('/block/<string:hash>')
def block(hash):
    # Get all bulletins and endos in block
    block = make_api_req('/block/%s' % hash)
    return render_template('block.html', block=block)

@app.route('/new')
def new():
  return render_template('new.html', new=[])

@app.route('/tag/<string:tagurl>')
def tag(tagurl):
    tag = urllib.unquote(tagurl)
    tag = make_api_req("/tag/%s" % tag)
    return render_template('tag.html', tag=tag)

@app.route('/author/<string:address>')
def author(address):
    author = make_api_req("/author/%s" % address)
    return render_template('author.html', author=author)

@manager.command
def runserver():
    app.run('0.0.0.0', port=8000, debug=config.DEBUG)

@manager.command
def shell():
    from IPython import embed
    embed()

if __name__ == '__main__':
    manager.run()
