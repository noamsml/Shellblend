import subprocess
import sys
import os

BUFSIZE=1024

def fdwrite(fd, outstr):
	total_len = len(outstr)
	while total_len:
		result = os.write(fd, outstr)
		if result < 0: raise Exception
		total_len -= result
		outstr = outstr[result:]

class PipeHandler(object):
	def run_real(self, pipe_in, pipe_out, pipe_err=None):
		self.run(pipe_in, pipe_out, pipe_err)
	def wait_done():
		return None

class CommandPipeHandler(PipeHandler):
	def __init__(self, cmd):
		self.cmd = cmd
	def run(self, pipe_in, pipe_out, pipe_err):
		args = { "stdin" : pipe_in, "stdout" : pipe_out }
		if pipe_err:
			args["stderr"] = pipe_err
		if type(self.cmd) == str:
			args["shell"] = True
		self.process = subprocess.Popen(self.cmd, **args)
	def wait_done(self):
		return self.process.wait()

class ToStringPipeHandler(PipeHandler):
	def __init__(self):
		pass
	def run(self, pipe_in, pipe_out, pipe_err):
		self.pipe_in = pipe_in
	def wait_done(self):
		file_in = os.fdopen(self.pipe_in)
		rval = file_in.read().strip()
		file_in.close()
		return rval

class OutputToFilePipeHandler(PipeHandler):
	def __init__(self, filename, append):
		self.filename = filename
		self.append = append
	def run(self, pipe_in, pipe_out, pipe_err):
		self.pipe_in = pipe_in
	def wait_done(self):
		# TODO(noamsml): Optimize this with buffering
		if self.append:
			mode = "a"
		else:
			mode = "w"
		file_out = open(self.filename, mode)
		while True:
			buf = os.read(self.pipe_in, BUFSIZE)
			if not buf: break
			file_out.write(buf)
		file_out.close()
		return None

# This one is a bit of a mess
class InputFromFilePipeHandler(PipeHandler):
	def __init__(self, filename):
		self.filename = filename
	def run(self, pipe_in, pipe_out, pipe_err):
		child_pid = os.fork()
		if child_pid: # in parent
			self.child_pid = child_pid
		else: # in child
			file_in = open(self.filename)
			while True:
				buf = file_in.read(BUFSIZE)
				if not buf: break
				fdwrite(pipe_out, buf)
			os.close(pipe_out)
			sys.exit(0)
	def wait_done(self):
		os.waitpid(self.child_pid, 0)
		return None


class OutputStringPipeHandler(PipeHandler):
	def __init__(self, string):
		self.string = string
	def run(self, pipe_in, pipe_out, pipe_err):
		fdwrite(pipe_out, self.string)
	def wait_done(self):
		return self.string;

class OutputToDevNullPipeHandler(PipeHandler):
	def __init__(self):
		pass
	def run(self, pipe_in, pipe_out, pipe_err):
		pass
	def wait_done(self):
		return None

class CommandWrapper(object):
	def __init__(self, handler):
		self.handler = handler
		self.pipe_stderr = False
		self.pipe_to_close = None
	def do_pipe_stderr(self):
		self.pipe_stderr = True
	def run(self, pipe_in, pipe_out):
		if self.pipe_stderr:
			pipe_err = pipe_out
		else:
			pipe_err = None
		self.handler.run(pipe_in, pipe_out, pipe_err)
	def wait_done(self):
		return self.handler.wait_done()

class PipedCommand(object):
	def __init__(self):
		self.commands = []

	def string(self, s):
		return self.pipe(OutputStringPipeHandler(s))

	def pipe(self, cmd):
		if type(cmd) in [str, list]:
			cmd = CommandPipeHandler(cmd)
		self.commands.append(CommandWrapper(cmd))
		return self

	def start(self):
		pipe_in = sys.stdin.fileno()
		for cmd in self.commands[:-1]:
			read_end,write_end = os.pipe()
			cmd.run(pipe_in,write_end)
			os.close(write_end)
			pipe_in = read_end
		self.commands[-1].run(pipe_in,sys.stdout.fileno())

	def wait(self):
		value = None
		for cmd in self.commands:
			new_value = cmd.wait_done()
			if new_value != None: value = new_value
		return value

	def run(self):
		self.start()
		return self.wait()

	def to_stdout(self):
		return run()

	def to_dev_null(self):
		self.pipe(OutputToDevNullPipeHandler())
		return self.run()

	def to_string(self):
		self.pipe(ToStringPipeHandler())
		return self.run()

	def to_file(self, filename):
		self.pipe(OutputToFilePipeHandler(filename, False))
		return self.run()

	def append(self, filename):
		self.pipe(OutputToFilePipeHandler(filename, True))
		return self.run()

	def from_file(self, filename):
		return self.pipe(InputFromFilePipeHandler(filename))

	def p(self, cmd):
		return self.pipe(cmd)

	def c(self, cmd):
		return self.pipe(cmd)

	def r(self):
		return self.run()
