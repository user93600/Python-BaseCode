import socket
import json
import pymysql
from datetime import datetime
import pwinput

DB_CONFIG={
    "host":"127.0.0.1",
    "user":"root",
    "password":pwinput.pwinput("请输入密码："),
    "database":"tcp_data_db",
    "charset":"utf8mb4",
    "port":3306
}

#==========数据库查询==========
def query_records(start=None,end=None):
    """从mysql查询，可选时间过滤"""
    conn=pymysql.connect(**DB_CONFIG)
    cursor=conn.cursor(pymysql.cursors.DictCursor)

    sql="SELECT id,client_ip,receive_data,create_time FROM tcp_record"
    params=[]

    if start and end:
        sql+="WHERE create_time >= %s AND create_time <= %s"
        params=[start,end]

    sql+="ORDER BY create_time DESC LIMIT 100"
    cursor.execute(sql,params)
    rows=cursor.fetchall()

    for row in rows:
        if isinstance(row.get('create_time'),datetime):
            row['create_time']=row['create_time'].strftime("%Y-%m-%d %H:%M:%S")

    cursor.close()
    conn.close()
    return rows

#===========HTTP 响应构造=============
def make_http_response(status_code,body,content_type='application/json'):
    """
    手动拼接一个标准的 HTTP 响应
    格式：
        状态行（HTTP/1.1 200 OK）
        响应头（Content-Type, Content-Length...）
        空行
        响应体
    """
    status_message={
        200:"OK",
        400:"Bad Request",
        500:"Not Found"
    }
    status_msg=status_message.get(status_code,'Unknown')

    if isinstance(body,(dict,list)):
        body=json.dumps(body,ensure_ascii=False)

    
    headers=[]
    headers.append(f"HTTP/1.1{status_code}{status_msg}")
    headers.append(f"Content-Type:{content_type};charset=utf-8")
    headers.append(f"Content-Length:{len(body.encode('utf-8'))}")
    headers.append("Connection:close")
    headers.append("")

    response="\r\n".join(headers)+"\r\n"+body
    return response.encode('utf-8')

#==============请求解析==============
def parse_http_request(data):
    """
    解析原始HTTP请求报文
    返回字典，包含method,path,headers,params
    """

    request_text=data.decode("utf-8",errors='ignore')
    lines=request_text.split('\r\n')

    request_line=lines[0].split()
    method=request_line[0]
    full_path=request_line[1]

    if '?' in full_path:
        path,query_string=full_path.split('?',1)
    else:
        path=full_path
        query_string=''

    params={}
    if query_string:
        for pair in query_string.split('&'):
            if '=' in pair:
                key,value=pair.split('=',1)
                params[key]=value

    return{
        'method':method,
        'path':path,
        'params':params
    }

#===========路由处理============
def handle_request(parsed):
    """
    根据解析后的请求，执行对应的处理函数
    这就是flask @app背后做的事情：一个if/elif判断
    """

    path=parsed['path']
    params=parsed['params']

    if path =='/':
        return 200,{"message":"welcome to mini web server",'endpoints':["/api/records"]}
    
    elif path =='/api/records':
        start=params.get('start')
        end=params.get('end')
        data=query_records(start,end)
        return 200,data
    
    else:
        return 404,{"error":"Not Found","path":path}
    

#==========主程序=========
def main():
    server_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    server_socket.bind(("127.0.0.1",8080))
    server_socket.listen(5)
    print("简易web服务器已经启动，访问http://127.0.0.1:8080")

    while True:
        client_socket,addr=server_socket.accept()
        print(f"收到数据：{addr}")

        request_data=b''
        while True:
            chunk=client_socket.recv(4096)
            if not chunk:
                break
            request_data += chunk
            if b'\r\n\r\n' in request_data:
                break
        
        if not request_data:
            client_socket.close()
            continue

        print("="*40)
        print(request_data.decode('utf-8',error='ignore'))
        print("="*40)

        parsed=parse_http_request(request_data)
        print(f"解析结果：方法={parsed['method']},路径={parsed['path']},参数={parsed['params']}")

        status_code,body=handle_request(parsed)

        response=make_http_response(status_code,body)
        client_socket.sendall(response)
        client_socket.close()

if __name__=="__main__":
    main()