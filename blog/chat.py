# A simple chat server using websockets
# Uses a slight modification to the protocol I'm using to write a different
# application

# Modifications:
# No rooms
# Uses Facebook to authenticate

from flask import Flask, session, escape, request, redirect
from flask_socketio import SocketIO, emit
from blog.util import render_template, app
from os import getenv
from urllib.request import urlopen
from json import loads as loadjson

socketio = SocketIO(app)

fb_appid  = getenv('FB_APPID')
fb_secret = getenv('FB_SECRET')

@app.route('/chat')
def chat():
	if 'accesskey' not in session:
		if 'error_reason' in request.args:
			return 'You must login via Facebook to use our chat!'
		elif 'code' in request.args:
			resp = ''
			with urlopen('https://graph.facebook.com/v2.3/oauth/access_token?client_id=%s&redirect_uri=http://wtc.codeguild.co/chat&client_secret=%s&code=%s' % (fb_appid, fb_secret, request.args['code'])) as r:
				resp = r.read()
			j = loadjson(resp.decode("utf-8"))
			if 'access_token' in j:
				session['accesskey'] = j['access_token']
				return render_template('chat.html')
			else:
				return 'An error has occured, please try again later'
		else:
			return redirect('https://www.facebook.com/dialog/oauth?client_id=%s&redirect_uri=http://wtc.codeguild.co/chat&response_type=code' % fb_appid)
	return render_template('chat.html')

@socketio.on('message')
def handle_message(json):
	if 'accesskey' in session:
		emit('message', {
			'room': 'willcoates',
			'msg': escape('%s: %s' % (session['displayname'], json['msg'])),
			'role': 'message'
		}, broadcast=True, include_self=False)
		emit('message', {
			'room': 'willcoates',
			'msg': escape('%s' % json['msg']),
			'role': 'mymessage'
		})
	else:
		emit('message', {
			'room': 'broadcast',
			'msg': 'You have not logged in to Facebook yet. Please log in to continue.',
			'role': 'error'
		})

@socketio.on('connect')
def connect():
	if 'accesskey' not in session:
		return False
	resp = ''
	with urlopen('https://graph.facebook.com/v2.3/me?client_id=%s&client_secret=%s&accses_token=%s' % (fb_appid, fb_secret, session['accesskey'])) as r:
		resp = r.read()
	j = loadjson(resp.decode("utf-8"))
	session['displayname'] = j['name']
	emit('message', {
		'room': 'broadcast',
		'msg': 'Welcome to Will Coates\' Chat',
		'role': 'notice'
	})
	emit('message', {
		'room': 'willcoates',
		'msg': escape('%s has joined the chat!' % session['displayname']),
		'role': 'notice'
	}, broadcast=True, include_self=False)
	return True

@socketio.on('disconnect')
def disconnect():
	emit('message', {
		'room': 'willcoates',
		'msg': escape('%s has left the chat!' % session['displayname']),
		'role': 'notice'
	}, broadcast=True, include_self=False)
