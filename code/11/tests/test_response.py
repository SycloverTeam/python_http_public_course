import _path
import unittest
import response
import gzip
import zlib


class TestAnalysis(unittest.TestCase):
    def test_response(self):
        raw_data = b"""HTTP/1.1 200 OK\r
Host: 127.0.0.1\r
Connection: close\r
Content-Type: text/html; charset=UTF-8\r
Content-Length: 6\r
Set-Cookie: a=b;c=d\r
\r
hello!"""
        res: response.Response = response.analysis_response(raw_data)
        self.assertIsInstance(res, response.Response)
        self.assertEqual(res.http_version, "HTTP/1.1")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.ok, True)
        self.assertEqual(res.reason, "OK")
        self.assertDictEqual(res.headers, {"Host": "127.0.0.1", "Connection": "close",
                             "Content-Type": "text/html; charset=UTF-8", "Content-Length": "6", "Set-Cookie": "a=b;c=d"})
        self.assertDictEqual(res.cookies,  {"a": "b", "c": "d"})
        self.assertEqual(res.body, b"hello!")

    def test_response_with_cookie(self):
        raw_data = b"""HTTP/1.1 200 OK\r
Host: 127.0.0.1\r
Connection: close\r
Content-Type: text/html; charset=UTF-8\r
Content-Length: 6\r
Set-Cookie: a=b;c=d; httponly\r
\r
hello!"""
        res: response.Response = response.analysis_response(raw_data)
        self.assertIsInstance(res, response.Response)
        self.assertEqual(res.http_version, "HTTP/1.1")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.ok, True)
        self.assertEqual(res.reason, "OK")
        self.assertDictEqual(res.headers, {"Host": "127.0.0.1", "Connection": "close",
                             "Content-Type": "text/html; charset=UTF-8", "Content-Length": "6", "Set-Cookie": "a=b;c=d; httponly"})
        self.assertDictEqual(res.cookies,  {"a": "b", "c": "d"})
        self.assertEqual(res.body, b"hello!")

    def test_response_with_gzip(self):
        raw_data = b"""HTTP/1.1 200 OK\r
Host: 127.0.0.1\r
Connection: close\r
Content-Type: text/html; charset=UTF-8\r
Content-Length: 31\r
Content-Encoding: gzip\r
\r
""" + gzip.compress(b"hello world")
        res: response.Response = response.analysis_response(raw_data)
        self.assertIsInstance(res, response.Response)
        self.assertEqual(res.http_version, "HTTP/1.1")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.ok, True)
        self.assertEqual(res.reason, "OK")
        self.assertDictEqual(res.headers, {"Host": "127.0.0.1", "Connection": "close",
                             "Content-Type": "text/html; charset=UTF-8", "Content-Length": "31", "Content-Encoding": "gzip"})
        self.assertDictEqual(res.cookies,  dict())
        self.assertEqual(res.body, b"hello world")

    def test_response_with_zlib(self):
        raw_data = b"""HTTP/1.1 200 OK\r
Host: 127.0.0.1\r
Connection: close\r
Content-Type: text/html; charset=UTF-8\r
Content-Length: 19\r
Content-Encoding: deflate\r
\r
""" + zlib.compress(b"hello world")
        res: response.Response = response.analysis_response(raw_data)
        self.assertIsInstance(res, response.Response)
        self.assertEqual(res.http_version, "HTTP/1.1")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.ok, True)
        self.assertEqual(res.reason, "OK")
        self.assertDictEqual(res.headers, {"Host": "127.0.0.1", "Connection": "close",
                             "Content-Type": "text/html; charset=UTF-8", "Content-Length": "19", "Content-Encoding": "deflate"})
        self.assertDictEqual(res.cookies,  dict())
        self.assertEqual(res.body, b"hello world")

    def test_response_with_zlib_gzip(self):
        raw_data = b"""HTTP/1.1 200 OK\r
Host: 127.0.0.1\r
Connection: close\r
Content-Type: text/html; charset=UTF-8\r
Content-Length: 40\r
Content-Encoding: deflate, gzip\r
\r
""" + gzip.compress(zlib.compress(b"hello world"))
        res: response.Response = response.analysis_response(raw_data)
        self.assertIsInstance(res, response.Response)
        self.assertEqual(res.http_version, "HTTP/1.1")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.ok, True)
        self.assertEqual(res.reason, "OK")
        self.assertDictEqual(res.headers, {"Host": "127.0.0.1", "Connection": "close",
                             "Content-Type": "text/html; charset=UTF-8", "Content-Length": "40", "Content-Encoding": "deflate, gzip"})
        self.assertDictEqual(res.cookies,  dict())
        self.assertEqual(res.body, b"hello world")

    def test_response_with_302(self):
        raw_data = """HTTP/1.1 301 Moved Permanently\r
Host: 127.0.0.1\r
Connection: close\r
Content-Type: text/html; charset=UTF-8\r
Location: http://www.baidu.com\r
\r
"""
        res: response.Response = response.analysis_response(raw_data)
        self.assertIsInstance(res, response.Response)
        self.assertEqual(res.http_version, "HTTP/1.1")
        self.assertEqual(res.status_code, 301)
        self.assertEqual(res.ok, False)
        self.assertEqual(res.reason, "Moved Permanently")
        self.assertDictEqual(res.headers, {"Host": "127.0.0.1", "Connection": "close",
                             "Content-Type": "text/html; charset=UTF-8", "Location": "http://www.baidu.com"})
        self.assertDictEqual(res.cookies,  dict())
        self.assertEqual(res.body, b"")

    def test_response_error1(self):
        raw_data = """200 OK\r
Host: 127.0.0.1\r
Connection: close\r
Content-Type: text/html; charset=UTF-8\r
Content-Length: 6\r
Set-Cookie: a=b;c=d; httponly\r
\r
hello!"""
        with self.assertRaises(response.InvalidResponseError):
            response.analysis_response(raw_data)

    def test_response_error2(self):
        raw_data = """HTTP/1.1 200 OK\r
Host: 127.0.0.1\r
Connection: close\r
Content-Type: text/html; charset=UTF-8\r
Content-Length: 6\r
Set-Cookie: a=b;c=d; httponly\r
hello!"""
        with self.assertRaises(response.InvalidResponseError):
            response.analysis_response(raw_data)


if __name__ == "__main__":
    unittest.main()
