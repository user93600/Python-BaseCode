import socket
import pymysql
import threading

DB_CONFIG={
    "host":"127.0.0.1",
    "user":"root",
    "password":input("请输入密码："),
    "database":"tcp_data_db",
    "port":3306,
    "charset":"utf8mb4"
}

def save_to_database(client_ip,data):
    conn=None
    cursor=None
    try:
        conn=pymysql.connect(**DB_CONFIG)
        cursor=conn.cursor()

        sql="INSERT INTO tcp_record (client_ip,receive_data) VALUES (%s,%s)"
        cursor.execute(sql, (client_ip, data))

        conn.commit()
        print(f"数据保存至{client_ip}-{data}")
        return True
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"数据上传失败：{type(e).__name__}-{e}")
        return False
    finally:
        if conn:
            conn.close()
        if cursor:
            cursor.close()
    
def handle_client(client_socket,client_addr):
    client_ip=client_addr[0]
    print(f"客户端连接：{client_ip}:{client_addr[1]}")

    try:
        while True:
            data=client_socket.recv(1024).decode("utf-8").strip()

            if not data:
                print(f"客户端断开连接：{client_ip}:{client_addr[1]}")
                break

            print(f"收到来自{client_ip}的数据：{data}")

            success=save_to_database(client_ip,data)

            if success:
                client_socket.send("数据已成功保存到数据库".encode("utf-8"))

            else:
                client_socket.send("数据保存失败".encode("utf-8"))

    except Exception as e:
        print(f"客户端处理错误：{type(e).__name__}-{e}")

    finally:
        client_socket.close()

def start_server():
    server_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    server_socket.bind(("0.0.0.0",8888))
    server_socket.listen(5)

    print("TCP服务端已启动，监听窗口8888")
    print("等待客户端响应...")

    try:
        while True:
            client_socket,client_addr=server_socket.accept()
            client_thread=threading.Thread(target=handle_client,args=(client_socket,client_addr))
            client_thread.start()

    except KeyboardInterrupt:
        print("\n服务端正在关闭...")

    finally:
        server_socket.close()
        print("服务端已关闭")

if __name__=="__main__":
    start_server()