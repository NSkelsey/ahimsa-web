import calendar
import inspect
import urllib
from datetime import date, datetime
from glob import glob

from flask import Flask, render_template, abort, request, url_for, redirect
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.assets import Environment, Bundle, ManageAssets
from flask.ext.script import Manager
from werkzeug.contrib.fixers import ProxyFix
from markdown2 import Markdown
from sqlalchemy import func, desc, and_, distinct
from sqlalchemy.orm import joinedload

import config, models, filters, side_thread
from config import BLK_DAY_STRF
from models import BlockHead, Bulletin, db_session
from filters import DayBrowser

app = Flask(__name__)
app.config.from_object(config)
app.wsgi_app = ProxyFix(app.wsgi_app)


# Flask-Assets
assets = Environment(app)

js_files = ['lib/js/jquery.js', 'lib/bootstrap/dist/js/bootstrap.js', 
            'lib/js/d3.js', 'lib/js/md5.js']
js = Bundle(*js_files, output='gen/js_lib.js')
assets.register('js_lib', js)

js_files = ['/'.join(f.split('/')[1:]) for f in glob('static/js/*.js')]
js = Bundle(*js_files, output='gen/js_all.js')
assets.register('js', js)

less = Bundle('css/app.less', depends="css/*.less", 
              filters='less', output='gen/css_all.css')
assets.register('css', less)

# Flask-Scripts
manager = Manager(app)
manager.add_command("assets", ManageAssets(assets))


# db hackery
@app.teardown_appcontext
def shutdown_session(exception=None):
    # closes the session
    db_session.remove()

# jinja filters
markdowner = Markdown()
app.jinja_env.globals['render_markdown'] = markdowner.convert

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
    unconfd_bltns = db_session\
        .query(Bulletin)\
        .filter(Bulletin.block == None)\
        .limit(25)\
        .all()
    recent_confd_bltns = db_session\
        .query(Bulletin)\
        .join(BlockHead)\
        .order_by(desc(BlockHead.height))\
        .limit(25)\
        .all()
    return render_template('home.html', 
                           unconfd_bltns=unconfd_bltns, 
                           confd_bltns=recent_confd_bltns)

@app.route('/create')
def create():
    return render_template('create.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/bulletin/<string:txid>')
def bulletin(txid):
    bltn = Bulletin.query.filter_by(txid=txid).limit(1).first()
    if bltn is None:
        abort(404)
    return render_template('bulletin.html', bltn=bltn)

#
# Ways to browse
#

@app.route('/blocks')
def blocks():
    '''
    Redirect to todays blocks
    '''
    today = datetime.now().date()
    return redirect(url_for('blocks_by_day', 
                    day_str=today.strftime(BLK_DAY_STRF)))
    

@app.route('/blocks/<int:height>')
def height(height):
    blocks = db_session.query(BlockHead)\
        .order_by(desc('blocks_height'))\
        .filter(and_(BlockHead.height <= height,
                     BlockHead.height > height - 25))\
        .all()

    assert len(blocks) == 25

    return render_template('blocks.html', blocks=blocks)

@app.route('/blocks/<string:day_str>/', defaults={'blks': 'w/bltns'})
@app.route('/blocks/<string:day_str>/<string:blks>')
def blocks_by_day(day_str, blks):

    day = datetime.strptime(day_str, BLK_DAY_STRF).date()
    i = calendar.timegm(day.timetuple())

    if day > datetime.now().date() or day < GENESIS_BLK.datetime().date():
        abort(404)


    show_all_blks = False
    if blks == 'all':
        show_all_blks = True

    # To speed up this query we are eventually going to have to index the db on
    # day of timestamp. Either we do this or load it all into memory...
    day_query = BlockHead.query\
        .order_by('blocks_height')\
        .filter(and_(BlockHead.timestamp < i + 86400, # A single day in seconds
                     BlockHead.timestamp > i))
    blocks = []
    if show_all_blks:
        blocks = day_query.options(joinedload('bulletin_collection')).all()
    else: 
        blocks = day_query.join(Bulletin)\
            .group_by(BlockHead)\
            .all()

    day_browser = DayBrowser(day, 
                             start=GENESIS_BLK.datetime(), 
                             show_all=show_all_blks)

    return render_template('blocks.html', 
                            blocks=blocks, 
                            day_browser=day_browser,
                            sort="By Date")


@app.route('/block/<string:hash>')
def block(hash):
    # get all bulletins in block
    block = BlockHead.query.filter_by(hash=hash)\
        .options(joinedload('bulletin_collection'))\
        .first()

    if block is None:
        abort(404)
    return render_template('block.html', block=block)

@app.route('/tags')
def tags():
    tags = db_session.query(func.count('*'), Bulletin.tags.label('title'))\
        .group_by(Bulletin.tags)\
        .order_by(desc('1'))\
        .limit(25)\
        .all()
    return render_template('topics.html', topics=tags)


@app.route('/topics')
def topics():
    topics = db_session.query(func.count('*'), Bulletin.topic.label('title'))\
        .group_by(Bulletin.topic)\
        .order_by(desc('1'))\
        .limit(25)\
        .all()
    return render_template('topics.html', topics=topics)

@app.route('/tag/<string:tagurl>')
def tag(tagurl):
    tag = urllib.unquote(tagurl)

    headline = db_session\
        .query(func.count('*').label('num'), Bulletin.topic.label('title'))\
        .filter(Bulletin.topic == topic)\
        .group_by(Bulletin.topic)\
        .limit(1)\
        .first()

    if headline is None:
        abort(404)

    res = db_session.query(Bulletin, BlockHead)\
            .join(BlockHead)\
            .filter(Bulletin.topic == topic)\
            .order_by(desc(BlockHead.height))\
            .limit(25)\
            .all()
    bltns = [bltn for (bltn, _) in res]
    return render_template('topic.html', headline=headline, topic=topic, bltns=bltns)

@app.route('/authors')
def authors():
    authors = db_session\
        .query(func.count('*').label('num'), Bulletin.author.label('name'))\
        .group_by(Bulletin.author)\
        .order_by(desc('1'))\
        .limit(25)\
        .all()
    return render_template('authors.html', authors=authors)

@app.route('/author/<string:address>')
def author(address):
    author = db_session\
        .query(func.count('*').label('num'), Bulletin.author.label('name'))\
        .group_by(Bulletin.author)\
        .filter(Bulletin.author == address)\
        .first()
    if author is None:
        abort(404)
    # TODO fix sort order
    bltns = Bulletin.query\
            .filter(Bulletin.author==address)\
            .limit(25)
    return render_template('author.html', author=author, bltns=bltns)

@manager.command
def runserver():
    app.run('0.0.0.0', port=8000, debug=config.DEBUG)

@manager.command
def shell():
    from IPython import embed
    embed()

if __name__ == '__main__':
    manager.run()
