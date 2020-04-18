import curse
import sys
from ssockets import server

ready = False
myserver = None
raw = False

if len(sys.argv) == 2:
	if sys.argv[1] == 'raw':
		raw = True
	else:
		print("usage: " + sys.argv[0] + " [raw]")
		sys.exit(0)

def get_user_input(in_box):
	global ready
	global raw
	while ready is not True:
		pass
	while True:
		val = in_box.getstr(0, len(curse.prompt))
		curse.clear_prompt(in_box)
		myserver.send(val, use_encryption_flag_____do_not_set_to_false_unless_you_know_what_you_are_doing=not raw)
		curse.q.put((False, val))

def get_sender_input():
	global ready
	global raw
	while ready is not True:
		pass
	while True:
		val = myserver.recv(raw=raw)
		curse.q.put((True, val))

def callback():
	global ready
	global myserver
	myserver = server("127.0.0.1", 60000)
	ready = True

curse.init(callback, (get_user_input, get_sender_input))
