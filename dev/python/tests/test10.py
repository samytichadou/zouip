import socket

# Connect to server
s = socket.socket()

print("debugA")
s.connect(("192.168.1.36",12345))
print("connected")
