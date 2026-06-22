import socket
import time
import threading

SECRET="MySecretKey123"
HEARTBEAT_TIMEOUT=10
RECV_TIMEOUT=3

def handle_client(conn,addr):
    """每个客户端独立的处理线程，带超时断开"""
    print(f"[+]客户端{addr}已连接")
    conn.settimeout(5)

    try:
        auth_data=conn.recv(1024).decode().strip()
        if auth_data!=f"AUTH {SECRET}":
            print(f'[-]{addr}认证超时（5秒内未发送认证信息）')
            conn.close()
            return
    except socket.timeout:
        print(f"[-]{addr}认证超时（5秒内未发送认证信息）")
        conn.close()
        return
    except Exception as e:
        print(f"[-]{addr}认证异常：{e}")
        conn.close()
        return
    
    conn.settimeout(RECV_TIMEOUT)
    print(f"[+]{addr}认证成功，进入心跳保活模式")

    last_data_time=time.time()

    try:
        while True:
            try:
                data=conn.recv(1024)
            except socket.timeout:
                elapsed=time.time()-last_data_time
                if elapsed >=HEARTBEAT_TIMEOUT:
                    print(f"[-]客户端{addr}超时无心跳，（{elapsed:.1f}s无数据）主动断开（已静默{elapsed:.1f}s)")
                    break
                continue

            if not data:
                print(f"[-]{addr}正常断开连接")
                break

            last_data_time=time.time()
            msg=data.decode().strip()
            

            if msg=="PING":
                conn.send(b'PONG\n')
                print(f"    {addr}心跳回复)")
            else:
                conn.send(data)
                print(f"    {addr}数据：{msg}")

    except (ConnectionRefusedError,OSError):
        print(f"[-]客户端{addr}连接异常断开")
    finally:
        conn.close()
        print(f"[-]客户端{addr}资源释放")

def main():
    server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    server.bind(('127.0.0.1',12345))
    server.listen(5)
    print("心跳保活服务器启动，10秒无数据断开....")

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