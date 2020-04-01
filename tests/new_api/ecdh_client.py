#!/usr/bin/env python3

import os, sys
sys.path.append(os.path.abspath('.'))
from ssockets import client

myclient = client("127.0.0.1", 60000, "ecdh")
cs_data = b"Hey, whats up server? it's me, the client talking. I'm using an elliptic curve key!"
print("[CLIENT] Sending the following data to the server: \"" + str(cs_data, 'utf-8') + "\"")
myclient.send(cdata)

cr_data = myclient.recv()
print("[CLIENT] The server sent the following data: \"" + str(cr_data, 'utf-8') + "\"")
