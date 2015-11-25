from flask import Flask, render_template
from os import getenv

import json

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
    posts = getallposts()
    return render_template('home.html', posts=posts.items())


@app.route('/posts/<name>/')
@app.route('/newposts/<name>/')
def posts(name):
    posts = getallposts()
    post  = posts[name]
    return render_template('viewpost.html', title=post['title'], post=post['post'], date=post['date'], posts=posts.items())

if __name__ == '__main__':
    app.secret_key = getenv('SessionKey')
    app.run(debug=True, host='0.0.0.0')
