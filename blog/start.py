# TODO: Fix this on my local python installation
import sys
sys.path.append('.')

from flask import Flask, redirect, request, session
import flask

from os import getenv
from pymongo import MongoClient
from datetime import datetime
import json
import facebook
import calendar
import time

from blog import util

client = MongoClient(getenv('MONGOLAB_URI'))
db = client.get_default_database()
posts = db.posts

util.app = Flask(__name__)

util.app.secret_key = getenv('SessionKey', 'not will coates')

def findposts():
    return list(posts.find(sort=[('date', -1)]))

def getadmin():
    if 'isadmin' not in session:
        session['isadmin'] = False
    return session['isadmin']

util.render_template = util.gargs(flask.render_template, posts_ascall=findposts, admin_ascall=getadmin)

from blog.util import adminpage, render_template, app, gargs
from blog.chat import socketio

# TODO: Move to database???
# TODO: Encrypt password
username = getenv('username', 'test')
password = getenv('password', 'test')

# Facebook graph API
graph = facebook.GraphAPI(access_token=getenv('FB_ACCESSKEY'), version='2.2')

@app.route('/google37b658fdf31067f4.html')
def googleverify():
    return 'google-site-verification: google37b658fdf31067f4.html'

@app.route('/')
def home():
    posts = findposts()
    tags = {}
    for p in posts:
        for t in p['tags']:
            if t not in tags:
                tags[t] = 1
            else:
                tags[t] += 1
    return render_template('home.html', tags=sorted(tags, key=tags.get, reverse=True))

@app.route('/sitemap.xml')
def sitemap():
    posts = findposts()
    tags = {}
    for p in posts:
        for t in p['tags']:
            if t not in tags:
                tags[t] = 1
            else:
                tags[t] += 1
    return render_template('sitemap.xml', tags=sorted(tags, key=tags.get, reverse=True))

@app.route('/feed')
def rss():
    # Thanks stack overflow!
    return render_template('feed.rss'), 200, {'Content-Type': 'application/rss+xml' }

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/posts/<name>/')
def viewpost(name):
    post  = posts.find_one({'pid': name})
    date  = datetime.fromtimestamp(post['date']).strftime('%d-%m-%Y')
    return render_template('viewpost.html', post=post, date=date)

@app.route('/tags/<name>/')
def viewtag(name):
    tagged = list(posts.find({ 'tags': { '$in': [name] } }, sort=[('date', -1)]))
    return render_template('viewtag.html', name=name, tagged=tagged)

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        un = request.form['username']
        pw = request.form['password']
        # TODO: Slow equals
        if un == username and pw == password:
            session['isadmin'] = True
            return redirect('/')
        return render_template('login.html', un=un)
    else:
        return render_template('login.html')

@app.route('/logout')
def logout():
    session['isadmin'] = False
    return redirect('/')

@app.route('/addpost', methods=['GET','POST'])
@adminpage
def addpost():
    if request.method == 'POST':
        data = {
            'title': request.form['title'],
            'pid': request.form['id'],
            'post': request.form['post'].replace('\r','').split("\n\n"),
            'date': calendar.timegm(time.gmtime()),
            'tags': request.form['tags'].split(',')
        }
        posts.insert(data)
        graph.put_wall_post('I have just added a post to my blog!', attachment={
            'name': data['title'],
            'link': 'http://blog.willcoates.co.uk/posts/%s/' % data['pid'],
            'caption': 'Will Coates\' Blog',
            'description': data['post'][0]
        })
        return redirect('/posts/%s/' % data['pid'])
    else:
        return render_template('addpost.html')

@app.route('/editpost/<name>/', methods=['GET','POST'])
@adminpage
def editpost(name):
    if request.method == 'POST':
        return 'TODO'
    else:
        return 'TODO'
        
@app.route('/deletepost/<name>/')
@adminpage
def deletepost(name):
    posts.delete_one({'pid': name})
    return redirect('/')

app.debug = True
import logging
handler = logging.StreamHandler(stream=sys.stdout)
handler.setLevel(logging.DEBUG)
handler.formatter = logging.Formatter(
    fmt=u"%(asctime)s level=%(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%SZ",
)

if __name__ == '__main__':
    app.debug = True
    socketio.run(app)
