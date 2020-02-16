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

def connect_to_server():
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((HOST, PORT))
	return s

def client_exchange_keys(connected_socket, public_key):
	client_public_key_bytes = public_key.public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)
	print("CLIENT: about to send the following public key:")
	print(client_public_key_bytes)
	connected_socket.sendall(client_public_key_bytes)
	server_public_key_bytes = connected_socket.recv(1024*4)
	if not server_public_key_bytes:
		print("Could not read the servers public key")
		sys.exit(1)
	print("CLIENT: received the following public key")
	print(server_public_key_bytes)
	server_public_key = serialization.load_pem_public_key(server_public_key_bytes, backend=default_backend())
	return server_public_key

def client():
	client_private_key = ec.generate_private_key(ec.SECP384R1(), default_backend())
	client_public_key = client_private_key.public_key()
	connected_socket = connect_to_server()
	server_public_key = client_exchange_keys(connected_socket, client_public_key)
	if server_public_key:
		shared_key = client_private_key.exchange(ec.ECDH(), server_public_key)
		derived_key = HKDF(
			algorithm=hashes.SHA256(),
			length=32,
			salt=None,
			info=b'handshake data',
			backend=default_backend()
		).derive(shared_key)
		f = Fernet(base64.urlsafe_b64encode(derived_key))
		encrypted_data = f.encrypt(b"arrays start at 0. anyone who disagrees is a heretic.")
		connected_socket.sendall(encrypted_data)


client()
