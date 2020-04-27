from ssockets import server

myserver = server("127.0.0.1", 60005)
data = myserver.recv()
