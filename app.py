import urllib
from glob import glob

from flask import Flask, render_template, abort
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.assets import Environment, Bundle, ManageAssets
from flask.ext.script import Manager
from werkzeug.contrib.fixers import ProxyFix
from markdown2 import Markdown
from sqlalchemy import func, desc

import config, models, filters
from config import DEBUG
from models import Base, BlockHead, Bulletin, db_session

app = Flask(__name__)
app.config.from_object(config)
app.wsgi_app = ProxyFix(app.wsgi_app)

# Flask-Assets
assets = Environment(app)

js_files = ['lib/js/jquery.js', 'lib/bootstrap/dist/js/bootstrap.js', 
            'lib/js/d3.js', 'lib/js/md5.js']
js = Bundle(*js_files, output='gen/js_lib.js')
assets.register('js_lib', js)

js_files = ['js/addrname.js', 'js/onload.js']
js = Bundle(*js_files, output='gen/js_all.js')
assets.register('js', js)

less_files = ['/'.join(f.split('/')[1:]) for f in glob('static/css/*.less')]
print less_files
less = Bundle(*less_files, filters='less', output='gen/css_all.css')
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
app.jinja_env.filters['nice_date']       = filters.nice_date
app.jinja_env.filters['trim_msg']        = filters.trim_msg

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
    # return last 25 blocks
    return render_template('blocks.html')

@app.route('/block/<string:blockhash>')
def block(blockhash):
    # get all bulletins in block
    return render_template('block.html', block=block)

@app.route('/topics')
def topics():
    topics = db_session.query(func.count('*'), Bulletin.topic.label('title'))\
                .group_by(Bulletin.topic)\
                .order_by(desc('1'))\
                .limit(25)\
                .all()
    return render_template('topics.html', topics=topics)

@app.route('/topic/<string:topurl>')
def topic(topurl):
    topic = urllib.unquote(topurl)

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
    bltns = Bulletin.query\
            .filter(Bulletin.author==address)\
            .limit(25)
    return render_template('author.html', author=author, bltns=bltns)

@manager.command
def runserver():
    app.run('0.0.0.0', debug=DEBUG)


if __name__ == '__main__':
    manager.run()
