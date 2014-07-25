from flask import Flask, render_template
from flask.ext.sqlalchemy import SQLAlchemy
from werkzeug.contrib.fixers import ProxyFix
from markdown2 import Markdown

import config, models, filters
from config import DEBUG
from models import Base, BlockHead, Bulletin, Session

app = Flask(__name__)
app.config.from_object(config)
app.wsgi_app = ProxyFix(app.wsgi_app)

Base.prepare(models.engine, reflect=True)

markdowner = Markdown()

app.jinja_env.globals['render_markdown'] = markdowner.convert
app.jinja_env.filters['nice_date'] = filters.nice_date

db = SQLAlchemy(app)
db.Model = Base


@app.route('/')
def home():
    session = Session()
    first = session.query(Bulletin).first()
    return render_template('home.html', recent=first)

@app.route('/blocks/<string:blockhash>')
def block(blockhash):
    pass 

@app.route('/topic/<string:topic>')
def topic(topic):
    pass

@app.route('/bltn/<string:txid>')
def bulletin(txid):
    pass

@app.route('/topics')
def topics():
    pass

@app.route('/author/<string:author>')
def author():
    pass

if __name__ == '__main__':
    app.run('0.0.0.0', debug=DEBUG)
