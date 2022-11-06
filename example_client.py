import socket
import time

sock = socket.socket()
sock.connect(("localhost", 1234))

sock.send("Halaa".encode())

print(sock.recv(1024))
sock.send("BlaBla".encode())
print("end")
time.sleep(10)
