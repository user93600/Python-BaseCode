import socket

server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

server.bind(("127.0.0.1",54321))

server.listen(1)
print("服务器已经启动，等待客户端连接")

conn,addr =server.accept()
print(f"客户端{addr}已连接")

data = conn.recv(1024)
print(f"收到客户端消息：{data.decode()}")

conn.close()
server.close()