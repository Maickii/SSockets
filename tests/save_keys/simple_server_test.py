from ssockets import server

myserver = server("127.0.0.1", 60000, False, False)
data = myserver.recv()
print("[SERVER] The client sent the following data: \"" + str(data, 'utf-8') + "\"")
