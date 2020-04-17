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


class server:
	# have_public_private_keys
	#	type: boolean
	#	purpose: do you have server keys saved to file?
	#save_keys
	#	type: boolean
	#	purpose: do you want to save keys to file?
	#default configuration: no previous keys saved, do not save keys to file
	def __init__(self, host, port, have_public_private_keys=False, save_keys=False, alg="ecdh"):
		self.__host = host
		self.__port = port
		self.__alg = alg
		self.__socket = self.__bind_socket()
		self.__conn, self.__addr = self.__connect_to_client(self.__socket)
		if have_public_private_keys is False and save_keys is False: #case keys need to be generated but not saved
			if alg == "ecdh": #elliptic curve key
				self.__server_private_key = ec.generate_private_key(ec.SECP384R1(), default_backend())
			elif alg == "rsa":
				self.__server_private_key = rsa.generate_private_key(public_exponent=65537, key_size=4096, backend=default_backend())
			self.__server_public_key = self.__server_private_key.public_key()
			self.__finish_server_connection()
		elif have_public_private_keys is False and save_keys is True: #case where keys need to be generated and saved
			if alg == "ecdh": #elliptic curve key
				self.__server_private_key = ec.generate_private_key(ec.SECP384R1(), default_backend())
			elif alg == "rsa":
				self.__server_private_key = rsa.generate_private_key(public_exponent=65537, key_size=4096, backend=default_backend())
			self.__server_public_key = self.__server_private_key.public_key()
			#end of key generation
			serialized_private_key = self.__server_private_key.private_bytes(
				encoding=serialization.Encoding.PEM,
				format=serialization.PrivateFormat.PKCS8,
				encryption_algorithm=serialization.BestAvailableEncryption(b'testpassword')
			)
			serialized_public_key = self.__server_public_key.public_bytes(
				encoding=serialization.Encoding.PEM,
				format=serialization.PublicFormat.SubjectPublicKeyInfo
			)
			self.__finish_server_connection()
			#open server key file, if does not exist, then create
			key_file_descriptor = open("server_keys.pem", "w+b")
			key_file_descriptor.write(serialized_public_key)
			key_file_descriptor.write(serialized_private_key)
			key_file_descriptor.close()
		elif have_public_private_keys is True and save_keys is False:
			key_file_descriptor = open("server_keys.pem", "r+b")
			server_keys_lines = key_file_descriptor.readlines()
			retrieved_public_key = None
			retrieved_private_key = None
			flag = 0
			for i in range(len(server_keys_lines)):
				if b"BEGIN ENCRYPTED PRIVATE" in server_keys_lines[i]:
					flag = 1
				if flag == 1:
					if retrieved_private_key is None:
				 		retrieved_private_key = server_keys_lines[i]
					else:
						retrieved_private_key = retrieved_private_key + server_keys_lines[i]
				if flag == 0:
					if retrieved_public_key is None:
				 		retrieved_public_key = server_keys_lines[i]
					else:
						retrieved_public_key = retrieved_public_key + server_keys_lines[i]
			key_file_descriptor.close()
			loaded_public_key = serialization.load_pem_public_key(
				retrieved_public_key,
   				backend=default_backend()
			)
			loaded_private_key = serialization.load_pem_private_key(
				retrieved_private_key,
		   		password=b'testpassword',
		    	backend=default_backend()
		 	)
			self.__server_private_key = loaded_private_key
			self.__server_public_key = loaded_public_key

			self.__finish_server_connection()
	# end def __init__

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

	def send(self, message): #message must be a byte string, otherwise encrypt will fail
		if self.__alg == "ecdh":
			encrypted_data = self.__f.encrypt(message) #TODO if message message is not a byte string either fail gracefully or try to convert it to a byte string
		elif self.__alg == "rsa":
			encrypted_data = self.__server_public_key.encrypt(message, padding.OAEP(
					mgf=padding.MGF1(algorithm=hashes.SHA512()),
					algorithm=hashes.SHA512(),
					label=None)
			)
		self.__conn.sendall(encrypted_data)

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
	def __init__(self, host, port, have_public_private_keys=False, save_keys=False, alg="ecdh"): #have_public_private_keys
		self.__host = host
		self.__port = port
		self.__alg = alg
		if have_public_private_keys is False and save_keys is False: #case generate keys and not save
			if alg == "ecdh":
				self.__client_private_key = ec.generate_private_key(ec.SECP384R1(), default_backend())
			elif alg == "rsa":
				self.__client_private_key = rsa.generate_private_key(public_exponent=65537, key_size=4096, backend=default_backend())
			self.__client_public_key = self.__client_private_key.public_key()
			self.__finish_client_connection()
		elif have_public_private_keys is False and save_keys is True: #case generate and save
			if alg == "ecdh":
				self.__client_private_key = ec.generate_private_key(ec.SECP384R1(), default_backend())
			elif alg == "rsa":
				self.__client_private_key = rsa.generate_private_key(public_exponent=65537, key_size=4096, backend=default_backend())
			serialized_private_key = self.__client_private_key.private_bytes(
				encoding=serialization.Encoding.PEM,
				format=serialization.PrivateFormat.PKCS8,
				encryption_algorithm=serialization.BestAvailableEncryption(b'testpassword')
			)
			self.__client_public_key = self.__client_private_key.public_key()
			serialized_public_key = self.__client_public_key.public_bytes(
				encoding=serialization.Encoding.PEM,
    			format=serialization.PublicFormat.SubjectPublicKeyInfo
			)
			self.__finish_client_connection()
			key_file_descriptor = open("client_keys.pem", "w+b")
			key_file_descriptor.write(serialized_public_key)
			key_file_descriptor.write(serialized_private_key)
			key_file_descriptor.close()
		elif have_public_private_keys is True and save_keys is False:
			key_file_descriptor = open("client_keys.pem", "r+b")
			client_keys_lines = key_file_descriptor.readlines()
			retrieved_public_key = None
			retrieved_private_key = None
			flag = 0
			for i in range(len(client_keys_lines)):
				if b"BEGIN ENCRYPTED PRIVATE" in client_keys_lines[i]:
					flag = 1
				if flag == 1:
					if retrieved_private_key is None:
				 		retrieved_private_key = client_keys_lines[i]
					else:
						retrieved_private_key = retrieved_private_key + client_keys_lines[i]
				if flag == 0:
					if retrieved_public_key is None:
				 		retrieved_public_key = client_keys_lines[i]
					else:
						retrieved_public_key = retrieved_public_key + client_keys_lines[i]
			key_file_descriptor.close()
			loaded_public_key = serialization.load_pem_public_key(
				retrieved_public_key,
   				backend=default_backend()
			)
			loaded_private_key = serialization.load_pem_private_key(
				retrieved_private_key,
		   		password=b'testpassword',
		    	backend=default_backend()
		 	)
			self.__client_public_key = loaded_public_key
			self.__client_private_key = loaded_private_key
			self.__finish_client_connection()
	# end def __init__

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

	def send(self, message): #message must be a byte string, otherwise encrypt will fail
		if self.__alg == "ecdh":
			encrypted_data = self.__f.encrypt(message) #TODO if message message is not a byte string either fail gracefully or try to convert it to a byte string
		elif self.__alg == "rsa":
			encrypted_data = self.__client_public_key.encrypt(message, padding.OAEP(
					mgf=padding.MGF1(algorithm=hashes.SHA512()),
					algorithm=hashes.SHA512(),
					label=None)
			)
		self.__connected_socket.sendall(encrypted_data)

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
