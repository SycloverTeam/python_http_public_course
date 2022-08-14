import _path
import unittest
import request
import myrequest
from unittest import mock


_response_data = b"""HTTP/1.1 200 OK
Date: Sat, 13 Aug 2022 04:06:59 GMT
Content-Type: application/json
Content-Length: 265
Connection: close
Server: gunicorn/19.9.0
Access-Control-Allow-Origin: *
Access-Control-Allow-Credentials: true

{
  "args": {
    "a": "B",
    "c": "D"
  },
  "headers": {
    "Customheader": "AAA",
    "Host": "httpbin.org",
    "X-Amzn-Trace-Id": "Root=1-62f72363-13ba203d2b420f877fc26954"
  },
  "origin": "183.27.46.183",
  "url": "http://httpbin.org/get?a=B&c=D"
}"""


class TestSend(unittest.TestCase):
    def test_send(self):
        with mock.patch('socket.socket') as mock_socket:
            mock_socket.return_value.recv.side_effect = [_response_data, b""]

            raw_request = """GET /get?a=B&c=D HTTP/1.1
Connection: close
CustomHeader: AAA
Host: httpbin.org:80

""".replace("\n", "\r\n")
            req = request.analysis_request(raw_request)
            raw_response = myrequest._send(req, raw_request)
            self.assertEqual(raw_response, _response_data)
            mock_socket.return_value.connect.assert_called_with(
                ("httpbin.org", 80))


if __name__ == "__main__":
    unittest.main()
