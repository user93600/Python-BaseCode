import socket
from concurrent.futures import ThreadPoolExecutor

def handle_client(conn,addr):
    print(f"[+]客户端{addr}已连接")
    try:
        while True:
            data=conn.recv(1024)
            if not data:
                break
            conn.send(data)
    except ConnectionResetError:
        print(f"客户端{addr}已强制断开")
    finally:
        conn.close()
        print(f"客户端{addr}已断开")


def main():
    server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    server.bind(('127.0.0.1',12345))
    server.listen(5)
    print("线程池Echo服务器启动（最大10线程）....")

    executor=ThreadPoolExecutor(max_workers=10)

    try:
        while True:
            conn,addr=server.accept()
            executor.submit(handle_client,conn,addr)
    except KeyboardInterrupt:
        executor.shutdown(wait=True)
        server.close()

if __name__=="__main__":
    main()