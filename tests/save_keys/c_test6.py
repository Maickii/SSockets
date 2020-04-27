from ssockets import client

myclient = client("127.0.0.1", 60010, True)
data = b"Hey, whats up server? it's me, the client talking!"
myclient.send(data)
