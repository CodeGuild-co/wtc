from flask import Flask, render_template
from os import getenv

import json

app = Flask(__name__)

def getallposts():
    data = ''
    with open('posts.json', 'r') as f:
        data = f.read()
    return json.loads(data)

@app.route('/')
def home():
    posts = getallposts()
    return render_template('home.html', posts=posts.items())


@app.route('/posts/<name>/')
def posts(name):
    return render_template('posts/%s.html' % name)

@app.route('/newposts/<name>/')
def testpost(name):
    realdata = getallposts()
    post = realdata[name]
    return render_template('viewpost.html', title=post['title'], post=post['post'], date=post['date'])

if __name__ == '__main__':
    app.secret_key = getenv('SessionKey')
    app.run(debug=True, host='0.0.0.0')
