#About
SSockets is a Python library that uses both the [Python Cryptography](https://cryptography.io/en/latest/ "Python Cryptography") library and the [Python Socket](https://docs.python.org/3/library/socket.html "Python Socket") library to simplify the work necessary to make successful secure transmissions of private data between hosts. The intent of this library is to give developers an easy to use tool for establishing a secure connection between hosts and ensuring that all communication between the hosts are encrypted.

##!!!Warning!!!
This library is for educational purposes only! For real use of encryption over a network please see [Python SSL](https://docs.python.org/3/library/ssl.html "Python SSL") library

#Getting Started
Clone Repo `git clone https://github.com/Maickii/SSockets.git`
Check out the  [TravisCI Instance](https://travis-ci.com/github/Maickii/SSockets "TravisCI Instance")

#Linux dependencies:
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
#Running tests
Run a simple test on legacy code. Root access is required for tshark.
```bash
sudo ./tests/legacy/test.sh
```
This test will perform the following actions
1. Spawn a server proccess in the background that will listen in for incoming connections on localhost (loopback interface) on port 60000
2. Start tshark on the background and scan all packet traffic going through the loopback interface
3. Start a client process that will attempt to comunicate with the server process 2 ttimes via the loopback interface.
	a. The first time the client communicates with the server, the client will send a plaintext string to make sure that we can succesfully communicate with the server over the loopback interface and that tshark is capable of catching that plaintext string. The test fails if tshark does not catch the string
	b. The second time the client communicates with the server, the client will perform a public key exchange with the server, derive a shared key, and then encrypt the same plaintext string on part a, and finally send the now encrypted string over to the server. tshark will inform if it sees the same plaintext data. The test fails if tshark manages to catch the plaintext string
