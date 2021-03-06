from flask import redirect, session
from functools import wraps

def ascallparse(data):
    newdata = data.copy()
    for k, v in data.items():
        if k.endswith('_ascall'):
            realk = k[:-7]
            newdata[realk] = v()
            del newdata[k]
    return newdata

def gargs(method, **dkwargs):
	def newmethod(*args, **kwargs):
		t = ascallparse(dkwargs)
		t.update(kwargs)
		return method(*args, **t)
	return newmethod

def adminpage(method):
    @wraps(method)
    def newmethod(*args, **kwargs):
        if session['isadmin'] == True:
            return method(*args, **kwargs)
        else:
            return redirect('/login')
    return newmethod
    
# No longer do we have to provide posts
render_template = None

app = None