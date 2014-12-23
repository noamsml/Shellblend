import shellblend

def c(cmd):
	return shellblend.PipedCommand().pipe(cmd)

def s(st):
	return shellblend.PipedCommand().string(st)

def f(fn):
	return shellblend.PipedCommand().from_file(fn)