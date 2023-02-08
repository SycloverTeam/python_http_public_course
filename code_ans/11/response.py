from curses import raw
from request import PreparedRequest

import re,gzip,zlib
from urllib.parse import unquote


class InvalidResponseError(RuntimeError):
    def __init__(self, msg):
        self.msg = msg


class Response():
    def __init__(self) -> None:
        self.request: PreparedRequest = None
        self.url: str = None

        self.http_version: str = None
        self.status_code: int = None
        self.ok: bool = None
        self.reason: str = None
        self.headers: dict = None
        self.cookies: dict = None
        self.body: bytes = None
        self.content: bytes = None

    def setRequest(self, request: PreparedRequest):
        self.request = request
        self.url = request.url

    def setResponse(self, http_version: str, status_code: int, reason: str, headers: dict, cookies: dict, body: bytes):
        self.http_version = http_version
        self.status_code = status_code
        self.ok = self.status_code == 200
        self.reason = reason
        self.headers = headers
        self.cookies = cookies
        self.body = body
        self.content = body


def analysis_response(raw_data):
    # 解释成功则返回一个Response实例，记得调用serResponse方法
    # 解析失败则 raise InvalidResponseError()
    ...
    def prepare(raw_data):
        if isinstance(raw_data,bytes):
            if len(re.findall(b'\r\n\r\n',raw_data)) != 1:
                raise InvalidResponseError("body err")
            flag=0
            ansl=[]
            ll = raw_data.split(b"\r\n\r\n")[0].split(b'\r\n')
            for i in ll:
                ansl.append(i.decode("UTF-8"))
                if b"Content-Encoding" in i:
                    flag=1
                    data = raw_data.split(b"\r\n\r\n")[1]
                    #print(data,33)
                    zip_method = i.replace(b",",b"").split(b" ")
                    for k in zip_method[::-1]:
                        #print(1111)
                        if k == b"gzip":
                            data = gzip.decompress(data)
                        if k == b"deflate":
                            data = zlib.decompress(data)
                    ansl.append(data)
        else:
            if len(re.findall('\r\n\r\n',raw_data)) != 1:
                raise InvalidResponseError("body err")            
            ansl = raw_data.split('\r\n') 
        #print(len(raw_data.split(b"\r\n\r\n")),3333)
        if isinstance(raw_data,bytes) and flag == 0:
            raw_data=raw_data.decode("UTF-8")
            ansl = raw_data.split('\r\n') 
        #print(ansl)
        return ansl        
    def get_http_version(raw_data):
        data=re.findall("HTTP.*? ",raw_data[0])
        if len(data) != 1:
            raise InvalidResponseError("errr")
        return data[0].strip()
    
    def get_status_code(raw_data):
        data=re.findall(" (\d*) ",raw_data[0])
        if len(data) != 1:
            raise InvalidResponseError("errr")
        return int(data[0].strip())
    
    def get_reason(raw_data):
        if get_status_code(raw_data) == 200:
            return "OK"
        if get_status_code(raw_data) == 301:
            return "Moved Permanently"
        
    def get_headers_cookie(raw_data):
        hl=dict()
        ck=dict()
        #print(1)
        del raw_data[0]
        #print(raw_data)
        for i in raw_data:
            #i=str(i)
            if i == "" or isinstance(i,bytes):
                break
            #print(i)
            if i.split(":")[0]=="Set-Cookie":
                try:
                    for j in i.replace("Set-Cookie: ","").split(";"):
                        ck[j.split('=')[0].strip()]=unquote(j.split('=')[1],"utf-8")
                except:
                    pass
                #print(ck)
            hl[i.split(":")[0]] = i.replace(i.split(":")[0]+": ","")
        return (hl,ck)

    def get_body(raw_data):
        data=raw_data[-1]
        #print(raw_data)
        if isinstance(data,str):
            return data.encode("UTF-8")
        return data
    raw_data = prepare(raw_data)
    hl,ck = get_headers_cookie(raw_data.copy())
    ans=Response()
    ans.setResponse(http_version=get_http_version(raw_data.copy()),
                    status_code=get_status_code(raw_data.copy()),
                    reason=get_reason(raw_data.copy()),
                    headers=hl,
                    cookies=ck,
                    body=get_body(raw_data.copy()))
    return ans
