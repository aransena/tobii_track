# Adapted from https://wiki.python.org/moin/TcpCommunication

#!/usr/bin/env python

import socket
import time

TCP_IP = '127.0.0.1'
TCP_PORT = 8000
BUFFER_SIZE = 1024  # Normally 1024, but we want fast response

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)

conn, addr = s.accept()
print('Connection address:', addr)

while 1:
    start = time.time()
    data = conn.recv(BUFFER_SIZE)
    if not data:
        break
    print("received data:", data.decode('utf-8'))
    print(1/(time.time() - start))
    # conn.send(data)  # echo

conn.close()