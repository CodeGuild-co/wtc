# TODO: Fix this on my local python installation
import sys
sys.path.append('.')

from flask import Flask, render_template
from os import getenv
from pymongo import MongoClient
from datetime import datetime
import json
from blog.util import gargs

client = MongoClient(getenv('MONGOLAB_URI'))
db = client.get_default_database()
posts = db.posts

app = Flask(__name__)

def findposts():
    return list(posts.find(sort=[('date', -1)]))

# No longer do we have to provide posts
render_template = gargs(render_template, posts_ascall=findposts)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/feed')
def rss():
    # Thanks stack overflow!
    return render_template('feed.rss'), 200, {'Content-Type': 'application/rss+xml' }

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/posts/<name>/')
@app.route('/newposts/<name>/')
def viewpost(name):
    post  = posts.find_one({'pid': name})
    date  = datetime.fromtimestamp(post['date']).strftime('%d-%m-%Y')
    return render_template('viewpost.html', post=post, date=date)

@app.route('/tags/<name>/')
def viewtag(name):
    tagged = list(posts.find({ 'tags': { '$in': [name] } }, sort=[('date', -1)]))
    return render_template('viewtag.html', name=name, tagged=tagged)

if __name__ == '__main__':
    app.secret_key = getenv('SessionKey')
    app.run(debug=True, host='0.0.0.0')
