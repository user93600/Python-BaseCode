import socket

class SimpleHTTPResponse:
    """简单的HTTP响应对象"""
    def __init__(self):
        self.status_code=0
        self.headers={}
        self.body=b''

def http_get_advance(host,port=80,path='/'):
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

    response_obj=SimpleHTTPResponse()

    header_data = b''
    while b'\r\n\r\n' not in header_data:
        chunk=sock.recv(4096)
        if not chunk:
            break
        header_data += chunk

    header_end=header_data.find(b'\r\n\r\n')
    header_part=header_data[:header_end].decode()
    body_start=header_data[header_end+4:]

    lines=header_part.split('\r\n')
    status_line=lines[0]
    parts=status_line.split()
    if len(parts) >=2:
        response_obj.status_code=int(parts[1])

    for line in lines[1:]:
        if ':' in line:
            key,value=line.split(':',1)
            response_obj.headers[key.strip().lower()]=value.split()

    raw_content_length=response_obj.headers.get('content-length',0)
    if isinstance(raw_content_length,list):
        raw_content_length=raw_content_length[0]
    content_length=int(raw_content_length)

    body=body_start
    remaining=content_length-len(body)
    while remaining>0:
        chunk =sock.recv(min(4096,remaining))
        if not chunk:
            break
        body+=chunk
        remaining-=len(chunk)

    response_obj.body=body
    sock.close()
    return response_obj

host="www.baidu.com"
resp=http_get_advance(host)
print(f"状态码:{resp.status_code}")
print(f"Content-Length:{resp.headers.get('content-length','unknown')}")
print(f"Content-Type:{resp.headers.get("content-type",'unknown')}")
print("===========正文前200个字符=========")
print(resp.body[:200].decode(errors='replace'))