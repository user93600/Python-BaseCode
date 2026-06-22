import socket
import base64
import hashlib
import struct

MAGIC_STRING="258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

def handle_client(conn,addr):
    print("[+]客户端{addr}已连接")
    try:
        #========http握手==========
        #接收客户端的http请求
        request_data=b''
        while b"\r\n\r\n" not in request_data:
            request_data+=conn.recv(4096)

        request_text=request_data.decode()
        print("收到http升级请求:")
        print(request_text)

        #提取Sec-WebSocket-Key(必须的头部)
        key=None
        for line in request_text.split('\r\n'):
            if line.lower().startswith("sec-websocket-key:"):
                key=line.split(":",1)[1].strip()
                break

        if not key:
            print("[-]缺少 Sec-WebSocket-Key,断开")
            conn.close()
            return
        
        #计算响应密钥
        response_key=base64.b64encode(
            hashlib.sha1((key+MAGIC_STRING).encode()).digest()
        ).decode()

        #构造HTTP101切换协议响应
        response=(
            "HTTP/1.1 101 Switching Protocols\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Accept: {response_key}\r\n"
            "\r\n"
        )

        conn.send(response.encode())
        print("[+]握手完成，协议已升级为 WebSocket")

        #=========第二步：帧收发循环========
        while True:
            frame=recv_frame(conn)
            if frame is None:
                break
            #收到文本帧，原样回显（Echo)
            if frame['opcode']==1:#文本帧
                print(f"收到消息：{frame['payload']}")
                send_frame(conn,frame['payload'])
            elif frame['opcode']==8:#关闭帧
                print("收到关闭帧")
                break
            elif frame['opcode']==9:#Ping
                print("收到Ping，回复Pong")
                send_frame(conn,frame['payload'],opcode=10)

    except Exception as e:
        print(f"[-]异常：{e}")
    finally:
        conn.close=()
        print(f"[-]客户端{addr}断开")


def recv_frame(conn):
    """解析webSocket帧，返回{opcode，ayload}或None（连接关闭）"""
    #读取前二字节基本头
    header=conn.recv(2)
    if len(header)<2:
        return None
    
    byte1,byte2=header[0],header[1]
    fin=(byte1>>7) & 1        #最高位FIN
    opcode=byte1 & 0x0F       #低四位操作码
    masked=(byte2>>7) & 1     #MASK位，客户端发来必须为1
    payload_len=byte2 & 0x7F  #载荷长度（初始）

    if not masked:
        #客户端到服务器的帧必须是掩码的，否则断开
        raise Exception("客户端帧必须掩码")
    
    #扩展载荷长度
    if payload_len==126:
        ext=conn.recv(2)
        payload_len=struct.unpack("!H",ext)[0] #无符号短整型，网络字节序
    elif payload_len==127:
        ext=conn.recv(8)
        payload_len=struct.unpack("!Q",ext)[0] #无符号长整型

    #读取四字掩码
    mask_key=conn.recv(4)

    #读取载荷数据
    payload_data=b''
    while len(payload_data)<payload_len:
        chunk=conn.recv(payload_len-len(payload_data))
        if not chunk:
            break
        payload_data+=chunk

    #用掩码解码：每个字节与mask_key[i%4]做异或
    unmasked=bytes(
        payload_data[i]^mask_key[i%4] for i in range(len(payload_data))
    )

    return{
        'opcode':opcode,
        'payload':unmasked.decode('utf-8',errors='replace')
    }

def send_frame(conn,payload_text,opcode=1):
    """发送文本帧给客户端（服务器到客户端不需要掩码）"""
    payload=payload_text.encode('utf-8')
    length=len(payload)

    #构造帧头
    frame=bytearray()
    frame.append(0x80 | opcode)   #FIN+操作码

    if length<126:
        frame.append(length)
    elif length<65536:
        frame.append(126)
        frame.extend(struct.pack("!H",length))
    else:
        frame.append(127)
        frame.extend(struct.pack("!Q",length))

    frame.extend(payload)
    conn.send(frame)

def main():
    server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    server.bind(('127.0.0.1',8000))
    server.listen(1)
    print("WebSocket 服务器启动在 ws://127.0.0.1:8000")

    while True:
        conn,addr=server.accept()
        handle_client(conn,addr)

if __name__=="__main__":
    main()