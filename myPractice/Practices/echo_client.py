import socket

client=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client.connect(('127.0.0.1',12345))

while True:
    msg=input("请输入需要发送的消息（输入quit退出）：")
    if msg=='quit':
        break
    client.send(msg.encode())
    reply=client.recv(1024)
    print(f"服务器回复：{reply.decode()}")

client.close()
