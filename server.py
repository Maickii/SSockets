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
PORT = 60000        # Port to listen on (non-privileged ports are > 1023)

def bind_socket():
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((HOST, PORT))
	return s
	
def connect_to_client(bound_socket):
	bound_socket.listen()
	return bound_socket.accept()

def server_exchange_keys(conn, public_key):
	client_public_key_bytes = conn.recv(1024*4)
	print("SERVER: received the following public key")
	print(client_public_key_bytes)
	client_public_key = serialization.load_pem_public_key(client_public_key_bytes, backend=default_backend())
	server_public_key_bytes = public_key.public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)
	print("SERVER: public key about to be sent")
	print(server_public_key_bytes)
	conn.sendall(server_public_key_bytes)
	return client_public_key

def server():
	server_private_key = ec.generate_private_key(ec.SECP384R1(), default_backend())
	server_public_key = server_private_key.public_key()
	socket = bind_socket()
	while True:
		conn, addr = connect_to_client(socket)
		client_public_key = server_exchange_keys(conn, server_public_key)
		if client_public_key:
			#print(client_public_key) # should print something like <cryptography.hazmat.backends.openssl.ec._EllipticCurvePublicKey object at 0x7fc9d9d62550>
			#we have the child's public key. now we can perform the exchange and ready to receive encrypted data
			shared_key = server_private_key.exchange(ec.ECDH(), client_public_key)
			derived_key = HKDF(
				algorithm=hashes.SHA256(),
				length=32,
				salt=None,
				info=b'handshake data',
				backend=default_backend()
			).derive(shared_key)
			f = Fernet(base64.urlsafe_b64encode(derived_key))
			encrypted_message = conn.recv(1024*4)
			print("SERVER: the client sent the following encrypted message:")
			print(encrypted_message)
			print("SERVER: here is the same message, now decryted")
			print(f.decrypt(encrypted_message))

server()
