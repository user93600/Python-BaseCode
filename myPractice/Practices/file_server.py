import socket
import os

SAVE_DIR=os.path.join(os.path.dirname(__file__),"received_files")
os.makedirs(SAVE_DIR,exist_ok=True)

def recv_exact(conn,size):
    """精确接收指定字节数，用于接收固定长度的头部信息"""
    data=b''
    while len(data)<size:
        chunk=conn.recv(size-len(data))
        if not chunk:
            raise ConnectionError("连接断开，无法接收完整数据")
        data += chunk
    return data

def recv_file_resume(conn,filename,filesize,offset):
    """断点续传：接收文件，从offset位置追加写入"""
    filepath=os.path.join(SAVE_DIR,filename)
    try:
        with open(filepath,'ab+') as f:
            f.seek(offset)
            remaining=filesize-offset

            while remaining>0:
                chunk=conn.recv(min(4096,remaining))
                if not chunk:
                    return False
                f.write(chunk)
                remaining-=len(chunk)
        return True
    except Exception as e:
        print(f"写入失败：{e}")
        return False

def recv_file(conn,filename,filesize):
    """接收文件内容并写入磁盘，返回是否成功"""
    filepath=os.path.join(SAVE_DIR,filename)
    try:
        with open(filepath,'wb')as f:
            remaining=filesize
            while remaining>0:
                chunk=conn.recv(min(4096,remaining))
                if not chunk:
                    os.remove(filepath)
                    return False
                f.write(chunk)
                remaining -= len(chunk)
        return True
    except Exception as e:
        print(f"写入文件失败：{e}")
        return False

def main():
    server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    server.bind(('127.0.0.1',12345))
    server.listen(1)
    print("文件服务器已启动，等待客户端连接....")

    conn,addr=server.accept()
    print(f"客户端{addr}已连接")

    try:
        name_len_bytes=recv_exact(conn,4)
        name_len=int.from_bytes(name_len_bytes,'big')

        filename_bytes=recv_exact(conn,name_len)
        filename=filename_bytes.decode('utf-8')

        size_bytes=recv_exact(conn,8)
        filesize=int.from_bytes(size_bytes,'big')

        print(f"准备接收文件：{filename},大小{filesize}字节")

        filepath=os.path.join(SAVE_DIR,filename)
        exist_size=0
        if os.path.exists(filepath):
            exist_size=os.path.getsize(filepath)
            if exist_size>=filesize:
                conn.send(b"ALREADY_DONE")
                print(f"文件{filename}已完整接收")
                return
            
        conn.send(exist_size.to_bytes(8,'big'))
        print(f"准备续传：{filename}|总大小：{filesize}|已接收{exist_size}")


        success=recv_file_resume(conn,filename,filesize,exist_size)

        if success:
            conn.send(b"SUCCESS")
            print(f"文件{filename}接收成功")
        else:
            conn.send(b"FAILED")
            print(f"文件{filename}接收失败")

    except Exception as e:
        print(f"传输错误:{e}")
        conn.send(b"FAILED")

    finally:
        conn.close()
        server.close()
if __name__=="__main__":
    main()
