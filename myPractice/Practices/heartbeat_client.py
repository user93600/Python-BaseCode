import socket
import time
import threading

def heartbeat_loop(sock):
    """后台线程，每2秒发送PING"""
    while True:
        time.sleep(2)
        try:
            sock.send(b"PING\n")
        except:
            break

def main():
    client=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client.connect(("127.0.0.1",12345))

    auth_msg=b'AUTH MySecretKey123\n'
    client.send(auth_msg)
    print("发送认证信息")

    hb_thread=threading.Thread(target=heartbeat_loop,args=(client,),daemon=True)
    hb_thread.start()

    try:
        while True:
            data=client.recv(1024)
            if not data:
                print("服务器断开连接")
                break
            msg=data.decode().strip()
            if msg=="PONG":
                pass
            else:
                print(f"服务器回复：{{msg}}")

    except KeyboardInterrupt:
        print("客户端退出")
    except ConnectionRefusedError:
        print("连接被服务器重置（可能认证失败）")
    finally:
        client.close()

if __name__=="__main__":
    main()