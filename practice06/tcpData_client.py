import socket
import time
import random

client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client.connect(("127.0.0.1",8888))

while True:
    num=random.randint(0,100)
    client.send(f"{num}\n".encode())
    print(f"已发送：{num}")
    time.sleep(1)