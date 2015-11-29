# TODO: Fix this on my local python installation
import sys
sys.path.append('.')

from flask import Flask, render_template, redirect, request, session
from os import getenv
from pymongo import MongoClient
from datetime import datetime
import json
from blog.util import gargs, adminpage
import facebook
import calendar
import time


client = MongoClient(getenv('MONGOLAB_URI'))
db = client.get_default_database()
posts = db.posts

app = Flask(__name__)

# Configure logging.
app.debug = True
app.logger.setLevel(logging.DEBUG)
del app.logger.handlers[:]

handler = logging.StreamHandler(stream=sys.stdout)
handler.setLevel(logging.DEBUG)
handler.formatter = logging.Formatter(
    fmt=u"%(asctime)s level=%(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%SZ",
)
app.logger.addHandler(handler)

# TODO: Move to database???
# TODO: Encrypt password
username = getenv('username', 'test')
password = getenv('password', 'test')

# Facebook graph API
graph = facebook.GraphAPI(access_token=getenv('FB_ACCESSKEY'), version='2.2')

def findposts():
    return list(posts.find(sort=[('date', -1)]))

def getadmin():
    if 'isadmin' not in session:
        session['isadmin'] = False
    return session['isadmin']

# No longer do we have to provide posts
render_template = gargs(render_template, posts_ascall=findposts, admin_ascall=getadmin)

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
            'link': 'http://wtc.codeguild.co/posts/%s/' % data['pid'],
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

if __name__ == '__main__':
    app.secret_key = getenv('SessionKey', 'not will coates')
    app.run(debug=True, host='0.0.0.0')
