import curse
import random
from time import sleep
##################################
#These 5 steps can be reduced to 1 once we have the import from anywhere working
import sys
import os
cwd = os.getcwd()
sys.path.append(cwd + '/../')
from ssockets import client
##################################

ready = False
myclient = None
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
		myclient.send(val, use_encryption_flag_____do_not_set_to_false_unless_you_know_what_you_are_doing=not raw)
		curse.q.put((False, val))

def get_sender_input():
	global ready
	global raw
	while ready is not True:
		pass
	while True:
		val = myclient.recv(raw=raw)
		curse.q.put((True, val))

def callback():
	global ready
	global myclient
	myclient = client("127.0.0.1", 60000)
	ready = True

curse.init(callback, (get_user_input, get_sender_input))
