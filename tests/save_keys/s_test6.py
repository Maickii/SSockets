from ssockets import server

myserver = server("127.0.0.1", 60010, True)
data = myserver.recv()
