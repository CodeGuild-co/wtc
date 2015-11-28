from flask import Flask, render_template, redirect, request, session
from os import getenv
from pymongo import MongoClient
from datetime import datetime
import json

client = MongoClient(getenv('MONGOLAB_URI'))
db = client.heroku_g8btf552
posts = db.posts

app = Flask(__name__)

# TODO: Encrypt password
username = getenv('username', 'test')
password = getenv('password', 'test')

def getallposts():
    data = ''
    fn = 'blog/posts.json'
    if getenv('DYNO') != None:
        fn = '/app/blog/posts.json'
    with open(fn, 'r') as f:
        data = f.read()
    return json.loads(data)

@app.route('/')
def home():
    return render_template('home.html', posts=list(posts.find(sort=[('date', -1)])))

@app.route('/feed')
def rss():
    return render_template('feed.rss', posts=list(posts.find(sort=[('date', -1)])))

@app.route('/about')
def about():
    return render_template('about.html', posts=list(posts.find(sort=[('date', -1)])))

@app.route('/posts/<name>/')
@app.route('/newposts/<name>/')
def viewpost(name):
    post  = posts.find_one({'pid': name})
    return render_template('viewpost.html', title=post['title'], post=post['post'], date=datetime.fromtimestamp(post['date']).strftime('%d-%m-%Y'), posts=list(posts.find(sort=[('date', -1)])))

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        un = request.form['username']
        pw = request.form['password']
        # TODO: Slow equals
        if un == username and pw == password:
            session['isadmin'] = True
            return redirect('/')
        return render_template('login.html', un=un, posts=list(posts.find(sort=[('date', -1)])))
    else:
        return render_template('login.html', posts=list(posts.find(sort=[('date', -1)])))

@app.route('/logout')
def logout():
    session['isadmin'] = False

if __name__ == '__main__':
    app.secret_key = getenv('SessionKey') or 'not will coates'
    app.run(debug=True, host='0.0.0.0')
