from flask import Flask, render_template
from os import getenv
from pymongo import MongoClient
from datetime import datetime
import json
import util

client = MongoClient(getenv('MONGOLAB_URI'))
db = client.heroku_g8btf552
posts = db.posts

app = Flask(__name__)

def findposts():
    return list(posts.find(sort=[('date', -1)]))

# No longer do we have to provide posts
render_template = util.gargs(render_template, posts_ascall=findposts)

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

if __name__ == '__main__':
    app.secret_key = getenv('SessionKey')
    app.run(debug=True, host='0.0.0.0')
