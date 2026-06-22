import json
import re
from wsgiref.simple_server import make_server

#===========请求上下文===============
class Request:
    """模拟flask的request对象，包装wsgi的envrion字典
        让用户在视图函数中通过 request.path,request.args等方式获取信息    
    """

    def __init__(self,environ):
        self.environ=environ
        self.method=environ.get("REQUEST_METHOD",'GET')
        self.path=environ.get('PATH_INFO','/')
        self.query_string=environ.get('QUERY_STRING','')
        self.args={}
        if self.query_string:
            for pair in self.query_string.split('&'):
                if "=" in pair:
                    k,v=pair.split('=',1)
                    self.args[k]=v
