#!/bin/sh
number_of_tests_passed=0
for i in 1 2 3
do
  python3 simple_server_test.py &
  python3 simple_client_test.py
done
echo "Test Passed"
echo "Will now auto generate figure"
python3 gen_graph.py
