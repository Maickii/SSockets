from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

server_private_key = ec.generate_private_key(ec.SECP384R1(), default_backend())
serialized_public = server_private_key.public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)

print(serialized_public)

print("")
print("")

#print(serialized_public.splitlines())

print("")
print("")

utf8_based_public_key = serialized_public.decode('UTF-8')

print(utf8_based_public_key)

byte_based_public_key = utf8_based_public_key.encode('UTF-8')

print(byte_based_public_key)

loaded_public_key = serialization.load_pem_public_key(byte_based_public_key, backend=default_backend())

print(loaded_public_key.public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo))
