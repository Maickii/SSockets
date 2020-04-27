from ssockets import server

myserver = server("127.0.0.1", 60007, True, "./server_keys.pem")
data = myserver.recv()
