#!/bin/bash

saved_cwd="$(pwd)/"
for i in `ls -d */`
do
	cd "$saved_cwd$i"
	./test.sh
done
