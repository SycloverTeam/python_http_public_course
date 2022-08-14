import socket
import ssl
import json
from request import analysis_request, PreparedRequest, File
from response import analysis_response, Response


def request(method, url, **kwargs) -> Response:
    req = PreparedRequest()
    method = method.upper()
    params = kwargs.get("params", dict())
    headers = kwargs.get("headers", dict())
    cookies = kwargs.get("cookies", dict())
    body = kwargs.get("data", b"")
    json_data = kwargs.get("json", dict())
    if json and not body:
        body = json.dumps(json_data).encode()
    for k, v in headers.items():
        if k.upper() == "CONNECTION":
            headers[k] = "close"
            break
    else:
        headers["Connection"] = "close"

    filedicts: dict = kwargs.get("files", {})
    files = None
    if filedicts:
        files = []

    for name, v in filedicts.items():
        if isinstance(v, str):
            files.append(File(name, "", "", v.encode()))
        elif isinstance(v, bytes):
            files.append(File(name, "", "", v))
        elif isinstance(v, (tuple, list)):
            filelist = []
            if isinstance(v[0], (tuple, list)):
                filelist.extend(v)
            else:
                filelist.append(v)

            for filedata in filelist:
                filename = filedata[0]
                data = filedata[1]
                if isinstance(data, str):
                    data = data.encode()
                elif hasattr(data, "read"):
                    data = data.read()

                content_type = ""
                if len(filedata) > 2:
                    content_type = filedata[2]

                files.append(File(name, filename, content_type, data))

    req.prepare(method, url, "HTTP/1.1", headers,
                cookies, params, body, files, update=True)
    # print(req.to_raw().decode())
    raw_response = _send(req)
    resp = analysis_response(raw_response)
    resp.setRequest(req)
    # print(raw_response.decode())
    return resp


def request_raw(raw_request: bytes) -> Response:
    raw_request = raw_request.replace(b"\n", b"\r\n")
    req = analysis_request(raw_request)
    data_list = raw_request.split(b"\r\n")
    splitLines = 0
    for n, line in enumerate(data_list):
        if line == b"":
            splitLines = n
            break

    for n, line in enumerate(data_list[1:splitLines]):
        if line.upper().startswith(b"CONNECTION"):
            break
    else:
        data_list.insert(1, b"Connection: close")

    raw_request = b"\r\n".join(data_list)
    # print(raw_request.decode())
    raw_response = _send(req, raw_request)
    resp = analysis_response(raw_response)
    resp.setRequest(req)
    # print(raw_response.decode())
    return resp


def get(url, params=dict(), **kwargs) -> Response:
    return request('get', url, params=params, **kwargs)


def post(url, data=b"", json=None, **kwargs) -> Response:
    return request('post', url, data=data, json=json, **kwargs)


def _send(req, raw_data=b"") -> bytes:
    ...


# resp = request_raw(b"""GET /get?a=B&c=D HTTP/1.1
# CustomHeader: AAA
# Host: httpbin.org:80

# """)

# request("GET", "http://httpbin.org/get", params={"a": "B", "c": "D"}, headers={"CustomHeader": "AAA"}, cookies={"CustomCookie1": "BBBB", "CustomCookie2": "CCCC"})

# request("POST", "http://httpbin.org/post", data={"a": "B", "c": "D"}, headers={"CustomHeader": "AAA"}, cookies={"CustomCookie1": "BBBB", "CustomCookie2": "CCCC"})

# request("POST", "http://httpbin.org/post", data=b"qweqweqwe", headers={"CustomHeader": "AAA"}, cookies={"CustomCookie1": "BBBB", "CustomCookie2": "CCCC"}, files={"file1": b"asdasd", "file2": ("a.xls", b"x,x,x,x", "application/vnd.ms-excel"), "file3": (("b.xls", b"b,b,b,b"), ("c.xls", b"c,c,c,c"))})
