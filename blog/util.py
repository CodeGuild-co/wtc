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