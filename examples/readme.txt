This example demonstrates the ease of use of ssockets. All one needs to do is stablish a connetion between two hosts, just like bad_guy1 and bad_guy2 do using the server() and client() functions. after that it's all matter of calling send()/recv() functions.

To run this example you are going to need 3 terminals. one for bad_guy1, another for bad_guy2, and a third for the fbi trying to catch these bad guys. 
on each terminal naviate to the examples directory. on one of the terminals run the fbi script as root. on a separete terminal run bad_guy1 by `python3 bad_guy1.py raw`. same with bad_guy2, but on the third terminal
IT must be done in this order, otherwise it will not work.

wait a few seconds for the bad guys to connect. you will know when they have connected when the fbi terminal shows their public keys. once you see that the keys have been exchanged you can start typing on either of the bad guys.
the blinking cursor has been disabled, but you can still type. once you are ready to send your message press enter.

it will send your message to the other bad guy. if you used the 'raw' flag the fbi will be able to see the what the bad guys are sending to each other. to correctly exit you must first exit bad_guy2 and then bad_guy1 in that order. otherwise you will get an error and have to wait a couple seconds before you can reconnect (this is a bug).

start up the bad guys again, but this time without the raw flag. This time the fbi cant figure out what it is that you are sending to each other
