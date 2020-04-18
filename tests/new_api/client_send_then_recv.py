#!/usr/bin/env python3

import os, sys
sys.path.append(os.path.abspath('.'))
from ssockets import client

myclient = client("127.0.0.1", 60000)
print(dir(myclient))
data = b"Hey, whats up server? it's me, the client talking!"
print("[CLIENT] Sending the following data to the server: \"" + str(data, 'utf-8') + "\"")
myclient.send(data)
data = myclient.recv()
print("[CLIENT] The server sent the following data: \"" + str(data, 'utf-8') + "\"")
