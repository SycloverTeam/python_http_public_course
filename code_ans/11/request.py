

from urllib.parse import urlparse,unquote
from string import ascii_lowercase, digits
from random import choice

import re
import json

class PrepareError(RuntimeError):
    def __init__(self, msg):
        self.msg = msg


class AnalysisError(RuntimeError):
    def __init__(self, msg):
        self.msg = msg


class File():
    def __init__(self, name: str, filename: str, content_type: str, data: bytes):
        self.name = name
        self.filename = filename
        self.content_type = content_type
        self.data = data


class PreparedRequest():
    def __init__(self):
        ...
        # self.method = None
        # self.url = None
        # self.headers = None
        # self.cookies = None
        # self.http_version = None

    def prepare(self, method, url, http_version, headers, cookies, params, body, files=None, update=False):
        self.method = method
        self._set_cookies(cookies)
        self._set_headers(headers)
        self.__set_url(url, update)
        self._set_params(params, update)
        self._set_body(body, update)
        self._set_files(files, update)
        self.http_version = http_version

    def __parse_qs(self, qs_dict):
        result = ""
        for k, v in qs_dict.items():
            if isinstance(v, (tuple, list)):
                result += "&".join(f"{k}={e}" for e in v) + "&"
            else:
                result += f"{k}={v}&"
        result = result.rstrip("&")
        return result

    def __set_url(self, url, update_host=True):
        url_parsed = urlparse(url)
        if url_parsed.path == "":
            url_parsed = url_parsed._replace(path="/")
        self.host = url_parsed.hostname
        port = url_parsed.port
        if not port:
            if url.startswith("https"):
                port = 443
            else:
                port = 80
        self.port = port
        self.path = url_parsed.path

        self._params_str = url_parsed.query
        self.__dict__['url'] = url
        if update_host:
            self.__set_header("HOST", "%s:%d" % (url_parsed.hostname, port))
    
    def __set_header(self, key, value):
        if not hasattr(self, "headers"):
            self._set_headers({})

        for k in self.headers.keys():
            if k.upper() == key:
                self.__dict__['headers'][k] = value
                return

        self.__dict__['headers'][key.capitalize()] = value

    def _set_headers(self, headers):
        if not isinstance(headers, dict):
            raise PrepareError("Invalid headers type, must be dict.")

        self.__dict__['headers'] = headers

    def _set_cookies(self, cookies):
        if not isinstance(cookies, dict):
            raise PrepareError("Invalid cookies type, must be dict.")

        self.__dict__['cookies'] = cookies
        if cookies:
            self.__set_header("COOKIES", self.__parse_qs(
                cookies).replace("&", "; "))

    def _set_params(self, params, update_host=True):
        if not isinstance(params, dict):
            raise PrepareError("Invalid params type, must be dict.")

        self.__dict__['params'] = params

        url_parsed = urlparse(self.url)
        query_str = self.__parse_qs(params)
        url_parsed = url_parsed._replace(query=query_str)
        self.__set_url(url_parsed.geturl(), update_host)

    def _set_body(self, body, update_content_length=True):
        if not isinstance(body, (dict, str, bytes)) and body is not None:
            raise PrepareError(
                "Invalid data type, must be dict or string or bytes.")

        if isinstance(body, dict):
            body = self.__parse_qs(body).encode()
        elif isinstance(body, str):
            body = body.encode()
        elif body is None:
            body = b""

        self.__dict__['body'] = body
        if body and update_content_length:
            self.__set_header("CONTENT-LENGTH", str(len(body)))

    def _set_files(self, files, update_data=True):
        if (isinstance(files, (tuple, list)) and all(isinstance(file, File) for file in files)) or files is None:
            if files is None:
                return

            self.__dict__['files'] = files

            if update_data:
                alphabet = list(ascii_lowercase + digits)
                boundary = ''.join([choice(alphabet) for _ in range(32)])
                content_type = f"multipart/form-data; boundary={boundary}"
                self.__set_header("CONTENT-TYPE", content_type)
                body = b""

                for f in files:
                    filename = b'; filename="' + f.filename.encode() + b'"' if f.filename else b""
                    content_type = b"Content-Type: " + \
                        f.content_type.encode() if f.content_type else b""

                    body += b"--" + boundary.encode() + b"\r\n"
                    body += b'Content-Disposition: form-data; name="' + f.name.encode() + b'"' + \
                        filename + b"\r\n"
                    body += (content_type + b"\r\n" if content_type else b"")
                    body += b"\r\n"
                    body += f.data + b"\r\n"
                    body += b"\r\n"

                body += b"--" + boundary.encode() + b"--"
                self._set_body(body)
            return

        raise PrepareError("Invalid files type, must be File list.")

    def __setattr__(self, __name, __value) -> None:
        if __name == "url":
            return self.__set_url(__value)
        elif __name == "params":
            return self._set_params(__value)
        elif __name == "headers":
            return self._set_headers(__value)
        elif __name == "cookie":
            return self._set_cookies(__value)
        elif __name == "body":
            return self._set_body(__value)
        elif __name == "files":
            return self._set_files(__value)
        else:
            self.__dict__[__name] = __value

    def to_raw(self) -> str:
        headers = '\r\n'.join(['{}: {}'.format(*kv)
                            for kv in self.headers.items()])
        return f"""{self.method} {self.path}{"?" if self._params_str else ""}{self._params_str} {self.http_version}\r
{headers}\r
\r
""".encode() + self.body

def analysis_request(raw_data, update_content_length=True):
    # 解释成功则返回一个PreparedRequest实例，记得调用prepare方法来设置其属性
    # 解析失败则 raise AnalysisError()
    ...
    global method
    global content_type
    def pre_raw_data(raw_data):
        global method
        if isinstance(raw_data,bytes):
            raw_data=raw_data.decode("UTF-8")
        ansl = raw_data.split('\r\n')
        method=ansl[0].split(" ")[0].lower()
        if method == "get":
            try:
                if  not raw_data.endswith('\r\n\r\n') or raw_data == "" or len(ansl[0].split(" ")) != 3:
                    raise AnalysisError("geterr")
            except:
                raise AnalysisError("geterr")
        if method == "post":
            try:
                if  raw_data == "" or len(ansl[0].split(" ")) != 3:
                    raise AnalysisError("posterr")
            except:
                raise AnalysisError("posterr")            
                    
        return ansl
    
    def get_headers_cookie(raw_data):
        hl=dict()
        ck=dict()
        #print(1)
        del raw_data[0]
        for i in raw_data:
            if i == "":
                break
            #print(i)
            if i.split(":")[0]=="Cookie":
                for j in i.replace("Cookie: ","").split(";"):
                    ck[j.split('=')[0].strip()]=unquote(j.split('=')[1],"utf-8")
                #print(ck)
            hl[i.split(":")[0]] = i.replace(i.split(":")[0]+": ","")
        return (hl,ck)
    
    def get_params(raw_data) -> dict:
        par=dict()
        url=unquote(raw_data[0].split(" ")[1])
        url = re.findall("\?.*",url)
        if len(url) != 0:
            for i in url[0][1:].split("&"):
                if str(i.split("=")[0].strip()) not in par.keys():
                    par[str(i.split("=")[0]).strip()]=[]
                par[str(i.split("=")[0]).strip()].append(i.split("=")[1])
        return par
    
    def get_url(raw_data,hl) -> str:
        try:
            url=unquote(raw_data[0].split(" ")[1])
            url ="http://"+hl['Host']+url
            return url
        except:
            raise AnalysisError("url err")
    
    def get_body(raw_data,hl):
        global method
        global content_type
        #print(content_type)
        if method == "get":
            return b""
        if method == "post":
            if not (raw_data[-1] and raw_data[-2] == "" and raw_data[-3] != ""):
                raise AnalysisError("lose the white line between headers and post body")
            data=unquote(raw_data[-1],"UTF-8")[:-1]
            if content_type== "multipart/form-data":
                return "\r\n".join(raw_data[2+len(hl):])
            elif content_type == "application/json":
                try:
                    json.loads(data)
                    return data.encode("UTF-8")
                except:
                    raise AnalysisError("json format err")
            return data.encode("UTF-8")
            
                
    def get_files(raw_data,hl):
        global method
        global content_type
        if method == "post":
            if not (raw_data[-1] and raw_data[-2] == "" and raw_data[-3] != ""):
                raise AnalysisError("lose the white line between headers and post body")
            data=unquote(raw_data[-1],"UTF-8")[:-1]
            if content_type == "application/x-www-form-urlencoded":
                return data.encode("UTF-8")
            elif content_type == "application/json":
                try:
                    json.loads(data)
                    return data.encode("UTF-8")
                except:
                    raise AnalysisError("json format err")
            elif content_type == "multipart/form-data":
                boundary = re.findall("boundary=(.+)",hl['Content-Type'])[0]
                if " " in boundary:
                    boundary=boundary[1:-1]
                if len(boundary) > 70:
                    raise AnalysisError("lenth err")
                boundary_indexs = [index for (index, item) in enumerate(raw_data) if item == "--"+boundary]
                if raw_data[-1] != "--"+boundary+"--":
                    raise AnalysisError("end err")
                boundary_indexs.append(len(raw_data))
                #print(boundary_indexs)
                file_array=[]
                for i in range(len(boundary_indexs)-1):
                    index = boundary_indexs[i]+1
                    cnt = 0
                    for k in range(index,boundary_indexs[i+1]):
                        if raw_data[k] == "":
                            cnt+=1
                    if cnt != 2:
                        raise AnalysisError("body err")
                    content_type=False
                    if len(re.findall("Content-Type: (.+)",raw_data[index+1])) != 0:
                        content_type=re.findall("Content-Type: (.+)",raw_data[index+1])[0]
                    nfile=File(name=re.findall("name=(.*?);",raw_data[index])[0][1:-1],
                            filename=re.findall("filename=(.*)",raw_data[index])[0][1:-1],
                            content_type=content_type,
                            data=("".join(raw_data[index+1:boundary_indexs[i+1]-1])).encode("UTF-8"))
                    file_array.append(nfile)
                    #print(vars(nfile))
                #print(file_array)
                return file_array

    def check_content_length(update_content_length,raw_data,hl):
        global method
        global content_type
        if update_content_length == True and method == "post" :
            hl['Content-Length'] = str(len(get_body(raw_data,hl)))
            
    data = pre_raw_data(raw_data)
    ans = PreparedRequest()
    hl = get_headers_cookie(data.copy())[0]
    #print(hl,type(hl),hl.keys(),hl.get('Content-Type'))
    content_type=str(hl.get("Content-Type")).split(";")[0]
    #print(content_type)
    check_content_length(update_content_length,data.copy(),hl)
    if content_type == "multipart/form-data" :
        ans.prepare(method=data.copy()[0].split(' ')[0],
                                    url=get_url(data.copy(),get_headers_cookie(data.copy())[0]),
                                    http_version=data.copy()[0].split(' ')[2],
                                    headers=hl,
                                    cookies=get_headers_cookie(data.copy())[1],
                                    params=get_params(data.copy()),
                                    body=get_body(data.copy(),hl),
                                    files=get_files(data.copy(),hl)
                                    )
    else:
        print(123);
        ans.prepare(method=data.copy()[0].split(' ')[0],
                                    url=get_url(data.copy(),get_headers_cookie(data.copy())[0]),
                                    http_version=data.copy()[0].split(' ')[2],
                                    headers=hl,
                                    cookies=get_headers_cookie(data.copy())[1],
                                    params=get_params(data.copy()),
                                    body=get_body(data.copy(),hl)
                                    )        
    return ans


def analysis_request1(raw_data, update_content_length=True):
    # 解释成功则返回一个PreparedRequest实例，记得调用prepare方法来设置其属性
    # 解析失败则 raise AnalysisError()
    ...
    ans = PreparedRequest()
    #print("111")
    if isinstance(raw_data,bytes):
        raw_data=raw_data.decode("UTF-8")
    ansl = raw_data.split('\r\n')
    #print("111")
    try:
        if  not raw_data.endswith('\r\n\r\n') or raw_data == "" or len(ansl[0].split(" ")) != 3:
            raise AnalysisError("1")
    except:
        raise AnalysisError("1")
    ansll = ansl.copy()
    del ansll[0]
    hl=dict()
    ck=dict()
    #print(1)
    for i in ansll:
        if i == "":
            break
        #print(i)
        if i.split(":")[0]=="Cookie":
            for j in i.replace("Cookie: ","").split(";"):
                ck[j.split('=')[0].strip()]=unquote(j.split('=')[1],"utf-8")
            #print(ck)
        hl[i.split(":")[0]] = i.replace(i.split(":")[0]+": ","")
    #print(hl,3)
    par=dict()
    #print(ansl,ansl[0],ansl[0].split(" "))
    url1=""
    url=unquote(ansl[0].split(" ")[1])
    url1 = url
    #print(url,1)
    url = re.findall("\?.*",url)
    if len(url) != 0:
        for i in url[0][1:].split("&"):
            if str(i.split("=")[0].strip()) not in par.keys():
                par[str(i.split("=")[0]).strip()]=[]
            par[str(i.split("=")[0]).strip()].append(i.split("=")[1])
    url1 ="http://"+hl['Host']+url1
    #print(hl,4)
    ans.prepare(params=par,headers=hl,cookies=ck,method=ansl[0].split(' ')[0],
                url=url1,
                http_version=ansl[0].split(' ')[2],
                body=b"")
    ans.url=url1
    ans.headers['Host']=ans.headers['Host'][:-3]
    return ans
