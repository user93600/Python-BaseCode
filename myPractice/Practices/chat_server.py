import socket
import selectors

sel=selectors.DefaultSelector()

clients={}

def accept(sock,mask):
    conn,addr=sock.accept()
    conn.setblocking(False)

    nickname=f"User-{addr[1]}"
    clients[conn]=(nickname,addr)
    print(f'{nickname}进入聊天室',conn)
    broadcast(f"{nickname}({addr})进入了聊天室",conn)
    sel.register(conn,selectors.EVENT_READ,read)

def read(conn,mask):
    nickname,addr=clients[conn]
    try:
        data=conn.recv(1024)
    except:
        data=None
    if not data:
        print(f"{nickname}({addr})离开了")
        broadcast(f"{nickname}离开了聊天室")
        sel.unregister(conn)
        conn.close()
        del clients[conn]
        return
    msg=data.decode().strip()
    if not msg:
        return
    if msg.startswith("NICK "):
        new_nick=msg[5:].strip()
        if new_nick:
            old_nick=nickname
            clients[conn]=(new_nick,addr)
            broadcast(f"{old_nick}改名为{new_nick}",conn)
            print(f"{old_nick}->{new_nick}")

    else:
        broadcast(f"{nickname}:{msg}",conn)

def broadcast(message,sender_conn=None):
    print(f"广播:{message}")
    data=message.encode()
    for sock,(nick,addr) in clients.items():
        if sock != sender_conn:
            try:
                sock.send(data)
            except:
                pass


def main():
    host="127.0.0.1"
    port=12345
    server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    server.bind((host,port))
    server.listen(5)
    server.setblocking(False)
    print(f"聊天室服务器启动在{host}：{port}")
    sel.register(server,selectors.EVENT_READ,accept)

    try:
        while True:
            events=sel.select(timeout=1)
            for key,mask in events:
                callback=key.data
                callback(key.fileobj,mask)

    except KeyboardInterrupt:
        print("服务器关闭")
    finally:
        sel.unregister(server)
        server.close()

if __name__=="__main__":
    main()
                
