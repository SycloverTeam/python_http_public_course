import socket
from urllib.parse import ParseResult, urlparse

def httpRequest(host):
    parseResult = urlparse(host)
    url = parseResult.netloc
    path = parseResult.path
    if path == "":
        path = "/"
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM) #创建套接字
    s.connect((url,80))                        # 连接WEB服务器
    data = '''GET %s HTTP/1.1
Host: %s
Connection: close
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36
Accept-Language: zh-CN,zh;q=0.8

    ''' %(path,url)
    s.send(data.encode())                              # 发送报文（注意格式）

    buf=s.recv(1024)                                   # 接受响应信息
    while len(buf):                                    # 判断长度，为0则接收完
        print(buf.decode())                            # 输出响应信息
        buf = s.recv(1024)
