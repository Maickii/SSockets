from ssockets import client

myclient = client("127.0.0.1", 60000, False, False)
data = b"Hey, whats up server? it's me, the client talking!"
print("[CLIENT] Sending the following data to the server: \"" + str(data, 'utf-8') + "\"")
myclient.send(data)
