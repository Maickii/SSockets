python3 tests/new_api/server_recv_then_send.py &
sleep 2
python3 tests/new_api/client_send_then_recv.py
sleep 2
python3 tests/new_api/ecdh_server.py &
sleep 2
python3 tests/new_api/ecdh_client.py
