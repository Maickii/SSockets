#!/usr/bin/env python3

import os
import sys
import socket
from time import sleep

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)

#parent proccess will listen for data sent by the child through the socket.
#Once the data has been read the parent proccess will terminate
def parent_proc():
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		s.bind((HOST, PORT))
		s.listen()
		print("PARENT: listening for host")
		conn, addr = s.accept()
		if conn:
			print('PARENT: Connected by', addr)
		while conn:
			while True:
				data = conn.recv(1024*4)
				if not data:
					break
				print("PARENT received data: [", end="")
				print(data, end="")
				print("]")

def child_proc():
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		s.connect((HOST, PORT))
		i = 0
		while True:
			print("CHILD sending data")
			s.sendall(('Hello, world'+str(i)).encode('UTF-8'))
			i = i + 1
			sleep(1)
		#data = s.recv(1024)
		sys.exit(0)

pid = os.fork()
if pid < 0:
	print("Error, could not fork child")
	sys.exit(0)
elif pid == 0: #child
	while True:
		child_proc()
else:
	while True:
		parent_proc()
