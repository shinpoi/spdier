# print the tcplink-data what you get.

import socket
import time
import threading
import sys

args = sys.argv
try:
    PORT = int(sys.argv[1])
except IndexError:
    PORT = 8000
print("set port=%d" % PORT)

def tcplink(sock, addr):
    print('Accept new connection from %s:%s...' % addr)
    
    while True:
        data = sock.recv(4096)
        time.sleep(1)
        if not data or data.decode('utf-8') == 'exit':
            break
        print("\n---------start---------")
        print(data.decode('utf-8'))
        print("----------end----------\n")
    sock.close()
    print('Connection from %s:%s closed.' % addr)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('127.0.0.1', PORT))
s.listen(5)

print('Waiting for connection...')

while True:
    try:
        sock, addr = s.accept()
        t = threading.Thread(target=tcplink, args=(sock, addr))
        t.start()
    except KeyboardInterrupt:
        t.stop()
        raise KeyboardInterrupt



