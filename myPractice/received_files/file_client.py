import socket
import os
import sys

def send_exact(sock,data):
    """确保所有数据都发送出去"""
    total=0
    while total<len(data):
        sent=sock.send(data[total:])
        if sent==0:
            raise ConnectionError("连接断开")
        total+=sent

def recv_exact(conn,size):
    data=b''
    while len(data)<size:
        chunk=conn.recv(size-len(data))
        if not chunk:
            raise ConnectionError("连接断开")
        data+=chunk
    return data

def send_file_resume(host,port,filepath):
    if not os.path.isfile(filepath):
        print(f"文件{filepath}不存在")
        return
    filename=os.path.basename(filepath)
    filesize=os.path.getsize(filepath)

    client=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client.connect((host,port))

    try:
        name_bytes=filename.encode('utf-8')
        name_len=len(name_bytes)
        send_exact(client,name_len.to_bytes(4,'big'))

        send_exact(client,name_bytes)

        send_exact(client,filesize.to_bytes(8,'big'))

        exist_bytes=recv_exact(client,8)
        exist_bytes=int.from_bytes(exist_bytes,'big')

        if exist_bytes>=filesize:
            print("已完整传输，无需重传")
            return
        
        print(f"开始续传|已传输：{exist_bytes}|剩余：{filesize-exist_bytes}")


        with open(filepath,'rb') as f:
            f.seek(exist_bytes)
            while True:
                chunk=f.read(4096)
                if not chunk:
                    break
                send_exact(client,chunk)

        response=client.recv(1024)
        print("服务器响应：",response.decode())

    except Exception as e:
        print(f"传输失败：{e}")
    finally:
        client.close()


def send_file(host,port,filepath):
    if not os.path.isfile(filepath):
        print(f"文件{filepath}不存在")
        return
    
    filename=os.path.basename(filepath)
    filesize=os.path.getsize(filepath)

    client=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client.connect((host,port))

    try:
        name_bytes=filename.encode('utf-8')
        name_len=len(name_bytes)
        send_exact(client,name_len.to_bytes(4,'big'))

        send_exact(client,name_bytes)

        send_exact(client,filesize.to_bytes(8,'big'))

        with open(filepath,'rb') as f:
            while True:
                chunk=f.read(4096)
                if not chunk:
                    break
                send_exact(client,chunk)

        response=client.recv(1024)
        print("服务器响应：",response.decode())

    except Exception as e:
        print(f"传输失败：{e}")
    finally:
        client.close()

if __name__=="__main__":
    if len(sys.argv)<2:
        print("用法：python file_client.py <文件路径>")
        sys.exit(1)
    filepath=sys.argv[1]
    send_file_resume('127.0.0.1',12345,filepath)