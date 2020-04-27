#!/usr/bin/env python3

from ssockets import server

myserver = server("127.0.0.1", 60000)
data = myserver.recv()
print("[SERVER] The client sent the following data: \"" + str(data, 'utf-8') + "\"")
data = b"Hey, whats up client? it's me, the server talking!"
print("[SERVER] Sending the following data to the client: \"" + str(data, 'utf-8') + "\"")
myserver.send(data)
