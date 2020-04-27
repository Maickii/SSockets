#!/usr/bin/env python3

from ssockets import server

myserver = server("127.0.0.1", 65001, alg="ecdh")
data = myserver.recv()
print("[SERVER] The client sent the following data: \"" + str(data, 'utf-8') + "\"")
data = b"It's me, the server talking, I'm using an ellipitc curve key!"
print("[SERVER] Sending the following data to the client: \"" + str(data, 'utf-8') + "\"")
myserver.send(data)
