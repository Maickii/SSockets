from ssockets import client

myclient = client("127.0.0.1", 60008, True, ".\client_keys.pem")
data = b"Hey, whats up server? it's me, the client talking!"
myclient.send(data)
