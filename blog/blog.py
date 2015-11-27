from flask import Flask, render_template
from os import getenv
from pymongo import MongoClient
from datetime import datetime
import json

client = MongoClient(getenv('MONGOLAB_URI'))
db = client.heroku_g8btf552
posts = db.posts

app = Flask(__name__)

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

if __name__ == '__main__':
    app.secret_key = getenv('SessionKey')
    app.run(debug=True, host='0.0.0.0')
