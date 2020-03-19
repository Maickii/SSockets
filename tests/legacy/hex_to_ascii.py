import binascii
import sys

#string = open(sys.argv[1],'r').read()
#sys.stdout.write(binascii.unhexlify(string))

file1 = open('out.txt', 'r') 
while True: 
	line = file1.readline() 
	if not line: 
		break
	#print(line)
	print(str(binascii.unhexlify(line.strip()), 'utf-8'))

file1.close() 
