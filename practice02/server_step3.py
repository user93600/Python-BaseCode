import socket

server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.bind(("127.0.0.1",11122))
server.listen(1)
print("服务器已经启动，等待客户端连接")

conn,addr=server.accept()
print(f"客户端{addr}已连接")

while True:
    data=conn.recv(1024)
    if not data:
        print("客户端已经断开了")
        break
    num=int(data.decode())
    print(f"实时收到{num}")

conn.close()
server.close()