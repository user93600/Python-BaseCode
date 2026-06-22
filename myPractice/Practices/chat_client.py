import socket
import threading

def receive_messages(sock):
    while True:
        try:
            data=sock.recv(1024)
            if not data:
                print("与服务器断开连接")
                break
            print(data.decode())
        except:
            break

def main():
    nickname=input("请输入您的昵称：").strip()
    if not nickname:
        nickname="Anonymous"
    client=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client.connect(("127.0.0.1",12345))
    client.send(f"NICK {nickname}".encode())
    print("输入消息并回车发送:\n输入/quit 退出\n输入/nick +昵称  修改昵称")
    recv_thread=threading.Thread(target=receive_messages,args=(client,),daemon=True)
    recv_thread.start()

    while True:
        msg=input()
        if msg == '/quit':
            break
        if msg.startswith('/nick '):
            client.send(f"NICK {msg[6:]}".encode())
            continue
        client.send(msg.encode())
    client.close()

if __name__=="__main__":
    main()