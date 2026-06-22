import socket

class SimpleHTTPResponse:
    """简单的HTTP响应对象"""
    def __init__(self):
        self.status_code=0
        self.headers={}
        self.body=b''

def http_get(host,port=80,path='/'):
    sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.settimeout(5)
    sock.connect((host,port))

    request=(
        f"GET {path} HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        "Connection: close\r\n"
        "\r\n"
    )
    sock.send(request.encode())

    response = b''
    while True:
        chunk =sock.recv(4096)
        if not chunk:
            break
        response+=chunk

    sock.close()
    return response

host="www.example.com"
print(f"连接{host}...")
response=http_get(host)
print("============HTTP响应=============")
print(response.decode(errors='repalce'))