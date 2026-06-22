import socket
from datetime import datetime

server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
server.bind(("127.0.0.1",12345))
server.listen(1)
print("echo 回声服务器已启动，等待客户连接...")

conn,addr=server.accept()
print(f"客户端{addr}已连接")

while True:
    data=conn.recv(1024)
    if not data:
        print("客户端断开连接")
        break
    text=data.decode().strip()
    print(f"收到：{data.decode().strip()}")
    timestamp=datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    reply=timestamp+text
    conn.send(reply.encode())

conn.close()
server.close()