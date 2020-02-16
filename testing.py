#!/usr/bin/env python3

#lots of help came from:
#https://cryptography.io/en/latest/hazmat/primitives/asymmetric/ec/
#https://realpython.com/python-sockets/
#https://docs.python.org/3/library/socket.html#socket.socket.sendall
import os
import sys
import socket
import base64
import random
from time import sleep
from base64 import b64encode

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = random.randint(2000, 60000)        # Port to listen on (non-privileged ports are > 1023)

def receive_public_key():
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		s.bind((HOST, PORT))
		s.listen()
		conn, addr = s.accept()
		if conn:
			child_public_key_bytes = conn.recv(1024*4)
			child_public_key = serialization.load_pem_public_key(child_public_key_bytes, backend=default_backend())
			return child_public_key

def send_public_key(public_key):
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		s.connect((HOST, PORT))
		child_public_key_bytes = public_key.public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)
		s.sendall(child_public_key_bytes)

def server():
	server_private_key = ec.generate_private_key(ec.SECP384R1(), default_backend())
	server_public_key = server_private_key.public_key()
	client_public_key = receive_public_key()
	send_public_key(server_public_key)
	
	if child_public_key:
		print(child_public_key) # should print something like <cryptography.hazmat.backends.openssl.ec._EllipticCurvePublicKey object at 0x7fc9d9d62550>
		#we have the child's public key. now we can perform the exchange and ready to receive encrypted data
		shared_key = parent_private_key.exchange(ec.ECDH(), child_public_key)
		derived_key = HKDF(
			algorithm=hashes.SHA256(),
			length=32,
			salt=None,
			info=b'handshake data',
			backend=default_backend()
		).derive(shared_key)
		print(derived_key)
		f = Fernet(base64.urlsafe_b64encode(derived_key))
		encrypted_data = f.encrypt(b"my deep dark secret")
		print(encrypted_data)
		print(f.decrypt(encrypted_data))

def client():
	client_private_key = ec.generate_private_key(ec.SECP384R1(), default_backend())
	client_public_key = client_private_key.public_key()
	send_public_key(client_public_key)
	server_public_key = receive_public_key()

pid = os.fork()
if pid < 0:
	print("Error, could not fork child")
	sys.exit(0)
elif pid == 0: #child
	client()
else:
	sleep(1)
	server()
