# TODO: Fix this on my local python installation
import sys
sys.path.append('.')

from flask import Flask, render_template, redirect, request, session
from os import getenv
from pymongo import MongoClient
from datetime import datetime
import json
from blog.util import gargs, adminpage

client = MongoClient(getenv('MONGOLAB_URI'))
db = client.heroku_g8btf552
posts = db.posts

app = Flask(__name__)

# TODO: Encrypt password
username = getenv('username', 'test')
password = getenv('password', 'test')

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
    return render_template('home.html')

@app.route('/feed')
def rss():
    return render_template('feed.rss')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/posts/<name>/')
@app.route('/newposts/<name>/')
def viewpost(name):
    post  = posts.find_one({'pid': name})
    return render_template('viewpost.html', title=post['title'], post=post['post'], date=datetime.fromtimestamp(post['date']).strftime('%d-%m-%Y'))

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
        return 'TODO'
    else:
        return 'TODO'

if __name__ == '__main__':
    app.secret_key = getenv('SessionKey') or 'not will coates'
    app.run(debug=True, host='0.0.0.0')
