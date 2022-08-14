import _path
import unittest
import request


class TestAnalysis(unittest.TestCase):
    def test_get(self):
        raw_data = b"""
GET /get HTTP/1.1\r
UserAgent: syclover\r
Host: httpbin.org\r
\r
""".lstrip()
        req: request.PreparedRequest = request.analysis_request(raw_data)
        self.assertIsInstance(req, request.PreparedRequest)
        self.assertEqual(req.method, "GET")
        self.assertIn(
            req.url, {"http://httpbin.org:80/get", "http://httpbin.org/get"})
        self.assertEqual(req.http_version, "HTTP/1.1")
        self.assertDictEqual(req.params, dict())
        self.assertDictEqual(
            req.headers, {"UserAgent": "syclover", "Host": "httpbin.org"})
        self.assertDictEqual(req.cookies, dict())

    def test_get_with_params(self):
        raw_data = b"""
GET /get?a=1&b=2&c=%73%79%63%6c%6f%76%65%72 HTTP/1.1\r
UserAgent: syclover\r
Host: httpbin.org\r
\r
""".lstrip()
        req: request.PreparedRequest = request.analysis_request(raw_data)
        self.assertIsInstance(req, request.PreparedRequest)
        self.assertEqual(req.method, "GET")
        self.assertIn(
            req.url, {"http://httpbin.org:80/get?a=1&b=2&c=syclover", "http://httpbin.org/get?a=1&b=2&c=syclover"})
        self.assertEqual(req.http_version, "HTTP/1.1")
        self.assertDictEqual(
            req.params, {"a": ["1"], "b": ["2"], "c": ["syclover"]})
        self.assertDictEqual(
            req.headers, {"UserAgent": "syclover", "Host": "httpbin.org"})
        self.assertDictEqual(req.cookies, dict())

    def test_get_with_params_list(self):
        raw_data = b"""
GET /get?c=syc&c=%73%79%63%6c%6f%76%65%72 HTTP/1.1\r
UserAgent: syclover\r
Host: httpbin.org\r
\r
""".lstrip()
        req: request.PreparedRequest = request.analysis_request(raw_data)
        self.assertIsInstance(req, request.PreparedRequest)
        self.assertEqual(req.method, "GET")
        self.assertIn(
            req.url, {"http://httpbin.org:80/get?c=syc&c=syclover", "http://httpbin.org/get?c=syc&c=syclover"})
        self.assertEqual(req.http_version, "HTTP/1.1")
        self.assertDictEqual(req.params, {"c": ["syc", "syclover"]})
        self.assertDictEqual(
            req.headers, {"UserAgent": "syclover", "Host": "httpbin.org"})
        self.assertDictEqual(req.cookies, dict())

    def test_get_with_cookies(self):
        raw_data = b"""
GET /get HTTP/1.1\r
UserAgent: syclover\r
Cookie: test=true; id=%73%79%63%6c%6f%76%65%72\r
Host: httpbin.org\r
\r
""".lstrip()
        req: request.PreparedRequest = request.analysis_request(raw_data)
        self.assertIsInstance(req, request.PreparedRequest)
        self.assertEqual(req.method, "GET")
        self.assertIn(
            req.url, {"http://httpbin.org:80/get", "http://httpbin.org/get"})
        self.assertEqual(req.http_version, "HTTP/1.1")
        self.assertDictEqual(req.params, dict())
        self.assertDictEqual(
            req.headers, {"UserAgent": "syclover", "Cookie": r"test=true; id=%73%79%63%6c%6f%76%65%72", "Host": "httpbin.org"})
        self.assertDictEqual(req.cookies, {"test": "true", "id": "syclover"})

    def test_get_with_error1(self):  # 第一行有误
        raw_data = b"""
GET /get?a=1 &b=2 HTTP/1.1\r
UserAgent: syclover\r
Host: httpbin.org\r
\r
""".lstrip()
        with self.assertRaises(request.AnalysisError):
            request.analysis_request(raw_data)

    def test_get_with_error2(self):  # 没有以\r\n\r\n结尾
        raw_data = """
GET /get HTTP/1.1\r
UserAgent: syclover\r
Host: httpbin.org\r
""".lstrip()
        with self.assertRaises(request.AnalysisError):
            request.analysis_request(raw_data)

    def test_get_with_error3(self):  # 空请求
        raw_data = r"""
""".lstrip()
        with self.assertRaises(request.AnalysisError):
            request.analysis_request(raw_data)


if __name__ == "__main__":
    unittest.main()
