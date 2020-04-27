from ssockets import server

myserver = server("127.0.0.1", 60006)
data = myserver.recv()
myserver.save_keys("./server_keys.pem")
