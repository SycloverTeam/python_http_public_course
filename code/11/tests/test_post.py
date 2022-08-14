import _path
import unittest
import request


class TestAnalysis(unittest.TestCase):
    def test_post(self):
        raw_data = b"""
POST /post HTTP/1.1\r
UserAgent: syclover\r
Content-Length: 0\r
Content-Type: application/x-www-form-urlencoded; charset=utf-8\r
Host: httpbin.org\r
\r

""".lstrip()
        req: request.PreparedRequest = request.analysis_request(raw_data)
        self.assertIsInstance(req, request.PreparedRequest)
        self.assertEqual(req.method, "POST")
        self.assertIn(
            req.url, {"http://httpbin.org:80/post", "http://httpbin.org/post"})
        self.assertEqual(req.http_version, "HTTP/1.1")
        self.assertDictEqual(req.params, dict())
        self.assertDictEqual(
            req.headers, {"UserAgent": "syclover", "Host": "httpbin.org", "Content-Length": "0", "Content-Type": "application/x-www-form-urlencoded; charset=utf-8"})
        self.assertDictEqual(req.cookies, dict())
        self.assertEqual(req.body, b"")

    def test_post_with_data(self):
        raw_data = b"""
POST /post HTTP/1.1\r
UserAgent: syclover\r
Content-Length: 18\r
Content-Type: application/x-www-form-urlencoded; charset=utf-8\r
Host: httpbin.org\r
\r
a=1&b=2&c=%73%79%63%6c%6f%76%65%72
""".lstrip()
        req: request.PreparedRequest = request.analysis_request(raw_data)
        self.assertIsInstance(req, request.PreparedRequest)
        self.assertEqual(req.method, "POST")
        self.assertIn(
            req.url, {"http://httpbin.org:80/post", "http://httpbin.org/post"})
        self.assertEqual(req.http_version, "HTTP/1.1")
        self.assertDictEqual(req.params, dict())
        self.assertDictEqual(
            req.headers, {"UserAgent": "syclover", "Host": "httpbin.org", "Content-Length": "18", "Content-Type": "application/x-www-form-urlencoded; charset=utf-8"})
        self.assertDictEqual(req.cookies, dict())
        self.assertEqual(req.body, b"a=1&b=2&c=syclover")

    def test_post_with_incomplete_data(self):
        raw_data = b"""
POST /post HTTP/1.1\r
UserAgent: syclover\r
Content-Length: 13\r
Content-Type: application/x-www-form-urlencoded; charset=utf-8\r
Host: httpbin.org\r
\r
a=1&b=2&c=%73%79%63%6c%6f%76%65%72
""".lstrip()
        req: request.PreparedRequest = request.analysis_request(raw_data)
        self.assertIsInstance(req, request.PreparedRequest)
        self.assertEqual(req.method, "POST")
        self.assertIn(
            req.url, {"http://httpbin.org:80/post", "http://httpbin.org/post"})
        self.assertEqual(req.http_version, "HTTP/1.1")
        self.assertDictEqual(req.params, dict())
        self.assertDictEqual(
            req.headers, {"UserAgent": "syclover", "Host": "httpbin.org", "Content-Length": "18", "Content-Type": "application/x-www-form-urlencoded; charset=utf-8"})
        self.assertDictEqual(req.cookies, dict())
        self.assertEqual(req.body, b"a=1&b=2&c=syclover")

    def test_post_with_incomplete_data_without_update_content_length(self):
        raw_data = b"""
POST /post HTTP/1.1\r
UserAgent: syclover\r
Content-Length: 13\r
Content-Type: application/x-www-form-urlencoded; charset=utf-8\r
Host: httpbin.org\r
\r
a=1&b=2&c=%73%79%63%6c%6f%76%65%72
""".lstrip()
        req: request.PreparedRequest = request.analysis_request(raw_data, False)
        self.assertIsInstance(req, request.PreparedRequest)
        self.assertEqual(req.method, "POST")
        self.assertIn(
            req.url, {"http://httpbin.org:80/post", "http://httpbin.org/post"})
        self.assertEqual(req.http_version, "HTTP/1.1")
        self.assertDictEqual(req.params, dict())
        self.assertDictEqual(
            req.headers, {"UserAgent": "syclover", "Host": "httpbin.org", "Content-Length": "13", "Content-Type": "application/x-www-form-urlencoded; charset=utf-8"})
        self.assertDictEqual(req.cookies, dict())
        self.assertEqual(req.body, b"a=1&b=2&c=syclover")

    def test_post_with_data_params(self):
        raw_data = b"""
POST /post?d=syc&e=%73%79%63%6c%6f%76%65%72 HTTP/1.1\r
UserAgent: syclover\r
Content-Length: 18\r
Content-Type: application/x-www-form-urlencoded; charset=utf-8\r
Host: httpbin.org\r
\r
a=1&b=2&c=%73%79%63%6c%6f%76%65%72
""".lstrip()
        req: request.PreparedRequest = request.analysis_request(raw_data)
        self.assertIsInstance(req, request.PreparedRequest)
        self.assertEqual(req.method, "POST")
        self.assertIn(
            req.url, {"http://httpbin.org:80/post?d=syc&e=syclover", "http://httpbin.org/post?d=syc&e=syclover"})
        self.assertEqual(req.http_version, "HTTP/1.1")
        self.assertDictEqual(req.params, {"d": ["syc"], "e": ["syclover"]})
        self.assertDictEqual(
            req.headers, {"UserAgent": "syclover", "Host": "httpbin.org", "Content-Length": "18", "Content-Type": "application/x-www-form-urlencoded; charset=utf-8"})
        self.assertDictEqual(req.cookies, dict())
        self.assertEqual(req.body, b"a=1&b=2&c=syclover")

    def test_post_with_data_list(self):
        raw_data = b"""
POST /post HTTP/1.1\r
UserAgent: syclover\r
Content-Length: 16\r
Content-Type: application/x-www-form-urlencoded; charset=utf-8\r
Host: httpbin.org\r
\r
c=syc&c=%73%79%63%6c%6f%76%65%72
""".lstrip()
        req: request.PreparedRequest = request.analysis_request(raw_data)
        self.assertIsInstance(req, request.PreparedRequest)
        self.assertEqual(req.method, "POST")
        self.assertIn(
            req.url, {"http://httpbin.org:80/post", "http://httpbin.org/post"})
        self.assertEqual(req.http_version, "HTTP/1.1")
        self.assertDictEqual(req.params, dict())
        self.assertDictEqual(
            req.headers, {"UserAgent": "syclover", "Host": "httpbin.org", "Content-Length": "16", "Content-Type": "application/x-www-form-urlencoded; charset=utf-8"})
        self.assertDictEqual(req.cookies, dict())
        self.assertEqual(req.body, b"c=syc&c=syclover")

    def test_post_with_data_cookies(self):
        raw_data = b"""
POST /post?d=syc&e=%73%79%63%6c%6f%76%65%72 HTTP/1.1\r
UserAgent: syclover\r
Content-Length: 18\r
Content-Type: application/x-www-form-urlencoded; charset=utf-8\r
Cookie: test=true; id=%73%79%63%6c%6f%76%65%72\r
Host: httpbin.org\r
\r
a=1&b=2&c=%73%79%63%6c%6f%76%65%72
""".lstrip()
        req: request.PreparedRequest = request.analysis_request(raw_data)
        self.assertIsInstance(req, request.PreparedRequest)
        self.assertEqual(req.method, "POST")
        self.assertIn(
            req.url, {"http://httpbin.org:80/post?d=syc&e=syclover", "http://httpbin.org/post?d=syc&e=syclover"})
        self.assertEqual(req.http_version, "HTTP/1.1")
        self.assertDictEqual(req.params, {"d": ["syc"], "e": ["syclover"]})
        self.assertDictEqual(
            req.headers, {"UserAgent": "syclover", "Host": "httpbin.org", "Content-Length": "18", "Content-Type": "application/x-www-form-urlencoded; charset=utf-8", "Cookie": r"test=true; id=%73%79%63%6c%6f%76%65%72"})
        self.assertDictEqual(req.cookies, {"test": "true", "id": "syclover"})
        self.assertEqual(req.body, b"a=1&b=2&c=syclover")

    def test_post_with_error1(self):  # 请求体与请求头之间没分行
        raw_data = b"""
POST /post HTTP/1.1\r
UserAgent: syclover\r
Content-Length: 18\r
Content-Type: application/x-www-form-urlencoded; charset=utf-8\r
Host: httpbin.org\r
a=1&b=2&c=%73%79%63%6c%6f%76%65%72
""".lstrip()
        with self.assertRaises(request.AnalysisError):
            request.analysis_request(raw_data)

    def test_post_with_error2(self):  # 第一行有误
        raw_data = b"""
POST /post?a=1 &b=2 HTTP/1.1\r
UserAgent: syclover\r
Content-Length: 18\r
Content-Type: application/x-www-form-urlencoded; charset=utf-8\r
Host: httpbin.org\r
\r
a=1&b=2&c=%73%79%63%6c%6f%76%65%72
""".lstrip()
        with self.assertRaises(request.AnalysisError):
            request.analysis_request(raw_data)

    def test_get_with_error3(self):  # 空请求
        raw_data = r"""
""".lstrip()
        with self.assertRaises(request.AnalysisError):
            request.analysis_request(raw_data)

    def test_post_with_error4(self):  # Content-Length有误
        raw_data = b"""
POST /post?a=1 &b=2 HTTP/1.1\r
UserAgent: syclover\r
Content-Length: aaaa\r
Content-Type: application/x-www-form-urlencoded; charset=utf-8\r
Host: httpbin.org\r
\r
a=1&b=2&c=%73%79%63%6c%6f%76%65%72
""".lstrip()
        with self.assertRaises(request.AnalysisError):
            request.analysis_request(raw_data)


if __name__ == "__main__":
    unittest.main()
