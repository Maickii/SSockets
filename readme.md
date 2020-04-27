# About
SSockets is a Python library that uses both the [Python Cryptography](https://cryptography.io/en/latest/ "Python Cryptography") library and the [Python Socket](https://docs.python.org/3/library/socket.html "Python Socket") library to simplify the work necessary to make successful secure transmissions of private data between hosts. The intent of this library is to give developers an easy to use tool for establishing a secure connection between hosts and ensuring that all communication between the hosts are encrypted.

## !!!Warning!!!
This library is for educational purposes only! For real use of encryption over a network please see [Python SSL](https://docs.python.org/3/library/ssl.html "Python SSL") library

# Getting Started
Clone Repo `git clone https://github.com/Maickii/SSockets.git`

Check out the  [TravisCI Instance](https://travis-ci.com/github/Maickii/SSockets "TravisCI Instance")

There are no building steps as this is a python library and does not need to be compiled. One can simply start coding by importing the library using `from ssockets import server` or `from ssockets import client`. It is important that `ssockets.py` is in your current working directory for the import to properly work. On future releases there may be an installer that takes care of making sure the import works without having `ssockets.py` in the corrent working directory.

See dependencies and usage to get started

# Linux dependencies
Most of the testing has been done on Ubuntu 18.04. Other Linux distributions may need additional dependencies

**Install Python3 & pip3**
```bash
sudo apt-get install python3
sudo apt-get install python3-pip
```
**Install Python's cryptography library**
```bash
sudo pip3 install cryptography
```
**Install tshark (CLI version of wireshark)**
```bash
sudo apt-get install tshark
```
# Usage
Open up two terminals and change your current working directory to the repo folder and then open up the interactive python shell using the command `python3`. In one terminal write up the server code and on the other type up the client code. Alternativily you can run the test `./tests/new_api/test.sh` which is the same as this example.

**Server proccess**
```python
from ssockets import server

myserver = server("127.0.0.1", 60000)
data = myserver.recv()
print("[SERVER] The client sent the following data: \"" + str(data, 'utf-8') + "\"")
```
**Client proccess**
```python
from ssockets import client

myclient = client("127.0.0.1", 60000)
data = b"Hey, whats up server? it's me, the client talking!"
print("[CLIENT] Sending the following data to the server: \"" + str(data, 'utf-8') + "\"")
myclient.send(data)
```
## Explanation
Both `from ssockets import server` and `from ssockets import client` import the neccesary library.
When `myserver = server("127.0.0.1", 60000)` is run it waits for an incomming connection on the loopback interface. For the client to establish a connection it must run `myclient = client("127.0.0.1", 60000)` on the same ip and port.

Once a connection is established, the client and the server perform a public key exchange, and each derive a shared key. Once the shared key has been generated `server()` and `client()` will return.

The server then runs `data = myserver.recv()`. Internally it waits for the client to send some encrypted data. Once it receives encrypted data, it will then decrypt the data using the shared key and return the data to the caller.

The client does the reverse proccess when it calls `myclient.send(data)`. It first encrypts the data using the shared key, and then it sends it to the server.
# Running tests
Run a simple test on legacy code. Root access is required for tshark.
```bash
sudo ./tests/legacy/test.sh
```
This test will perform the following actions
1. Spawn a server process in the background that will listen in for incoming connections on localhost (loopback interface) on port 60000
2. Start tshark on the background and scan all packet traffic going through the loopback interface
3. Start a client process that will attempt to communicate with the server process 2 times via the loopback interface.
    1. The first time the client communicates with the server, the client will send a plaintext string to make sure that we can successfully communicate with the server over the loopback interface and that tshark is capable of catching that plaintext string. The test fails if tshark does not catch the string
    1. The second time the client communicates with the server, the client will perform a public key exchange with the server, derive a shared key, and then encrypt the same plaintext string on part (i), and finally send the now encrypted string over to the server. tshark will inform it if it sees the same plaintext data. The test fails if tshark manages to catch the plaintext string
    
    
    
An alternative test can be invoked by running `./tests/new_api/test.sh`

# Bugs
You may run into errors such as `OSError: [Errno 98] Address already in use`. This is _probably_ due to the server not cleaning up properly on exit. If you do get this error just wait 5 minutes and try again. The kernel will clean up sometime after the process has exited. This is a known bug that we are trying to fix
