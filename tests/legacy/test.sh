#!/bin/bash

run_test () { # <encrypted|plain> <message>
	python3 server.py > /dev/null &
	pid=$!
	sleep 1
	tshark -i lo -Y 'tcp.flags.push == 1 and tcp.flags.ack == 1' -T fields -e data -a duration:3 > out.txt &
	sleep 1
	python3 client.py "$1" "$2" > /dev/null
	sleep 4

	kill -9 "$pid"

	python3 -u hex_to_ascii.py | tee /dev/tty | grep -q "$2"
} 2> /dev/null

string="Arrays start at 0. Anyone who disagrees is practising heresy and must be punished at the stake."

test_num=1

debug_test () {
	echo "======================================================================================   Running test ($test_num/2)  ======================================================================================"
	echo "Sending the following marker string to server (using $1): \"$string\"."
	echo ""
	echo "START WIRESHARK OUTPUT"
	run_test $1 "$string"
	stat=$?
	echo "END WIRESHARK OUTPUT"
	echo ""
	if [ $stat -eq 0 ]
	then
		if [ "$1" == "plain" ]
		then
			echo "Succesfully found the marker string in the plaintext communication between the client and server"
		elif [ "$1" == "encrypted" ]
		then
			echo "Somehow found the marker string in the encrypted communication between the client and server. !THIS MUST BE AN ERROR!"
		fi
	elif [ $stat -eq 1 ]
	then
		if [ "$1" == "plain" ]
		then
			echo "Could not find the marker string in the plaintext communication between the client and server. This is an error. Something went wrong."
		elif [ "$1" == "encrypted" ]
		then
			echo "As expected, could not find the marker string in the encrypted communication between the client and server."
		fi
	fi
	echo "======================================================================================   Done running test ($test_num/2)  =================================================================================="
	test_num=$((test_num+1))
	return $stat
}

cd tests/legacy/

debug_test plain && echo -en "\n\n\n\n" && ! debug_test encrypted
