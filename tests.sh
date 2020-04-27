#!/bin/sh

touch output_server.txt
touch output_client.txt

s0errors(){
  SE0=$(grep -c "sec0" output_server.txt)
  echo $SE0
}

s1errors(){
  SE1=$(grep -c "sec1" output_server.txt)
  echo $SE1
}

s2errors(){
  SE2=$(grep -c "sec2" output_server.txt)
  echo $SE2
}

s3errors(){
  SE3=$(grep -c "sec3" output_server.txt)
  echo $SE3
}

s4errors(){
  SE4=$(grep -c "sec4" output_server.txt)
  echo $SE4
}

s5errors(){
  SE5=$(grep -c "sec5" output_server.txt)
  echo $SE5
}

s6errors(){
  SE6=$(grep -c "sec6" output_server.txt)
  echo $SE6
}

c0errors(){
  CE0=$(grep -c "cec0" output_client.txt)
  echo $CE0
}

c1errors(){
  CE1=$(grep -c "cec1" output_client.txt)
  echo $CE1
}

c2errors(){
  CE2=$(grep -c "cec2" output_client.txt)
  echo $CE2
}

c3errors(){
  CE3=$(grep -c "cec3" output_client.txt)
  echo $CE3
}

c4errors(){
  CE4=$(grep -c "cec4" output_client.txt)
  echo $CE4
}

c5errors(){
  CE5=$(grep -c "cec5" output_client.txt)
  echo $CE5
}

c6errors(){
  CE6=$(grep -c "cec6" output_client.txt)
  echo $CE6
}

c7errors(){
  CE7=$(grep -c "cec7" output_client.txt)
  echo $CE7
}

#Test 1: Initial Configuration Test for Client/Server
TWONE=0
C1=0
python3 s_test1.py > output_server.txt &
python3 c_test1.py > output_client.txt
TWONE=$((TWONE+$(s0errors)+$(s1errors)+$(s2errors)+$(s3errors)+$(s4errors)+$(s5errors)+$(s6errors)+$(c0errors)+$(c1errors)+$(c2errors)+$(c3errors)+$(c4errors)+$(c5errors)+$(c6errors)+$(c7errors)))
if [ $TWONE -ne 0 ]
then
  C1=$((C1+1))
fi
rm output_server.txt
rm output_client.txt

#Test 2: Initial Configuration Test for Client/Server with save_keys (working directory)
touch server_keys.pem
touch client_keys.pem
TWTWO=0
C2=0
python3 s_test2.py > output_server.txt &
python3 c_test2.py > output_client.txt
TWTWO=$((TWTWO+$(s0errors)+$(s1errors)+$(s2errors)+$(s3errors)+$(s4errors)+$(s5errors)+$(s6errors)+$(c0errors)+$(c1errors)+$(c2errors)+$(c3errors)+$(c4errors)+$(c5errors)+$(c6errors)+$(c7errors)))
if [ $TWTWO -ne 0 ]
then
  C2=$((C2+1))
fi
rm output_server.txt
rm output_client.txt

#Test 3: Initial Configuration Test for Client/Server with load_key (working directory)
#save_keys is not used in this case
TWTHREE=0
C3=0
python3 s_test3.py > output_server.txt &
python3 c_test3.py > output_client.txt
TWTHREE=$((TWTHREE+$(s0errors)+$(s1errors)+$(s2errors)+$(s3errors)+$(s4errors)+$(s5errors)+$(s6errors)+$(c0errors)+$(c1errors)+$(c2errors)+$(c3errors)+$(c4errors)+$(c5errors)+$(c6errors)+$(c7errors)))
if [ $TWTHREE -ne 0 ]
then
  C3=$((C3+1))
fi

#Test 4: Test for Client/Server attempting to use load_key with bad path
#save_keys is not used in this case
TWFOUR=0
C4=0
python3 s_test4.py > output_server.txt &
python3 c_test4.py > output_client.txt
TWFOUR=$((TWFOUR+$(s0errors)+$(s1errors)+$(s2errors)+$(s3errors)+$(s4errors)+$(s5errors)+$(s6errors)+$(c0errors)+$(c1errors)+$(c2errors)+$(c3errors)+$(c4errors)+$(c5errors)+$(c6errors)+$(c7errors)))
if [ $TWFOUR -ne 0 ]
then
  C4=$((C4+1))
fi
rm output_server.txt
rm output_client.txt
rm client_keys.pem
rm server_keys.pem

# Test 5: Test for Client/Server attempting setting the save key flag, but providing no path
TWSIX=0
C6=0
python3 s_test6.py > output_server.txt &
python3 c_test6.py > output_client.txt
TWSIX=$((TWSIX+$(s0errors)+$(s1errors)+$(s2errors)+$(s3errors)+$(s4errors)+$(s5errors)+$(s6errors)+$(c0errors)+$(c1errors)+$(c2errors)+$(c3errors)+$(c4errors)+$(c5errors)+$(c6errors)+$(c7errors)))
if [ $TWSIX -ne 0 ]
then
  C6=$((C6+1))
fi
rm output_server.txt
rm output_client.txt

#Save results to file to be used in gen_graph.py
touch results.txt
echo $C1 $C2 $C3 $C4 $C6 > results.txt
python3 gen_graph.py
