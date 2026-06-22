import socket

server =socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
server.bind(('127.0.0.1',12345))
print("UDP回声服务器已启动，监听 127.0.0.1：12345")

while True:
    data,addr=server.recvfrom(1024)
    print(f"收到来自{addr}的数据:{data.decode()}")
    server.sendto(data,addr)