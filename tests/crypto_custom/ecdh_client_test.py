#!/usr/bin/env python3

from ssockets import client

myclient = client("127.0.0.1", 65001, alg="ecdh")
data = b"It's me, the client talking, I'm using a elipitic curve key!"
print("[CLIENT] Sending the following data to the server: \"" + str(data, 'utf-8') + "\"")
myclient.send(data)
data = myclient.recv()
print("[CLIENT] The server sent the following data: \"" + str(data, 'utf-8') + "\"")

