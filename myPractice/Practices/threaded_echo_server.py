import socket
import threading

def handle_client(conn,addr):
    """每个客户端独立的处理线程"""
    print(f"[+]客户端{addr}已连接")
    try:
        while True:
            data=conn.recv(1024)
            if not data:
                break
            conn.send(data)

    except ConnectionResetError:
        print(f"[-]客户端{addr}强制断开")
    finally:
        print(f"[-]客户端{addr}断开")
        conn.close()

def main():
    server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    server.bind(('127.0.0.1',12345))
    server.listen(5)
    print('多线程Echo服务器启动，等待连接....')

    try:
        while True:
            conn,addr=server.accept()
            t=threading.Thread(target=handle_client,args=(conn,addr))
            t.daemon=True
            t.start()
    except KeyboardInterrupt:
        print("\n服务器关闭")
    finally:
        server.close()

if __name__=="__main__":
    main()