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

class server:
	def __init__(self, host, port):
		self.__host = host
		self.__port = port
		self.__server_private_key = ec.generate_private_key(ec.SECP384R1(), default_backend())
		self.__server_public_key = self.__server_private_key.public_key()
		self.__socket = self.__bind_socket()
		self.__conn, self.__addr = self.__connect_to_client(self.__socket)
		self.__client_public_key = self.__server_exchange_keys(self.__conn, self.__server_public_key)
		if self.__client_public_key:
			#we have the child's public key. now we can perform the exchange and ready to receive encrypted data
			self.__shared_key = self.__server_private_key.exchange(ec.ECDH(), self.__client_public_key)
		self.__derived_key = HKDF(
			algorithm=hashes.SHA256(),
			length=32,
			salt=None,
			info=b'handshake data',
			backend=default_backend()
		).derive(self.__shared_key)
		self.__f = Fernet(base64.urlsafe_b64encode(self.__derived_key))

	def __bind_socket(self):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.bind((self.__host, self.__port))
		return s

	def __connect_to_client(self, bound_socket):
		bound_socket.listen()
		return bound_socket.accept()

	def __server_exchange_keys(self, conn, public_key):
		client_public_key_bytes = conn.recv(1024*4)
		try:
			client_public_key = serialization.load_pem_public_key(client_public_key_bytes, backend=default_backend())
		except:
			print("SERVER: Could not serialize client's public key. perhaps that was not a key")
			return None
		server_public_key_bytes = public_key.public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)
		conn.sendall(server_public_key_bytes)
		return client_public_key

	def recv(self):
		encrypted_message = self.__conn.recv(1024*4)
		return self.__f.decrypt(encrypted_message)

	def send(self, message): #message must be a byte string, otherwise encrypt will fail
		encrypted_data = self.__f.encrypt(message) #TODO if message message is not a byte string either fail gracefully or try to convert it to a byte string
		self.__conn.sendall(encrypted_data)

class client:
	def __init__(self, host, port, alg = ecdh):
		self.__host = host
		self.__port = port
		# Elliptic curve Diffie-Hellman (default)
		if alg == ecdh:
			self.__client_private_key = ec.generate_private_key(ec.SECP384R1(), default_backend())
			self.__client_public_key = self.__client_private_key.public_key()
			self.__connected_socket = self.__connect_to_server()
			self.__server_public_key = self.__client_exchange_keys(self.__connected_socket, self.__client_public_key)
			if self.__server_public_key:
				self.__shared_key = self.__client_private_key.exchange(ec.ECDH(), self.__server_public_key)
				self.__derived_key = HKDF(
					algorithm=hashes.SHA256(),
					length=32,
					salt=None,
					info=b'handshake data',
					backend=default_backend()
				).derive(self.__shared_key)
				self.__f = Fernet(base64.urlsafe_b64encode(self.__derived_key))
			else:
				print("could not retrieve the server's public key") #TODO throw an exception
		# RSA encryption
		elif alg == rsa:
			self.__client_private_key = rsa.generate_private_key(public exponent = 65537, key_size = 2048, backend = default_backend())
			self.__client_public_key = self.__client_private_key.public_key()
			self.__connected_socket = self.__connect_to_server()
			self.__server_public_key = self.__client_excahnge_keys(self.__connected_socket, self.__client_public_key)
	#end of def __init__
			

	def __connect_to_server(self):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((self.__host, self.__port))
		return s

	def __client_exchange_keys(self, connected_socket, public_key):
		client_public_key_bytes = public_key.public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)
		connected_socket.sendall(client_public_key_bytes)
		server_public_key_bytes = connected_socket.recv(1024*4)
		if not server_public_key_bytes:
			print("Could not read the servers public key")
			sys.exit(1)
		server_public_key = serialization.load_pem_public_key(server_public_key_bytes, backend=default_backend())
		return server_public_key

	def recv(self):
		encrypted_message = self.__connected_socket.recv(1024*4)
		return self.__f.decrypt(encrypted_message)

	def send(self, message): #message must be a byte string, otherwise encrypt will fail
		encrypted_data = self.__f.encrypt(message) #TODO if message message is not a byte string either fail gracefully or try to convert it to a byte string
		self.__connected_socket.sendall(encrypted_data)

