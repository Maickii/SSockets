#!/usr/bin/env python3

import os
import sys
import socket
from time import sleep

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)

#parent proccess will listen for data sent by the child through the socket.
#Once the data has been read the parent proccess will terminate
def parent_proc():
	parent_private_key = ec.generate_private_key(ec.SECP384R1(), default_backend())
	#parent_public_key = parent_private_key.public_key() #parent public key is not needed as we do not want to send data to the child
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
	child_private_key = ec.generate_private_key(ec.SECP384R1(), default_backend())
	child_public_key = child_private_key.public_key()
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		s.connect((HOST, PORT))
		print("CHILD attempting to send public key")
		child_public_key_bytes = child_public_key.public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)
		s.sendall(child_public_key_bytes)
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
