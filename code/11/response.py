from request import PreparedRequest


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
