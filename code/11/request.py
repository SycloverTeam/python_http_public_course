from urllib.parse import urlparse
from string import ascii_lowercase, digits
from random import choice


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
