#!/usr/bin/env python3
#lots of help came from:
#https://cryptography.io/en/latest/hazmat/primitives/asymmetric/ec/
#https://realpython.com/python-sockets/
#https://docs.python.org/3/library/socket.html#socket.socket.sendall
#https://cryptography.io/en/latest/hazmat/primitives/key-derivation-functions/
#https://cryptography.io/en/latest/hazmat/backends/interfaces/#cryptography.hazmat.backends.interfaces.EllipticCurveBackend
#https://cryptography.io/en/latest/_modules/cryptography/hazmat/backends/interfaces/#PEMSerializationBackend.load_pem_private_key
#https://www.tutorialspoint.com/How-to-write-binary-data-to-a-file-using-Python
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
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding

from pathlib import Path

class server:
	def __init__(self, host, port, load_key=None, key_path=None, alg="ecdh"):
		self.__host = host
		self.__port = port
		self.__alg = alg
		self.__socket = self.__bind_socket()
		try:
			self.__conn, self.__addr = self.__connect_to_client(self.__socket)
		except:
			print("SERVER: could not establish connection to the client, sec0")
			exit(1)
		if load_key is None:
			try:
				if alg == "ecdh": #elliptic curve key
					self.__server_private_key = ec.generate_private_key(ec.SECP384R1(), default_backend())
				elif alg == "rsa":
					self.__server_private_key = rsa.generate_private_key(public_exponent=65537, key_size=4096, backend=default_backend())
			except:
				print("SERVER: could not generate the private key, sec0")
				exit(1)
			try:
				self.serialized_private_key = self.__server_private_key.private_bytes(
					encoding=serialization.Encoding.PEM,
					format=serialization.PrivateFormat.PKCS8,
					encryption_algorithm=serialization.NoEncryption()
				)
			except:
				print("SERVER: could not serialize the private key, sec0")
				exit(1)
			try:
				self.__server_public_key = self.__server_private_key.public_key()
			except:
				print("SERVER: could not generate public key from private key, sec0")
				exit(1)
			try:
				self.serialized_public_key = self.__server_public_key.public_bytes(
					encoding=serialization.Encoding.PEM,
					format=serialization.PublicFormat.SubjectPublicKeyInfo
				)
			except:
				print("SERVER: could not serialize the public key, sec0")
				exit(1)
			try:
				self.__finish_server_connection()
			except:
				print("SERVER: could not finish establishing the connection to the client, sec0")
				exit(1)
		elif load_key is True:
			try:
				p = Path(key_path).exists()
			except:
				print("SERVER: invalid path specified for load_key, sec0")
				exit(1)
			try:
				loaded_public_key = serialization.load_pem_public_key(
					self.load_keys_from_file(key_path), 
	   				backend=default_backend()
				)
			except:
				print("SERVER: could not load the public key from file, sec0")
				exit(1)
			try:
				loaded_private_key = serialization.load_pem_private_key(
					self.load_keys_from_file(key_path),
					password=None,
			    	backend=default_backend()
			 	)
			except:
				print("SERVER: could not load the private key from file, sec0")
				exit(1)
			self.__server_private_key = loaded_private_key
			self.__server_public_key = loaded_public_key
			try:
				self.__finish_server_connection()
			except:
				print("SERVER: could not finish establishing connection to the client, sec0")
				exit(1)

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

	def recv(self, raw=False):
		try:
			encrypted_message = self.__conn.recv(1024*4)
		except:
			print("SERVER recv: could not receive message from client, sec3")
			exit(1)
		if len(encrypted_message) == 0:
			return b''
		if raw:
			return encrypted_message
		if self.__alg == "ecdh":
			return self.__f.decrypt(encrypted_message)
		else: #if alg == rsa
			#cipher_pass = base64.b64decode(encrypted_message);
			return self.__server_private_key.decrypt(encrypted_message,
					padding.OAEP(
					mgf=padding.MGF1(algorithm=hashes.SHA512()),
					algorithm=hashes.SHA512(),
					label=None)
			)

	def send(self, message, use_encryption_flag_____do_not_set_to_false_unless_you_know_what_you_are_doing=True): #message must be a byte string, otherwise encrypt will fail
		if not use_encryption_flag_____do_not_set_to_false_unless_you_know_what_you_are_doing:
			self.__conn.sendall(message)
			return
		try:
			if self.__alg == "ecdh":
				encrypted_data = self.__f.encrypt(message) #TODO if message message is not a byte string either fail gracefully or try to convert it to a byte string
			elif self.__alg == "rsa":
				encrypted_data = self.__server_public_key.encrypt(message, padding.OAEP(
						mgf=padding.MGF1(algorithm=hashes.SHA512()),
						algorithm=hashes.SHA512(),
						label=None)
				)
			self.__conn.sendall(encrypted_data)
		except:
			print("SERVER send: could not send message to client, sec3")
			exit(1)

	def load_keys_from_file(self, path):
		try:
			p = Path(path).exists()
		except:
			print("SERVER: invalid path specified for load_key, sec0")
			exit(1)
		try:
			key_file_descriptor = open(path, "r+b")
		except:
			print("SERVER load_keys_from_file: could not open file for reading, sec4")
			exit(1)
		try:
			server_keys_lines = key_file_descriptor.readlines()
		except:
			print("SERVER load_keys_from_file: could not read file, sec4")
			exit(1)
		serial_bytes = None
		for i in range(len(server_keys_lines)):
			if serial_bytes is None:
				serial_bytes = server_keys_lines[i]
			else:
				serial_bytes = serial_bytes + server_keys_lines[i]
		key_file_descriptor.close()
		return serial_bytes

	def save_keys(self, path):
		try:
			p = Path(path).exists()
		except:
			print("SERVER: invalid path specified for load_key, sec0")
			exit(1)
		try:
			key_file_descriptor = open(path, "w+b")
		except:
			print("SERVER save_keys: could not open file, sec5")
			exit(1)
		try:
			key_file_descriptor.write(self.serialized_public_key)
			key_file_descriptor.write(self.serialized_private_key)
		except:
			print("SERVER save_keys: could not write to file, sec5")
			exit(1)
		key_file_descriptor.close()

	def __finish_server_connection(self):
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

class client:
	def __init__(self, host, port, load_key=None, key_path=None, alg="ecdh"):
		self.__host = host
		self.__port = port
		self.__alg = alg
		if load_key is None:
			try:
				if alg == "ecdh":
					self.__client_private_key = ec.generate_private_key(ec.SECP384R1(), default_backend())
				elif alg == "rsa":
					self.__client_private_key = rsa.generate_private_key(public_exponent=65537, key_size=4096, backend=default_backend())
			except:
				print("Client: could not generate private key, cec0")
				exit(1)
			try:
				self.serialized_private_key = self.__client_private_key.private_bytes(
					encoding=serialization.Encoding.PEM,
					format=serialization.PrivateFormat.PKCS8,
					encryption_algorithm=serialization.NoEncryption()
				)
			except:
				print("Client: could not serialize private key, cec0")
				exit(1)
			try:
				self.__client_public_key = self.__client_private_key.public_key()
			except:
				print("Client: could not generate public key, cec0")
				exit(1)
			try:
				self.serialized_public_key = self.__client_public_key.public_bytes(
					encoding=serialization.Encoding.PEM,
	    			format=serialization.PublicFormat.SubjectPublicKeyInfo
				)
			except:
				print("Client: could not serialize public key, cec0")
				exit(1)
			try:
				self.__finish_client_connection()
			except:
				print("Client: could not finish connection to the server, cec0")
				exit(1)
		elif load_key is True:
			try:
				p = Path(key_path).exists()
			except:
				print("SERVER: invalid path specified for load_key, cec0")
				exit(1)
			try:
				loaded_public_key = serialization.load_pem_public_key(
					self.load_keys_from_file(key_path),
	   				backend=default_backend()
				)
			except:
				print("Client: could not load public key from file, cec0")
				exit(1)
			try:
				loaded_private_key = serialization.load_pem_private_key(
					self.load_keys_from_file(key_path),
					password=None,
			    	backend=default_backend()
			 	)
			except:
				print("Client: could not load private key from file, cec0")
				exit(1)
			self.__client_public_key = loaded_public_key
			self.__client_private_key = loaded_private_key
			try:
				self.__finish_client_connection()
			except:
				print("Client: could not finish connection to the server, cec0")
				exit(1)

	def __connect_to_server(self):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((self.__host, self.__port))
		return s

	def __client_exchange_keys(self, connected_socket, public_key):
		client_public_key_bytes = public_key.public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)
		connected_socket.sendall(client_public_key_bytes)
		server_public_key_bytes = connected_socket.recv(1024*4)
		if not server_public_key_bytes:
			print("Could not read the server's public key, cec2")
			sys.exit(1)
		server_public_key = serialization.load_pem_public_key(server_public_key_bytes, backend=default_backend())
		return server_public_key

	def recv(self, raw=False):
		# Raw means dont decrypt data, just return it as is
		try:
			encrypted_message = self.__connected_socket.recv(1024*4)
		except:
			print("Client recv: could not receive message from server. cec3")
			exit(1)
		if len(encrypted_message) == 0:
			return b''
		if raw:
			return encrypted_message
		if self.__alg == "ecdh":
			return self.__f.decrypt(encrypted_message)
		elif self.__alg == "rsa":
			#cipher_pass = base64.b64decode(encrypted_message);
			return self.__client_private_key.decrypt(encrypted_message,
					padding.OAEP(
					mgf=padding.MGF1(algorithm=hashes.SHA512()),
					algorithm=hashes.SHA512(),
					label=None)
			)

	def send(self, message, use_encryption_flag_____do_not_set_to_false_unless_you_know_what_you_are_doing=True): #message must be a byte string, otherwise encrypt will fail
		if not use_encryption_flag_____do_not_set_to_false_unless_you_know_what_you_are_doing:
			self.__connected_socket.sendall(message)
			return
		try:
			if self.__alg == "ecdh":
				encrypted_data = self.__f.encrypt(message) #TODO if message message is not a byte string either fail gracefully or try to convert it to a byte string
			elif self.__alg == "rsa":
				encrypted_data = self.__client_public_key.encrypt(message, padding.OAEP(
						mgf=padding.MGF1(algorithm=hashes.SHA512()),
						algorithm=hashes.SHA512(),
						label=None)
				)
			self.__connected_socket.sendall(encrypted_data)
		except:
			print("Client send: could not send data to server, cec4")
			exit(1)

	def load_keys_from_file(self, path):
		try:
			p = Path(path).exists()
		except:
			print("SERVER: invalid path specified for load_key, cec0")
			exit(1)
		try:
			key_file_descriptor = open(path, "r+b")
		except:
			print("Client load_keys_from_file: could not open file for reading, cec5")
			exit(1)
		try:
			client_keys_lines = key_file_descriptor.readlines()
		except:
			print("Client load_keys_from_file: could not read file, cec5")
			exit(1)
		serial_bytes = None
		for i in range(len(client_keys_lines)):
			if serial_bytes is None:
				serial_bytes = client_keys_lines[i]
			else:
				serial_bytes = serial_bytes + client_keys_lines[i]
		key_file_descriptor.close()
		return serial_bytes

	def save_keys(self, path):
		try:
			p = Path(path).exists()
		except:
			print("SERVER: invalid path specified for load_key, cec0")
			exit(1)
		try:
			key_file_descriptor = open(path, "w+b")
		except:
			print("Client save_keys: could not open file for writing, cec6")
			exit(1)
		try:
			key_file_descriptor.write(self.serialized_public_key)
			key_file_descriptor.write(self.serialized_private_key)
		except:
			print("Client save_keys: could not write to file, cec6")
			exit(1)
		key_file_descriptor.close()

	def __finish_client_connection(self):
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
